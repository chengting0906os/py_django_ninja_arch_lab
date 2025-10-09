# Database migrations
.PHONY: makemigrations mm
makemigrations mm:
	@echo "Creating Django migrations..."
	@uv run python manage.py makemigrations

.PHONY: migrate m
migrate m:
	@echo "Running Django migrations..."
	@uv run python manage.py migrate

.PHONY: migrate-show ms
migrate-show ms:
	@echo "Showing migration status..."
	@uv run python manage.py showmigrations

# Testing
.PHONY: test t mt
test t mt:
	@uv run pytest test/ -v -n 15



# Linting and formatting
.PHONY: lint
lint:
	@uv run ruff check .

.PHONY: format
format:
	@uv run ruff format .

.PHONY: pyre
pyre:
	@uv run pyrefly check

# Development
.PHONY: run
run:
	@uv run uvicorn src.platform.config.asgi:application --reload --host 0.0.0.0 --port 8000

.PHONY: clean
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name ".DS_Store" -delete

# Docker
.PHONY: docker-up
docker-up:
	@docker-compose up -d

.PHONY: docker-down
docker-down:
	@docker-compose down

.PHONY: docker-logs
docker-logs:
	@docker-compose logs -f

.PHONY: db-shell psql
db-shell psql:
	@docker exec -it shopping_db psql -U py_arch_lab -d shopping_db

# Help
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  Database Migrations:"
	@echo "    make makemigrations (mm) - Create new Django migrations"
	@echo "    make migrate (m)         - Run Django migrations"
	@echo "    make migrate-show (ms)   - Show migration status"
	@echo ""
	@echo "  Testing:"
	@echo "    make test (t)            - Run all tests"
	@echo ""
	@echo "  Development:"
	@echo "    make run                 - Run development server"
	@echo "    make lint                - Check code style"
	@echo "    make format              - Format code"
	@echo "    make pyre                - Run type checking"
	@echo "    make clean               - Remove cache files"
	@echo ""
	@echo "  Docker & Database:"
	@echo "    make docker-up           - Start Docker containers"
	@echo "    make docker-down         - Stop Docker containers"
	@echo "    make docker-logs         - View Docker logs"
	@echo "    make db-shell (psql)     - Connect to PostgreSQL shell"
