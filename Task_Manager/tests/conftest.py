import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("APP_ENV", "dev")
os.environ.setdefault("LOG_LEVEL", "WARNING")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://taskuser:taskpass@localhost:5432/task_manager_test",
)
os.environ["DATABASE_URL"] = DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def _apply_migrations():
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        check=True,
        env={**os.environ},
    )


@pytest.fixture(scope="session")
def engine(_apply_migrations):
    eng = create_engine(DATABASE_URL, poolclass=NullPool)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def truncate_tables(db_session):
    db_session.execute(
        text("TRUNCATE TABLE tasks, team_members, teams, users RESTART IDENTITY CASCADE")
    )
    db_session.commit()
    yield


@pytest.fixture
def client(db_session):
    from app.core.database import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
