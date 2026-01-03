#!/usr/bin/env python3
"""
Verify all required services are reachable.

Exit codes:
  0 - All services healthy
  1 - One or more services unhealthy
"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import psycopg2
import redis
import httpx


def check_postgres(host: str, port: int, user: str, password: str, db: str) -> tuple[bool, str]:
    """Check PostgreSQL connection."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=db,
            connect_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True, "PostgreSQL is healthy"
    except Exception as e:
        return False, f"PostgreSQL error: {str(e)}"


def check_qdrant(host: str, port: int) -> tuple[bool, str]:
    """Check Qdrant connection."""
    try:
        response = httpx.get(
            f"http://{host}:{port}/readiness",
            timeout=5.0,
        )
        if response.status_code == 200:
            return True, "Qdrant is healthy"
        return False, f"Qdrant returned status {response.status_code}"
    except Exception as e:
        return False, f"Qdrant error: {str(e)}"


def check_redis(url: str) -> tuple[bool, str]:
    """Check Redis connection."""
    try:
        r = redis.from_url(url, socket_connect_timeout=5)
        r.ping()
        r.close()
        return True, "Redis is healthy"
    except Exception as e:
        return False, f"Redis error: {str(e)}"


def main():
    """Run all service checks."""
    print("=" * 60)
    print("SERVICE VERIFICATION")
    print("=" * 60)

    # Load configuration from environment
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = int(os.getenv("POSTGRES_PORT", "5432"))
    pg_user = os.getenv("POSTGRES_USER", "tadabbur")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "tadabbur_dev")
    pg_db = os.getenv("POSTGRES_DB", "tadabbur")

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    all_passed = True
    results = []

    # Check PostgreSQL
    print("\n[1/3] Checking PostgreSQL...")
    passed, message = check_postgres(pg_host, pg_port, pg_user, pg_pass, pg_db)
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {message}")
    results.append(("PostgreSQL", passed, message))
    if not passed:
        all_passed = False

    # Check Qdrant
    print("\n[2/3] Checking Qdrant...")
    passed, message = check_qdrant(qdrant_host, qdrant_port)
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {message}")
    results.append(("Qdrant", passed, message))
    if not passed:
        all_passed = False

    # Check Redis
    print("\n[3/3] Checking Redis...")
    passed, message = check_redis(redis_url)
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {message}")
    results.append(("Redis", passed, message))
    if not passed:
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for service, passed, _ in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {service}: {status}")

    print("\n" + "=" * 60)

    if all_passed:
        print("OVERALL: PASS - All services healthy")
        print("=" * 60)
        sys.exit(0)
    else:
        print("OVERALL: FAIL - One or more services unhealthy")
        print("=" * 60)
        print("\nREMEDIATION:")
        print("  1. Ensure Docker Compose services are running: docker-compose up -d")
        print("  2. Check container logs: docker-compose logs <service>")
        print("  3. Verify network connectivity and ports")
        sys.exit(1)


if __name__ == "__main__":
    main()
