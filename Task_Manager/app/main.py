from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.logging_config import setup_logging
from app.routers import auth, task as task_router, team as team_router


setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Task Manager API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(team_router.router)
app.include_router(task_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    """Fails if the database is unreachable."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ready"}
