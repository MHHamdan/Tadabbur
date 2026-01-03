# Tadabbur-AI Makefile
# Automated pipeline for development and deployment

.PHONY: help up down logs migrate seed index verify test pipeline clean

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help
	@echo "Tadabbur-AI - Makefile Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# Docker Commands
# =============================================================================

up: ## Start all services
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Waiting for services to be healthy...$(NC)"
	@sleep 5
	@make verify-services

down: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	docker-compose down

logs: ## View logs for all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

restart: ## Restart all services
	@make down
	@make up

# =============================================================================
# Database Commands
# =============================================================================

migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)Migrations complete$(NC)"

migrate-down: ## Rollback last migration
	cd backend && alembic downgrade -1

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

# =============================================================================
# Data Seeding Commands
# =============================================================================

seed: seed-quran seed-stories ## Seed all data

seed-quran: ## Seed Quran verses
	@echo "$(GREEN)Seeding Quran verses...$(NC)"
	cd backend && python scripts/ingest/seed_quran.py

seed-stories: ## Seed stories data
	@echo "$(GREEN)Seeding stories...$(NC)"
	cd backend && python scripts/ingest/seed_stories.py

seed-tafseer: ## Seed tafseer data (requires source)
	@echo "$(GREEN)Seeding tafseer...$(NC)"
	@echo "$(YELLOW)Note: Tafseer sources require user-provided URLs$(NC)"
	@echo "Check data/manifests/tafseer_sources.json"

# =============================================================================
# Indexing Commands
# =============================================================================

index: index-tafseer ## Index all vectors

index-tafseer: ## Index tafseer into Qdrant
	@echo "$(GREEN)Indexing tafseer chunks...$(NC)"
	cd backend && python scripts/index/index_tafseer.py

# =============================================================================
# Verification Commands
# =============================================================================

verify: verify-services verify-downloads verify-db verify-qdrant verify-rag ## Run all verifications
	@echo "$(GREEN)All verifications complete$(NC)"

verify-services: ## Verify all services are running
	@echo "$(GREEN)Verifying services...$(NC)"
	cd backend && python scripts/verify/verify_services.py

verify-downloads: ## Verify dataset downloads
	@echo "$(GREEN)Verifying downloads...$(NC)"
	cd backend && python scripts/verify/verify_downloads.py

verify-db: ## Verify database is seeded
	@echo "$(GREEN)Verifying database...$(NC)"
	cd backend && python scripts/verify/verify_db_seed.py

verify-qdrant: ## Verify Qdrant index
	@echo "$(GREEN)Verifying Qdrant...$(NC)"
	cd backend && python scripts/verify/verify_qdrant_index.py

verify-rag: ## Verify RAG pipeline
	@echo "$(GREEN)Verifying RAG...$(NC)"
	cd backend && python scripts/verify/verify_rag_response.py

# =============================================================================
# Testing Commands
# =============================================================================

test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	cd backend && pytest tests/ -v

test-cov: ## Run tests with coverage
	cd backend && pytest tests/ -v --cov=app --cov-report=html

# =============================================================================
# Development Commands
# =============================================================================

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

install-backend: ## Install backend dependencies
	cd backend && pip install -e ".[dev]"

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

lint: ## Run linters
	cd backend && ruff check app/
	cd backend && black --check app/

format: ## Format code
	cd backend && black app/
	cd backend && ruff check --fix app/

# =============================================================================
# Full Pipeline Command
# =============================================================================

pipeline: ## Run the complete pipeline end-to-end
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)TADABBUR-AI FULL PIPELINE$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(GREEN)[Step 0/8] Starting services...$(NC)"
	@make up
	@echo ""
	@echo "$(GREEN)[Step 1/8] Verifying services...$(NC)"
	@make verify-services || (echo "$(RED)FAIL: Services not ready$(NC)" && exit 1)
	@echo ""
	@echo "$(GREEN)[Step 2/8] Verifying downloads...$(NC)"
	@make verify-downloads || echo "$(YELLOW)WARN: Some downloads need attention$(NC)"
	@echo ""
	@echo "$(GREEN)[Step 3/8] Running migrations...$(NC)"
	@make migrate
	@echo ""
	@echo "$(GREEN)[Step 4/8] Seeding Quran data...$(NC)"
	@make seed-quran
	@echo ""
	@echo "$(GREEN)[Step 5/8] Seeding stories...$(NC)"
	@make seed-stories
	@echo ""
	@echo "$(GREEN)[Step 6/8] Verifying database...$(NC)"
	@make verify-db || (echo "$(RED)FAIL: Database not seeded correctly$(NC)" && exit 1)
	@echo ""
	@echo "$(GREEN)[Step 7/8] Verifying Qdrant...$(NC)"
	@make verify-qdrant || echo "$(YELLOW)WARN: Qdrant needs indexing$(NC)"
	@echo ""
	@echo "$(GREEN)[Step 8/8] Verifying RAG pipeline...$(NC)"
	@make verify-rag || echo "$(YELLOW)WARN: RAG needs configuration$(NC)"
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)PIPELINE COMPLETE$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Set ANTHROPIC_API_KEY in .env for RAG"
	@echo "  2. Add tafseer sources for full functionality"
	@echo "  3. Run 'make index' after adding tafseer"
	@echo "  4. Access API at http://localhost:8000/docs"
	@echo "  5. Access frontend at http://localhost:3000"

# =============================================================================
# Cleanup Commands
# =============================================================================

clean: ## Clean up generated files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(NC)"

clean-all: clean ## Clean up everything including Docker volumes
	@echo "$(RED)WARNING: This will delete all data volumes$(NC)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker-compose down -v
	@echo "$(GREEN)Complete cleanup done$(NC)"
