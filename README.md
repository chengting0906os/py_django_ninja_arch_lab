# py_fastapi_arch_lab

## This repository is a lab for **Clean Architecture**, **Domain-Driven Design (DDD)**, and disciplined testing (TDD/BDD).

It implements Clean Architecture via a hexagonal (ports & adapters) structure: **driving adapters** handle inbound requests (FastAPI controllers), while **driven adapters** connect to outbound dependencies (SQLAlchemy repositories, auth services).

## Clean Architecture Overview

```
src/
├─ domain/           # Core business model: aggregates, entities, value objects, domain events
│                    # pure business logic
├─ app/
│  ├─ interface/     # Ports (abstract contracts/interfaces) defining dependencies
│  └─ use_case/      # Application services orchestrating domain/business workflows via those ports
│
├─ driven_adapter/   # Outbound adapters implementing app interfaces
│                    # (repositories, external APIs, message queues)
│
├─ driving_adapter/  # Inbound adapters exposing app functionality
│                    # (REST controllers, GraphQL resolvers, CLI commands)
│
└─ platform/         # Shared infrastructure concerns
                     # (config, database setup, logging, DI container)
```

---

## Domain Layer Overview

```
src/domain/
├─ aggregate/       # Aggregate roots (OrderAggregate manages invariants & events)
├─ entity/          # Entities (Order/Product/User with attrs + validators)
├─ value_object/    # Immutable snapshots (BuyerInfo, ProductSnapshot, etc.)
├─ enum/            # Domain enums (OrderStatus, ProductStatus, UserRole)
└─ domain_event/    # Events describing state changes (OrderCreatedEvent, etc.)
```

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
