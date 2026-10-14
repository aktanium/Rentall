from decimal import Decimal
from pathlib import Path

import pytest
from flask_migrate import upgrade
from sqlalchemy import text

from app import create_app
from app.extensions import db
from app.models import Category, Listing
from tests.factories import make_user

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


@pytest.fixture
def owner(app):
    return make_user("owner@example.com", is_owner=True)


@pytest.fixture
def renter(app):
    return make_user("renter@example.com")


@pytest.fixture
def listing(owner):
    category = Category(name="Машины", slug="cars", default_price_unit="day")
    listing = Listing(
        owner=owner,
        category=category,
        title="Toyota Camry",
        description="Test car",
        price=Decimal("3500"),
        price_unit="day",
        city="Бишкек",
        address="ул. Киевская, 96",
        lat=42.8761,
        lng=74.5962,
    )
    db.session.add(listing)
    db.session.commit()
    return listing
