.PHONY: api
.PHONY: db

dev: ## Setup dev environment
	poetry env use python3.10
	poetry install
	poetry run pre-commit install

api:
	poetry install
	poetry run alembic upgrade head
	poetry run uvicorn main:app --reload --port 8008 --host 0.0.0.0

audit:
	poetry self add poetry-audit-plugin
	poetry audit

docker-run:
	docker build --tag 'coach-ai-api' -f Dockerfile .; \
	docker run --env-file .env -p 8008:8008 coach-ai-api;

test:
	poetry run pytest tests

test-cov:
	poetry run pytest tests --cov=src -vv --cov-config=.coveragerc --cov-report=term-missing --cov-branch

db:
	docker compose -p coach-ai -f docker-compose.yaml up -d sqlserver
