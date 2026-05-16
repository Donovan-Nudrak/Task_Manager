# Task Manager API

Production-minded FastAPI backend for **multi-team task management**: JWT authentication, PostgreSQL persistence via SQLAlchemy 2.x, Alembic migrations, layered architecture (routers → services → repositories), RBAC-style team roles, soft-delete columns, pagination/filtering on tasks, Docker deployment, and CI with GitHub Actions.

---

## Highlights

- **FastAPI** + **Pydantic v2** validation (`Field` constraints on users, teams, tasks).
- **PostgreSQL** + **SQLAlchemy 2.0** declarative models (`Mapped` / `mapped_column`).
- **Alembic** as the **only** schema mechanism (no runtime `create_all`).
- **JWT** access tokens with configurable **`ACCESS_TOKEN_EXPIRE_MINUTES`**, Unix `exp`, and typed **`TokenPayload`** validation after decode.
- **Repositories** isolate persistence; **services** hold business rules; **routers** stay thin.
- **Team roles**: `viewer`, `member`, `manager`, `admin`, `owner` (PostgreSQL `ENUM`).
- **Soft delete** (`deleted_at`) and **audit** timestamps (`created_at`, `updated_at`) on core entities.
- **Health**: `GET /health` (liveness) and `GET /health/ready` (database probe).

---

## Architecture

### Layered design

```mermaid
flowchart LR
  HTTP[HTTP_Client]
  R[routers]
  S[services]
  P[PermissionService]
  Rep[repositories]
  DB[(PostgreSQL)]

  HTTP --> R --> S --> Rep --> DB
  S --> P
```

| Layer | Responsibility |
|-------|----------------|
| `app/routers/` | HTTP adapters, dependency injection, status codes |
| `app/services/` | Business workflows (teams, tasks, auth) |
| `app/services/permissions.py` | Centralised authorisation (`PermissionService`) |
| `app/repositories/` | SQLAlchemy queries only |
| `app/models/` | ORM mappings |
| `app/schemas/` | Request/response contracts |

---

## JWT flow

```mermaid
sequenceDiagram
  participant C as Client
  participant A as AuthRouter
  participant S as AuthService
  participant DB as PostgreSQL

  C->>A: POST /auth/login (OAuth2 form, username = email)
  A->>S: authenticate_user
  S->>DB: load active user by email
  S-->>A: User or failure
  A->>S: create_access_token(sub=email)
  Note over S: exp / iat as Unix timestamps (UTC)
  A-->>C: access_token + bearer type

  C->>A: Protected route + Authorization Bearer
  A->>S: decode_token_payload + TokenPayload validation
  A->>DB: resolve user by sub (email), check is_active
```

---

## ER diagram (conceptual)

```mermaid
erDiagram
  USER ||--o{ TEAM_MEMBER : joins
  TEAM ||--o{ TEAM_MEMBER : has
  USER ||--o{ TEAM : owns
  TEAM ||--o{ TASK : contains
  USER ||--o{ TASK : creates
  USER ||--o{ TASK : assigned_optional

  USER {
    int id PK
    string email UK
    string username UK
    bool is_active
    datetime created_at
    datetime updated_at
    datetime deleted_at
  }

  TEAM {
    int id PK
    string name UK
    string description
    int owner_id FK
    datetime created_at
    datetime updated_at
    datetime deleted_at
  }

  TEAM_MEMBER {
    int user_id PK_FK
    int team_id PK_FK
    enum role
  }

  TASK {
    int id PK
    string title
    string description
    string status
    string priority
    int team_id FK
    int created_by FK
    int assigned_to FK
    datetime created_at
    datetime updated_at
    datetime deleted_at
  }
```

---

## Configuration & environments

Settings load **environment variables first**, then optional env files:

1. `.env.{APP_ENV}` (for example `.env.prod` when `APP_ENV=prod`)
2. `.env`

Templates (safe to commit):

- [.env.example](.env.example)
- [.env.dev.example](.env.dev.example)
- [.env.prod.example](.env.prod.example)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQLAlchemy URL (`postgresql+psycopg://...`) |
| `SECRET_KEY` | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL |
| `DEBUG` | SQL echo / verbose behaviour |
| `APP_ENV` | Selects optional `.env.{APP_ENV}` file |
| `LOG_LEVEL` | Root logging level (`INFO`, `DEBUG`, …) |

---

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

docker compose up -d db            # PostgreSQL on localhost:5432
export DATABASE_URL=postgresql+psycopg://taskuser:taskpass@localhost:5432/task_manager
alembic upgrade head
uvicorn app.main:app --reload
```

Interactive docs: `http://localhost:8000/docs`

### Full stack (API + DB)

```bash
docker compose up --build
```

The API container runs `alembic upgrade head` before starting Uvicorn.

---

## Alembic

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
alembic downgrade -1
```

`alembic/env.py` reads **`DATABASE_URL` from application settings**, so Docker/Railway/CI stay aligned without editing `alembic.ini`.

---

## Example HTTP calls

Register:

```bash
curl -s -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","username":"alice","password":"password123"}'
```

Login (OAuth2 password flow — **`username` must be the email**):

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=alice@example.com&password=password123'
```

Create a team (Bearer token):

```bash
curl -s -X POST http://localhost:8000/teams/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Platform","description":"Core services"}'
```

Paginated & filtered tasks:

```bash
curl -s "http://localhost:8000/tasks/team/1?page=1&limit=20&status=done" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing & linting

Requires PostgreSQL (tests default to `task_manager_test`).

```bash
createdb dark_moon_test   # once
export DATABASE_URL=postgresql+psycopg://taskuser:taskpass@localhost:5432/task_manager_test
pytest -q
ruff check app alembic tests
```

---

## Observability

- Structured stdout logging configured via **`LOG_LEVEL`**.
- **`GET /health`** — process up.
- **`GET /health/ready`** — verifies database connectivity (`SELECT 1`).

---

## Deploy on Railway

1. Create a Railway project from this repo.
2. Add the **PostgreSQL** plugin and copy the generated `DATABASE_URL`.
3. Set service variables: `SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `APP_ENV=prod`, `LOG_LEVEL=INFO`.
4. Railway invokes **[railway.toml](railway.toml)** **`startCommand`**, which applies migrations then launches Uvicorn on **`PORT`**.

---

## GitHub Actions

[`.github/workflows/ci.yml`](/.github/workflows/ci.yml) installs dependencies, runs **Ruff**, applies **Alembic** migrations against a **PostgreSQL 16** service, and executes **pytest**.

---

## Project layout

| Path | Role |
|------|------|
| `app/main.py` | FastAPI app, routers, `/health*` |
| `app/core/` | Settings, DB session, JWT deps, logging |
| `app/routers/` | HTTP endpoints |
| `app/services/` | Domain workflows + `PermissionService` |
| `app/repositories/` | Persistence helpers |
| `app/models/` | SQLAlchemy models (`Mapped` API) |
| `app/schemas/` | Pydantic I/O models |
| `alembic/` | Migration scripts |
| `tests/` | Pytest suite (`httpx`/`TestClient` compatible stack) |
| `Dockerfile` / `docker-compose.yml` | Container workflows |

---

## Security notes

- **Never commit real `.env` files** or database passwords.
- Rotate **`SECRET_KEY`** for every environment.
- `GET /teams/{id}` requires **team membership** (IDs are not enumerable anonymously).

Licensed for portfolio / educational use unless otherwise stated.
