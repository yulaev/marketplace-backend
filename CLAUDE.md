# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workflow rules (enforced by `.claude/hooks/branch_policy.py`)
- Only work on branch `exp`. `main` is blocked. Worktrees off `exp` are allowed; creating new branches is not.
- If instructed to work on a blocked branch, report it as: `[entity] instructed [session/session subagent] to work on [branch]`.
- Never `git push`. Commits require explicit user review/approval first — prompt for review after edits, before committing.

## Commands
- Run app (dev, hot reload): `docker compose up` (uses `compose.override.yaml`); prod: `docker compose -f compose.yaml up`
- Run all tests: `pytest`
- Run one test file/case: `pytest app/tests/test_products.py::test_name`
- Migrations: `alembic revision --autogenerate -m "message"` to generate, `alembic upgrade head` to apply (runs automatically on container start); commit the generated file in `alembic/versions/`
- Tests need `TEST_DB` set (see `.env.example`); set `BCRYPT_ROUNDS=4` to speed up hashing in tests

## Architecture
FastAPI app (`app/main.py`) mounting three routers (`users`, `products`, `orders`), each following the same layering:
`routers/*_router.py` (HTTP + JWT dependency) → `crud/*_crud.py` (business logic, ownership/role checks) → `models/*.py` (SQLAlchemy ORM). Request/response validation lives in `schemas/*.py`, kept separate from ORM models (e.g. `ProductEdit` vs. `ProductRestock` are distinct schemas for what are conceptually different operations on the same model).

- **Auth** (`app/utilities/auth.py`): JWT via `python-jose`/`PyJWT`, bcrypt password hashing, roles `customer`/`seller`/`admin` (`UserRole` enum). Admins can only be created directly in the DB. `oauth2_scheme` + `validate_token` gate protected routes.
- **Orders** (`app/models/order.py`): `Order` has many `OrderItem`s. Both carry an `OrderStatus` (`pending → ordered → shipped → delivered`) with a `priority` property; an order's effective status is derived from its least-progressed item. Sellers mark items `shipped`; customers mark items `delivered`. One active (`pending`) cart per customer — placing an order transitions all its items to `ordered`, after an availability check; a non-pending order is complete and a new cart is required for further purchases.
- **DB sessions** (`app/database.py`): engine built from `DATABASE_URL`; `get_session` is the FastAPI dependency injected into routers.
- **Tests** (`app/tests/conftest.py`): separate `TEST_DB` engine; each test runs in a transaction + savepoint that's rolled back afterward (`test_session` fixture), with `client` overriding `get_session` via `app.dependency_overrides`. `set_up_get_token` fixture registers a user and returns a bearer token for authenticated requests.
