# `docker compose` (plugin) when available, else the standalone `docker-compose`.
COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo docker-compose)
BACKEND := $(COMPOSE) run --rm backend
BACKEND_NO_DB := $(COMPOSE) run --rm --no-deps backend
FRONTEND := $(COMPOSE) run --rm --no-deps frontend

.PHONY: up down build migrate format lint lint-backend lint-frontend test test-backend test-frontend load reload fetch competitions openapi dump

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

migrate:
	$(BACKEND) alembic upgrade head

format:
	$(BACKEND_NO_DB) sh -c "ruff check --fix --exit-zero . && ruff format ."

lint: lint-backend lint-frontend

lint-backend:
	$(BACKEND_NO_DB) sh scripts/lint.sh

test: test-backend test-frontend

test-backend:
	$(BACKEND) sh scripts/test.sh

lint-frontend:
	$(FRONTEND) sh -c "npm ci && npm run lint && npm run typecheck"

test-frontend:
	$(FRONTEND) sh -c "npm ci && npm test"

load:
	$(COMPOSE) run --rm ingestion judogg-ingest load --files tests/fixtures/ijf

# Rebuilds the app tables from the stored raw responses: unlike `load`, it never re-imports the examples.
reload:
	$(COMPOSE) run --rm ingestion judogg-ingest load

# Example: make fetch ARGS="--year 2025 --load"
fetch:
	$(COMPOSE) run --rm ingestion judogg-ingest fetch $(ARGS)

YEAR ?= $(shell date +%Y)

# The ids for `make fetch ARGS="--competition <id>"`, from the stored competitions list: make competitions YEAR=2026
competitions:
	@$(COMPOSE) exec -T db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -v year="$(YEAR)" -f -' < docker/db/competitions.sql

openapi:
	$(COMPOSE) run --rm --no-deps -T backend python -m judogg.app.interfaces.api.export_openapi > frontend/openapi.json
	$(FRONTEND) sh -c "npm ci && npm run gen:api"

dump:
	mkdir -p data
	$(COMPOSE) exec -T db sh -c 'pg_dump -U "$$POSTGRES_USER" "$$POSTGRES_DB"' > data/judogg-$$(date +%Y%m%d-%H%M%S).sql
