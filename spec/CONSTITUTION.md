# Before You Start

**Read First**:

- [README.md](../README.md) - Project overview and environment checklist
- [Makefile](../Makefile) - Common development and test commands
- [pyproject.toml](../pyproject.toml) - Runtime dependencies, tooling, and lint configuration
- [spec/TECH_STACK.md](TECH_STACK.md) - Dependency reference per stack layer

**Architecture Tip**: Run `tree --dirsfirst --prune -L 10 -I '__pycache__|*.log'` to inspect the hexagonal layers without cache noise.

## Layer-Specific Preferences

Our services follow a hexagonal architecture:

- **Domain** holds entities, value objects, and domain events (pure `attrs`-powered logic).
- **Application** orchestrates use cases via the Unit of Work interfaces.
- **Driven adapters** integrate with outbound systems (database/auth) using SQLAlchemy repos.
- **Driving adapters** expose inbound ports (FastAPI controllers, Pydantic schemas).
- **Platform** centralizes cross-cutting concerns such as configuration, migrations, logging, and notification stubs.

Refer to [TECH_STACK.md](TECH_STACK.md#hexagonal-architecture--layer-responsibilities) for a deeper breakdown.

# Must-Do Rules

- **Imports**: Always at top of file, never inside functions.
- **Async**: Prefer `async` over sync.
- **Function Parameters**: Use keyword-first style for clarity (`def action(*, order_id: int)`).
- **Dependency Inversion**: High-level modules depend on abstractions, not low-level implementations.
- **Transaction Management**: Use cases commit; repositories only perform CRUD.
- **Unit of Work Pattern**: Centralize session and repository management; define transaction boundaries.
- **Fail Fast**: Validate inputs and state early; raise domain exceptions immediately.
- **Open/Closed**: Open for extension, closed for modification.
- **Single Responsibility**: Each function, class, and module has one well-defined responsibility.
- **Logging**: Apply `Logger.io` decorators thoughtfully across layers to trace ingress/egress or critical operations.

# Core Development Philosophy

## BDD (Behavior-Driven Development)

**Before writing tests**: read [test/conftest.py](../test/conftest.py) for async fixtures, database bootstrap, and shared fakes.

- **Integration tests**: capture behavior in `.feature` files under `test/features/` using Given/When/Then.
- **Unit tests**: place fast, isolated tests in `test/<bounded_context>/unit/`, reuse doubles from `test/shared/fakes.py`.

## TDD (Test-Driven Development)

1. Write the test first - define expected behavior.
2. Watch it fail - ensure the test actually asserts something.
3. Write minimal code - just enough to make it pass.
4. Refactor - improve while keeping tests green.
5. Repeat - one test at a time.

## KISS (Keep It Simple, Stupid)

Choose straightforward solutions over complex ones. Simple code is easier to understand, maintain, and debug.

## YAGNI (You Aren't Gonna Need It)

Implement features only when they are required, not when you think they might be useful later.
