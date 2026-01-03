#!/usr/bin/env python3
"""
Index tafseer chunks into Qdrant vector database.

This script:
1. Loads tafseer chunks from PostgreSQL
2. Generates embeddings using sentence-transformers
3. Indexes vectors into Qdrant with metadata
"""
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    print("WARNING: sentence-transformers not installed. Using placeholder vectors.")

from app.models.tafseer import TafseerChunk, TafseerSource
from app.core.config import settings


def get_db_url() -> str:
    return os.getenv("DATABASE_URL", "postgresql://tadabbur:tadabbur_dev@localhost:5432/tadabbur")


def get_qdrant_client() -> QdrantClient:
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    return QdrantClient(host=host, port=port)


def ensure_collection(client: QdrantClient, collection_name: str, dimension: int):
    """Create collection if it doesn't exist."""
    collections = [c.name for c in client.get_collections().collections]

    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )
        print(f"  Created collection: {collection_name}")
    else:
        print(f"  Collection exists: {collection_name}")


def get_embedder():
    """Get sentence transformer model."""
    if HAS_EMBEDDINGS:
        model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
        print(f"  Loading embedding model: {model_name}")
        return SentenceTransformer(model_name)
    return None


def generate_embedding(embedder, text: str, dimension: int = 1024) -> list:
    """Generate embedding for text."""
    if embedder:
        return embedder.encode(text).tolist()
    # Placeholder: return zero vector
    return [0.0] * dimension


def main():
    print("=" * 60)
    print("TAFSEER INDEXING")
    print("=" * 60)

    start_time = datetime.now()
    collection_name = os.getenv("QDRANT_COLLECTION", "tafseer_chunks")
    dimension = int(os.getenv("EMBEDDING_DIMENSION", "1024"))
    batch_size = 50

    try:
        print("\n[1/4] Connecting to services...")
        engine = create_engine(get_db_url())
        qdrant = get_qdrant_client()

        # Test Qdrant connection
        qdrant.get_collections()
        print("  Qdrant: Connected")

        print("\n[2/4] Setting up collection...")
        ensure_collection(qdrant, collection_name, dimension)

        print("\n[3/4] Loading embedding model...")
        embedder = get_embedder()

        print("\n[4/4] Indexing chunks...")

        with Session(engine) as session:
            # Get chunks with source info
            result = session.execute(
                select(TafseerChunk, TafseerSource)
                .join(TafseerSource, TafseerChunk.source_id == TafseerSource.id)
                .where(TafseerChunk.is_embedded == 0)
            )
            chunks = result.all()

            if not chunks:
                print("  No unindexed chunks found")
                print("\n  Checking total chunk count...")
                total = session.execute(select(TafseerChunk.id)).all()
                print(f"  Total chunks in database: {len(total)}")

                if len(total) == 0:
                    print("\n  No tafseer data loaded. Run seed_tafseer.py first.")
                else:
                    print("  All chunks already indexed.")
                sys.exit(0)

            print(f"  Found {len(chunks)} chunks to index")

            points = []
            indexed_ids = []

            for i, (chunk, source) in enumerate(chunks):
                # Get content for embedding
                content = chunk.content_en or chunk.content_ar or ""
                if not content:
                    continue

                # Generate embedding
                vector = generate_embedding(embedder, content, dimension)

                # Create point
                point = PointStruct(
                    id=chunk.id,
                    vector=vector,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "source_id": chunk.source_id,
                        "source_name": source.name_en,
                        "source_name_ar": source.name_ar,
                        "verse_reference": chunk.verse_reference,
                        "sura_no": chunk.sura_no,
                        "aya_start": chunk.aya_start,
                        "aya_end": chunk.aya_end,
                        "content_en": chunk.content_en[:500] if chunk.content_en else None,
                        "content_ar": chunk.content_ar[:500] if chunk.content_ar else None,
                        "scholarly_consensus": chunk.scholarly_consensus,
                    }
                )
                points.append(point)
                indexed_ids.append(chunk.id)

                # Batch upsert
                if len(points) >= batch_size:
                    qdrant.upsert(collection_name=collection_name, points=points)
                    print(f"  Indexed {i + 1}/{len(chunks)} chunks")
                    points = []

            # Final batch
            if points:
                qdrant.upsert(collection_name=collection_name, points=points)

            # Update is_embedded flag
            if indexed_ids:
                from sqlalchemy import update
                session.execute(
                    update(TafseerChunk)
                    .where(TafseerChunk.id.in_(indexed_ids))
                    .values(is_embedded=1, embedding_model=os.getenv("EMBEDDING_MODEL", "placeholder"))
                )
                session.commit()

        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 60)
        print(f"SUCCESS: Indexed {len(indexed_ids)} chunks in {duration:.2f}s")
        print("=" * 60)
        sys.exit(0)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
