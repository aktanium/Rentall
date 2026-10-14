from pathlib import Path

import pytest
from flask_migrate import upgrade
from sqlalchemy import text

from app import create_app
from app.extensions import db

MIGRATIONS_DIR = str(Path(__file__).resolve().parent.parent / "migrations")


def _reset_schema() -> None:
    db.session.remove()
    with db.engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))


@pytest.fixture(scope="session")
def app():
    app = create_app("test")
    with app.app_context():
        # Build the schema from migrations so DB-level constraints match production.
        _reset_schema()
        upgrade(directory=MIGRATIONS_DIR)
        yield app
        _reset_schema()


@pytest.fixture(autouse=True)
def _clean_tables(app):
    yield
    db.session.remove()
    tables = ", ".join(f'"{t.name}"' for t in db.metadata.sorted_tables)
    if tables:
        with db.engine.begin() as conn:
            conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(app):
    return app.test_client()
