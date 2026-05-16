# Dark Moon

API REST para gestión de tareas en equipos. Construida con **FastAPI**, **SQLAlchemy** y **PostgreSQL**. Los usuarios se autentican con JWT, crean o se unen a equipos y gestionan tareas asociadas a cada equipo.

## Arquitectura general

El código sigue una estructura en capas:

```
Cliente HTTP → Routers (endpoints) → Services (lógica de negocio) → Models (BD)
                      ↓
                 Schemas (validación / respuestas)
```

La configuración, la conexión a base de datos y las dependencias de autenticación viven en `app/core/`.

---

## Raíz del proyecto

| Archivo / carpeta    | Propósito                                                                                |
| -------------------- | ---------------------------------------------------------------------------------------- |
| `requirements.txt`   | Dependencias Python del proyecto (FastAPI, SQLAlchemy, Alembic, etc.).                   |
| `docker-compose.yml` | Levanta el contenedor de PostgreSQL para desarrollo local.                               |
| `.env`               | Variables de entorno (URL de BD, clave secreta, modo debug). No versionar en producción. |
| `script_init.sh`     | Script de arranque rápido: lanza la API con Uvicorn en modo recarga.                     |
| `alembic.ini`        | Configuración principal de Alembic (rutas, URL de BD para migraciones).                  |

---

## `app/` — Aplicación FastAPI

### Punto de entrada

| Archivo | Propósito |
|---------|-----------|
| `app/main.py` | Instancia la aplicación FastAPI, registra los routers y expone el endpoint de salud (`/health`). |

### `app/core/` — Infraestructura compartida

| Archivo | Propósito |
|---------|-----------|
| `app/core/config.py` | Carga la configuración desde variables de entorno y `.env` (Pydantic Settings). |
| `app/core/database.py` | Motor SQLAlchemy, sesiones de BD y dependencia `get_db` para inyectar la sesión en los endpoints. |
| `app/core/dependencies.py` | Dependencias reutilizables: usuario autenticado (JWT), pertenencia a equipo y rol de owner. |

### `app/routers/` — Capa HTTP (endpoints)

| Archivo | Propósito |
|---------|-----------|
| `app/routers/auth.py` | Rutas de registro y login (`/auth`). |
| `app/routers/team.py` | Rutas CRUD básicas de equipos: crear, unirse, listar y consultar (`/teams`). |
| `app/routers/task.py` | Rutas de tareas: crear, listar por equipo y actualizar estado (`/tasks`). |

### `app/services/` — Lógica de negocio

| Archivo | Propósito |
|---------|-----------|
| `app/services/auth.py` | Registro de usuarios, hash de contraseñas, autenticación y generación de tokens JWT. |
| `app/services/team.py` | Creación de equipos, alta de miembros y consultas relacionadas. |
| `app/services/task.py` | Creación y consulta de tareas, validación de pertenencia al equipo y cambio de estado. |

### `app/models/` — Modelos ORM (tablas SQLAlchemy)

| Archivo | Propósito |
|---------|-----------|
| `app/models/user.py` | Entidad `User` (credenciales y datos básicos del usuario). |
| `app/models/team.py` | Entidades `Team` y `TeamMember` (equipos y relación usuario–equipo con rol). |
| `app/models/task.py` | Entidad `Task` (tareas vinculadas a un equipo y opcionalmente a un usuario asignado). |
| `app/models/models.py` | Borrador o versión alternativa de modelos unificados (enums y relaciones); no es el que importa `main.py` actualmente. |

### `app/schemas/` — Contratos Pydantic (entrada/salida API)

| Archivo | Propósito |
|---------|-----------|
| `app/schemas/user.py` | Esquemas de registro, respuesta de usuario y token de acceso. |
| `app/schemas/team.py` | Esquemas para crear equipos, devolver datos de equipo y de membresía. |
| `app/schemas/task.py` | Esquemas para crear tareas, enums de estado/prioridad y respuestas de tarea. |

---

## `alembic/` — Migraciones de base de datos

| Archivo / carpeta | Propósito |
|-------------------|-----------|
| `alembic/env.py` | Entorno de ejecución de Alembic; enlaza los modelos SQLAlchemy con las migraciones. |
| `alembic/script.py.mako` | Plantilla Mako para generar nuevos archivos de revisión. |
| `alembic/README` | Documentación breve incluida por Alembic sobre el uso de migraciones. |
| `alembic/versions/ea756a49ded1_initial_tables.py` | Revisión inicial de migración (placeholder; aún sin cambios de esquema aplicados). |

---

## Flujo funcional resumido

1. El usuario se **registra** o **inicia sesión** y obtiene un token Bearer.
2. Con el token, puede **crear equipos** o **unirse** a equipos existentes.
3. Como miembro de un equipo, puede **crear tareas**, **listarlas** por equipo y **actualizar su estado**.

La base de datos puede crearse al arrancar vía `create_all` en `main.py` o, en un despliegue más formal, mediante migraciones Alembic una vez estén definidas.

---

## Puesta en marcha (referencia rápida)

```bash
# Base de datos
docker compose up -d

# Dependencias
pip install -r requirements.txt

# API (también disponible vía script_init.sh)
uvicorn app.main:app --reload
```

Documentación interactiva de la API: `http://localhost:8000/docs`
