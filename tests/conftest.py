from pathlib import Path

import pytest
from flask import g
from flask_migrate import upgrade
from sqlalchemy import text

from app import create_app
from app.extensions import db, limiter
from tests.factories import make_category, make_listing, make_user

MIGRATIONS_DIR = str(Path(__file__).resolve().parent.parent / "migrations")


def _reset_schema() -> None:
    db.session.remove()
    with db.engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))


@pytest.fixture(scope="session")
def app():
    app = create_app("test")

    @app.teardown_request
    def _forget_cached_user(exc):
        # Tests share one app context (and `g`), where Flask-Login caches the user.
        # Drop it so every request loads the user from its own session cookie.
        g.pop("_login_user", None)

    with app.app_context():
        # Build the schema from migrations so DB-level constraints match production.
        _reset_schema()
        upgrade(directory=MIGRATIONS_DIR)
        yield app
        _reset_schema()


@pytest.fixture(autouse=True)
def _clean_tables(app):
    limiter.reset()
    yield
    db.session.remove()
    tables = ", ".join(f'"{t.name}"' for t in db.metadata.sorted_tables)
    if tables:
        with db.engine.begin() as conn:
            conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def owner(app):
    return make_user("owner@example.com", is_owner=True)


@pytest.fixture
def renter(app):
    return make_user("renter@example.com")


@pytest.fixture
def listing(owner):
    return make_listing(owner, make_category())
