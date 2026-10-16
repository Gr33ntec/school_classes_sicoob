import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import database_url

BACKEND = Path(__file__).resolve().parents[1]
TEST_DB = os.environ.get("DB_TEST_NAME", "school_management_test")


@pytest.fixture(scope="session")
def engine():
    # O fixture executa DROP DATABASE; nunca pode apontar para o banco real.
    if TEST_DB == os.environ.get("DB_NAME"):
        pytest.fail("DB_TEST_NAME deve diferir de DB_NAME")
    admin = create_engine(database_url("mysql"))
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS `{TEST_DB}`"))
        c.execute(
            text(
                f"CREATE DATABASE `{TEST_DB}` CHARACTER SET utf8mb4 "
                "COLLATE utf8mb4_0900_ai_ci"
            )
        )
    env = {**os.environ, "ALEMBIC_DB_NAME": TEST_DB}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND, env=env, check=True,
    )
    eng = create_engine(database_url(TEST_DB))
    yield eng
    eng.dispose()
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS `{TEST_DB}`"))


@pytest.fixture
def conn(engine):
    with engine.connect() as c:
        trans = c.begin()
        yield c
        trans.rollback()


@pytest.fixture
def client(engine):
    from app.core.database import get_db
    from app.main import app

    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()
    with engine.begin() as c:
        for table in ("enrollments", "school_classes", "students", "teachers", "courses"):
            c.execute(text(f"DELETE FROM {table}"))
