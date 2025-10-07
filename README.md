# py_fastapi_arch_lab

## This repository is a lab for **Clean Architecture**, **Domain-Driven Design (DDD)**, and disciplined testing (TDD/BDD).

## Clean Architecture at a Glance

```
src/
├─ domain/           # Core business model (pure, side-effect free)
├─ app/              # Application layer (use cases, orchestrating ports)
├─ driven_adapter/   # Outbound adapters (DB, auth, external services)
├─ driving_adapter/  # Inbound adapters (FastAPI controllers, schemas)
└─ platform/         # Cross-cutting infrastructure (config, DB, logging, migrations)
```

- **Domain layer** (`src/domain`) – business truth in `attrs` entities, value objects, aggregates, domain events, and enums.
- **Application layer** (`src/app`) – async use cases and UoW boundaries built on interfaces.
- **Driven adapters** (`src/driven_adapter`) – SQLAlchemy repos, auth helpers, and other outbound integrations.
- **Driving adapters** (`src/driving_adapter`) – FastAPI controllers + Pydantic schemas as inbound ports.
- **Platform** (`src/platform`) – configuration, Alembic migrations, DB sessions, logging, notifications.

---

## Inside the Domain Layer

```
src/domain/
├─ aggregate/       # Aggregate roots (OrderAggregate manages invariants & events)
├─ entity/          # Entities (Order/Product/User with attrs + validators)
├─ value_object/    # Immutable snapshots (BuyerInfo, ProductSnapshot, etc.)
├─ enum/            # Domain enums (OrderStatus, ProductStatus, UserRole)
└─ domain_event/    # Events describing state changes (OrderCreatedEvent, etc.)
```

- **Aggregates** enforce invariants and emit events (`OrderAggregate` orchestrates reservation/payment/cancellation).
- **Entities** capture business state with `attrs` validators (e.g., price must be positive).
- **Value objects** provide immutable snapshots for messaging across layers.
- **Domain events** express meaningful changes that adapters can react to.

---

## Simple Shopping Platform Scope

**User Stories**

- **Authentication**

  - As a visitor, I can register as seller
  - As a visitor, I can register as buyer
  - As a user, I can login
  - As a user, I can logout

- **Seller**

  - As a seller, I can create product
  - As a seller, I can manage stock
  - As a seller, I can view sales

- **Buyer**
  - As a buyer, I can browse product
  - As a buyer, I can buy product
  - As a buyer, I can make payment
  - As a buyer, I can view my orders

Features are intentionally lightweight; focus on the architecture patterns.

---

## Further Reading

- Clean Architecture & DDD overview: [spec/TECH_STACK.md](spec/TECH_STACK.md)
- Development constitution (TDD, BDD, coding rules): [spec/CONSTITUTION.md](spec/CONSTITUTION.md)
