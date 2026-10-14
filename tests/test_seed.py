from sqlalchemy import func, select

from app.extensions import db
from app.models import Category, Listing, ListingImage, User
from app.services.seed import SEED_PASSWORD, seed


def count(model) -> int:
    return db.session.scalar(select(func.count()).select_from(model))


def test_seed_creates_demo_data(app):
    result = seed()

    assert (result.categories, result.users, result.listings) == (5, 5, 20)
    assert count(Category) == 5
    assert count(User) == 5
    assert count(Listing) == 20
    assert count(ListingImage) == 40

    owners = db.session.scalars(select(User).where(User.is_owner)).all()
    assert len(owners) == 2
    assert all(user.check_password(SEED_PASSWORD) for user in owners)

    names = set(db.session.scalars(select(Category.name)))
    assert names == {"Машины", "Велосипеды", "Самокаты", "Жильё", "Площадки"}

    for listing in db.session.scalars(select(Listing)):
        assert listing.city == "Бишкек"
        assert 42.80 < listing.lat < 42.92
        assert 74.50 < listing.lng < 74.70
        assert listing.owner.is_owner


def test_seed_is_idempotent(app):
    seed()
    result = seed()

    assert (result.categories, result.users, result.listings) == (0, 0, 0)
    assert count(Listing) == 20


def test_seed_cli_command(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["seed"])

    assert result.exit_code == 0
    assert "20 listings" in result.output
