# Marketplace Backend

A backend API for a multi-seller marketplace built with FastAPI and PostgreSQL. Buyers can browse products, manage a cart, and place orders. Sellers can list and manage their own products

---

## Stack

- **Python 3.14**
- **FastAPI** — API layer
- **SQLAlchemy** — ORM
- **PostgreSQL** — database
- **Alembic** — migrations
- **bcrypt** — password hashing
- **JWT** — authentication
- **Docker + Docker Compose** — containerization

---

## Features

### Auth
- JWT-based authentication with role-based access control
- Three roles: `customer`, `seller`, `admin`
- Admin accounts can only be created directly via the database
- Passwords hashed with bcrypt
- Ownership and role checks

### Users
- Register as customer or seller
- Login returns a JWT

### Products
- Sellers can list, edit, and restock products
- Restock accepts a signed quantity — positive to add stock, negative to remove stock
- Editing a listing and restocking are separate endpoints with separate schemas

### Cart & Orders
- Customers add products to a cart (one active cart per customer)
- Place order transitions all items from `pending` to `ordered`
- Availability check before any status changes are applied

### Order Status System
Items and orders follow a status hierarchy:

```
pending → ordered → shipped → delivered
```

- **Seller** marks individual items as `shipped`
- **Customer** marks individual items as `delivered`
- Order status is derived from its items — the order is only as far along as its least progressed item
- A non-pending order is considered complete — new cart required for future purchases

---

## Getting Started

### Prerequisites
- Docker and Docker Compose installed and running

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/yulaev/marketplace-backend.git
cd marketplace-backend
```

**2. Create your environment file**
```bash
cp .env.example .env
```

Fill in the values in `.env`:
```
DATABASE_URL=postgresql://postgres:yourpassword@db:5432/marketplace
SECRET_KEY=your_secret_key_here
```

Generate a secure secret key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**3. Create the database password file**
```bash
mkdir db
echo "yourpassword" > db/password.txt
```

The password here must match the one in your `DATABASE_URL`.

**4. Make the entrypoint executable**
```bash
chmod +x entrypoint.sh
```

**5. Start the containers**
```bash
docker compose up --build
```

On first run, the entrypoint script automatically runs `alembic upgrade head` to build the schema before starting the server.

---

## Running in Development Mode

The `docker-compose.override.yml` is picked up automatically and enables:
- Hot reload via `fastapi dev`
- Bind mount so code changes reflect immediately without rebuilding
- Database port exposed for direct connection via TablePlus or psql

```bash
docker compose up
```

For production mode (no override):
```bash
docker compose -f docker-compose.yml up
```

---

## Example curl Commands

**Register**
```bash
curl -X POST http://localhost:8000/users/sign-up \
  -H "Content-Type: application/json" \
  -d '{"name": "alice", "password": "password123", "email": "alice@example.com", "role": "customer"}'
```

**Login**
```bash
curl -X POST http://localhost:8000/users/sign-in \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=password123"
```

**Store the token**
```bash
export TOKEN="your_jwt_token_here"
```

**Add to cart**
```bash
curl -X POST http://localhost:8000/orders/add-to-cart \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

**Place order**
```bash
curl -X PATCH http://localhost:8000/orders/place-order \
  -H "Authorization: Bearer $TOKEN"
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Secret used to sign JWTs — generate with `secrets.token_hex(32)` |

See `.env.example`

---

## Migrations

Migrations are managed with Alembic and run automatically on container startup.

To generate a new migration after changing a model:
```bash
alembic revision --autogenerate -m "describe the change"
```

To apply manually:
```bash
alembic upgrade head
```

Commit the generated file in `alembic/versions/`