# Tech Stack Overview

This project targets **Python 3.13** and relies on the `uv` toolchain for managing virtual environments and locking dependencies (`uv.lock`). When running locally, Docker Compose spins up the PostgreSQL service defined in `docker-compose.yml`.

## Domain-Specific Notes

- Core domain logic sits in `src/domain`, with aggregates emitting events defined in `src/domain/domain_event`.
- Use cases under `src/app/use_case` follow the Unit of Work pattern from `src/platform/db/unit_of_work.py`.
- Migrations are generated via `uv run alembic` using the settings resolved in `src/platform/config/core_setting.py`.

## Hexagonal Architecture Layers

- **Domain (`src/domain`)**

  - Use `attrs` for aggregates, entities, and value objects; keep the code side-effect free.
  - Guard invariants with enums and value objects; publish domain events from aggregates.
  - Never depend on adapters, frameworks, or persistence details.

- **Application (`src/app`)**

  - Implement async use cases that depend only on interfaces in `src/app/interface`.
  - Enforce Unit of Work boundaries via `src/platform/db/unit_of_work.py`; call `commit()` only from the use case.
  - Inject dependencies with FastAPI `Depends` (or similar) when exposed through driving adapters.

- **Driven Adapter (`src/driven_adapter`)** — outbound ports (DB, auth, external services)

  - Map persistence with SQLAlchemy models in `model/`; implement repository interfaces in `repo/` using async sessions.
  - Keep database-specific queries and authentication helpers (FastAPI Users, Passlib) isolated here.
  - Avoid leaking SQLAlchemy models or infrastructure types outside this layer.

- **Driving Adapter (`src/driving_adapter`)** — inbound ports (HTTP/API)

  - FastAPI controllers translate between HTTP/Pydantic schemas and application use cases.
  - Centralize auth and dependency helpers in `http_controller/dependency/`; route handlers stay free of business rules.
  - Apply logging decorators (e.g., `Logger.io`) at entry/exit points where visibility is valuable.

- **Platform (`src/platform`)**
  - Holds cross-cutting infrastructure: configuration loading, Alembic migrations, DB sessions, logging, notification stubs, and shared exceptions.
  - `src/platform/config/core_setting.py` defines environment-driven settings; `src/platform/alembic` provides migration tooling.
  - Utility modules (logging, notification, constants) should remain framework-agnostic and reusable by multiple adapters.

Refer back to `pyproject.toml` for full version constraints and dependency groups.

## Library Inventory

### Web & API

- **FastAPI** – async web framework for driving adapters.
- **uvicorn[standard]** – ASGI server for development/production.
- **fastapi-users[sqlalchemy]** – user/auth management utilities.

### Data & Persistence

- **SQLAlchemy** – ORM/Core for repositories and models.
- **asyncpg** – async PostgreSQL driver.
- **psycopg2-binary** – sync driver used by Alembic/tests.
- **Alembic** – migrations (configured in `src/platform/alembic`).
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
- **pytest-bdd-ng**, **pytest-postgresql** – BDD steps and ephemeral Postgres.

### Quality & Analysis

- **ruff** – linting and auto-formatting.
- **pyrefly** – runtime dependency and contract analysis.
