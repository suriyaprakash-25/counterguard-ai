.PHONY: help build up down restart logs test lint format check

help:
	@echo "Available commands:"
	@echo "  build    - Build Docker images"
	@echo "  up       - Start Docker containers in detached mode"
	@echo "  down     - Stop and remove Docker containers"
	@echo "  restart  - Restart Docker containers"
	@echo "  logs     - Tail Docker container logs"
	@echo "  test     - Run tests via pytest"
	@echo "  lint     - Run ruff linter"
	@echo "  format   - Run ruff formatter"
	@echo "  check    - Run pre-commit hooks"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	pytest backend/tests

lint:
	ruff check .

format:
	ruff format .

check:
	pre-commit run --all-files
