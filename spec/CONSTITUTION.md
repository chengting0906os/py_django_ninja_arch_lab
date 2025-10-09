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
- **Application** orchestrates use cases and coordinates repositories; transactions are managed by use cases or repository implementations (there is no mandatory global Unit of Work abstraction in this codebase).
- **Driven adapters** integrate with outbound systems (database/auth) using repository implementations (often SQLAlchemy-based).
- **Driving adapters** expose inbound ports (Django views/controllers and django-ninja endpoints where applicable); request/response schemas (Pydantic) are used in API layers when helpful.
- **Platform** centralizes cross-cutting concerns such as configuration, migrations, logging, and notification stubs.

Refer to [TECH_STACK.md](TECH_STACK.md#hexagonal-architecture-layers) for a deeper breakdown.

# Must-Do Rules

- **Imports**: Always at top of file, never inside functions.
- **Async**: Prefer `async` for I/O-bound work (network, external services).
- **Function Parameters**: Use keyword-first style for clarity (`def action(*, order_id: int)`).
- **Dependency Inversion**: High-level modules depend on abstractions, not low-level implementations. See [di.py](../src/platform/config/di.py) for DI configuration.
- **Fail Fast**: Validate inputs and state early; raise domain exceptions immediately.
- **Open/Closed**: Open for extension, closed for modification.
- **Single Responsibility**: Each function, class, and module has one well-defined responsibility.
- **Logging**: Apply `@Logger.io` decorators to public methods to trace ingress/egress operations.
- **Pydantic Schemas**: All `BaseModel` schemas MUST include a `Config` class with `from_attributes = True` and `json_schema_extra` containing example data for API documentation (OpenAPI/Swagger).

# Core Development Philosophy

## BDD (Behavior-Driven Development)

**Before writing tests**: read [test/conftest.py](../test/conftest.py) for fixtures, database bootstrap, and shared fakes. The test suite uses pytest with async helpers and a custom `SessionTestAsyncClient` to support Django session-based auth.

- **Integration tests**: tests follow a BDD-style structure (Given/When/Then) by convention, but the project does not rely on an external BDD framework or `.feature` files. Look for helper modules under `test/*/integration/util/` (for example `test_product_given_util.py`, `test_product_when_util.py`, `test_product_then_util.py`).
- **Unit tests**: place fast, isolated tests in `test/<bounded_context>/unit/`, reuse doubles from `test/shared/fakes.py`.

Notes:

- The BDD flavor is achieved through helper functions and consistent naming; prefer using the existing Given/When/Then helpers when adding integration tests.

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
