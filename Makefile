# Run `make help` to list targets.
.DEFAULT_GOAL := help
.PHONY: help install api web test e2e build-web migrate docker-compose build-image

IMAGE ?= hhollenstain/autochannel-ui:latest

help: ## List targets
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-16s %s\n", $$1, $$2}'

install: ## Install backend (uv sync) and frontend (npm ci) dependencies
	uv sync
	cd frontend && npm ci

# In dev, set FRONTEND_URL=http://localhost:5173 so OAuth returns to Vite.
api: ## Flask API on :5000 (needs the env vars from .env.example)
	uv run autochannel_ui --debug

web: ## Vite dev server on :5173, proxies /api, /login, /logout to :5000
	cd frontend && npm run dev

test: ## Lint + pytest + frontend typecheck/unit tests
	uv run ruff check .
	uv run pytest
	cd frontend && npm run typecheck && npm test

e2e: ## Playwright browser tests with mocked /api; screenshots in frontend/e2e/screenshots/
	cd frontend && npm run test:e2e

build-web: ## Production build of the frontend
	cd frontend && npm run build

migrate: ## alembic upgrade head against SQLALCHEMY_DATABASE_URI
	uv run alembic -c packages/autochannel-db/alembic.ini upgrade head

docker-compose: build-image ## Build the image, then docker compose up with 1Password-injected env
	op run --env-file=.env-dev -- docker compose up

build-image: ## Build the Docker image (override with IMAGE=...)
	docker build -t $(IMAGE) .
