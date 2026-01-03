# Tadabbur-AI

RAG-grounded Quranic knowledge platform with story connections.

## Overview

Tadabbur-AI is a scholarly Quranic knowledge platform that:
- Provides **grounded answers** with mandatory citations from authenticated tafseer sources
- Maps **Quranic stories** and their connections across different surahs
- Supports **bilingual interface** (Arabic/English) with RTL support
- Uses **RAG (Retrieval-Augmented Generation)** to avoid AI hallucinations

## Safety Rules

1. **NEVER** invent tafseer - LLM may ONLY summarize retrieved evidence
2. Every paragraph **MUST** include at least one citation referencing a retrieved `chunk_id`
3. Citations are **validated** - cited chunks must exist in retrieved set
4. For insufficient evidence: "This requires further scholarly consultation"
5. For fiqh/rulings: informational summary only, no fatwa language

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Make

### Setup

1. **Clone and configure:**
   ```bash
   cd tadabbur-ai
   cp .env.example .env
   # Edit .env and add ANTHROPIC_API_KEY
   ```

2. **Run the full pipeline:**
   ```bash
   make pipeline
   ```

   This will:
   - Start all Docker services
   - Run database migrations
   - Seed Quran verses
   - Seed stories
   - Verify all components

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
tadabbur-ai/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoints
│   │   ├── core/             # Configuration
│   │   ├── db/               # Database setup
│   │   ├── models/           # SQLAlchemy models
│   │   ├── rag/              # RAG pipeline
│   │   ├── services/         # Business logic
│   │   └── validators/       # Citation validators
│   ├── alembic/              # Database migrations
│   ├── scripts/
│   │   ├── datasets/         # Data download scripts
│   │   ├── verify/           # Verification scripts
│   │   ├── ingest/           # Data seeding scripts
│   │   └── index/            # Vector indexing scripts
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/       # React components
│       ├── pages/            # Page components
│       ├── i18n/             # Translations
│       ├── lib/              # API client
│       └── stores/           # State management
├── data/
│   ├── raw/                  # Raw downloaded data
│   ├── processed/            # Processed data
│   └── manifests/            # Dataset manifests
├── docker-compose.yml
├── Makefile
└── README.md
```

## Makefile Commands

```bash
# Docker
make up              # Start all services
make down            # Stop all services
make logs            # View logs

# Database
make migrate         # Run migrations
make seed            # Seed all data
make seed-quran      # Seed Quran verses only

# Verification
make verify          # Run all verifications
make verify-services # Check services health
make verify-db       # Check database seeding
make verify-rag      # Check RAG pipeline

# Development
make dev-backend     # Run backend in dev mode
make dev-frontend    # Run frontend in dev mode

# Full Pipeline
make pipeline        # Run complete pipeline
```

## API Endpoints

### Quran
- `GET /api/v1/quran/suras/{sura_no}` - Get verses for a sura
- `GET /api/v1/quran/verses/{sura}/{aya}` - Get specific verse
- `GET /api/v1/quran/tafseer/{sura}/{aya}` - Get tafseer for verse

### Stories
- `GET /api/v1/stories` - List all stories
- `GET /api/v1/stories/{id}` - Get story with segments
- `GET /api/v1/stories/{id}/graph` - Get story graph data

### RAG
- `POST /api/v1/rag/ask` - Ask a question
  ```json
  {
    "question": "What is the meaning of Ayat al-Kursi?",
    "language": "en",
    "include_scholarly_debate": true
  }
  ```

## Adding Data Sources

### Adding Tafseer Sources

1. Edit `data/manifests/tafseer_sources.json`
2. Add source with URL and license information
3. Run `make seed-tafseer`
4. Run `make index-tafseer`

### Adding Stories

1. Edit `data/manifests/stories.json`
2. Add story with segments and verse references
3. Run `make seed-stories`

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic v2
- **Database:** PostgreSQL
- **Vector DB:** Qdrant
- **Cache:** Redis
- **Frontend:** React, TypeScript, Tailwind CSS
- **Visualization:** Cytoscape.js

## Environment Variables

```env
# Required
DATABASE_URL=postgresql://tadabbur:tadabbur_dev@localhost:5432/tadabbur
ANTHROPIC_API_KEY=your_key_here

# Optional
QDRANT_HOST=localhost
QDRANT_PORT=6333
REDIS_URL=redis://localhost:6379/0
EMBEDDING_MODEL=intfloat/multilingual-e5-large
```

## License

This project respects all source licenses. Quran text is public domain.
Tafseer sources must be verified for license compliance before use.
