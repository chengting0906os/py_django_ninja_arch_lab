# Tech Stack Overview

This project targets **Python 3.13** and relies on the `uv` toolchain for managing virtual environments and locking dependencies (`uv.lock`). When running locally, Docker Compose spins up the PostgreSQL service defined in `docker-compose.yml`.

## Domain-Specific Notes

- Core domain logic sits in `src/domain`, with aggregates emitting events defined in `src/domain/domain_event`.
- Use cases under `src/app/use_case` depend on abstract interfaces in `src/app/interface`. This project does not use a formal Unit of Work pattern; transactions are managed inside application use cases or repository implementations as needed.
- Migrations are managed via Django's migration system (manage.py makemigrations / migrate) and adapter-specific tools when necessary.

## Hexagonal Architecture Layers

- **Domain (`src/domain`)**

  - Use `attrs` for aggregates, entities, and value objects; keep the code side-effect free.
  - Guard invariants with enums and value objects; publish domain events from aggregates.
  - Never depend on adapters, frameworks, or persistence details.

- **Application (`src/app`)**

  - Implement use cases that depend only on interfaces in `src/app/interface`.
  - Manage transactions and persistence calls inside use cases or repository implementations;
  - Inject dependencies via Django settings or a simple service registry when exposed through driving adapters.

- **Driven Adapter (`src/driven_adapter`)** — outbound ports (DB, auth, external services)

  - Implement repository interfaces defined in `src/app/interface/`.
  - Use Django ORM for database operations; keep queries isolated in repository implementations.
  - Authentication helpers and external service integrations belong here.
  - Avoid leaking infrastructure details or ORM models outside this layer.

- **Driving Adapter (`src/driving_adapter`)** — inbound ports (HTTP/API)

  - Django views/controllers handle HTTP requests and translate to application use cases.
  - Centralize auth and dependency helpers in `http_controller/dependency/`; route handlers should remain free of business rules.
  - Apply logging decorators (e.g., `Logger.io`) at entry/exit points where visibility is valuable.

- **Platform (`src/platform`)**
  - Holds cross-cutting infrastructure: Django configuration, database models, migrations, logging, and shared utilities.
  - `src/platform/config/settings.py` defines Django settings; database and CORS configuration are here.
  - `src/platform/models/` contains Django ORM models (User, Product, Order).
  - `src/platform/migrations/` holds Django database migrations.
  - Dependency injection configured in `src/platform/config/di.py`.
  - Utility modules (logging, exception handling) should remain framework-agnostic where possible.

Refer back to `pyproject.toml` for full version constraints and dependency groups.

## Library Inventory

### Web & API

- **Django** – main web framework.
- **django-ninja / django-ninja-extra** – API router and DI support.
- **uvicorn[standard]** – ASGI server for development/production.
- **django-cors-headers** – CORS support (if enabled).

## Data & Persistence

- **Django ORM** – primary ORM for Django models, admin integration, and Django-managed migrations where applicable.
- **pydantic / pydantic-settings** – validation and environment configuration.
- **email-validator** – email format checks.

### Auth & Security

- **passlib[bcrypt]** – password hashing.

### Observability & Support

- **loguru** – structured logging with `Logger.io`.

### Testing

- **pytest** – test runner.
- **pytest-asyncio**, **httpx** – async testing and HTTP clients.
- **pytest-xdist** – parallel execution.

### Quality & Analysis

- **ruff** – linting and auto-formatting.
- **pyrefly** – runtime dependency and contract analysis.
