from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import ACTIVE_STATUSES, Booking, Listing, Review, User
from tests.factories import make_user

START = datetime(2026, 11, 1, 10, 0, tzinfo=UTC)


def add_booking(listing, renter, start, end, status="pending") -> Booking:
    booking = Booking(
        listing=listing,
        renter=renter,
        start_at=start,
        end_at=end,
        total_price=Decimal("7000"),
        status=status,
    )
    db.session.add(booking)
    db.session.commit()
    return booking


def test_user_password_is_hashed(owner):
    assert owner.password_hash != "password123"
    assert owner.check_password("password123")
    assert not owner.check_password("wrong")


def test_duplicate_email_is_rejected(owner):
    duplicate = User(email=owner.email, name="Someone else", password_hash="x")
    db.session.add(duplicate)
    with pytest.raises(IntegrityError):
        db.session.commit()


@pytest.mark.parametrize("price", [Decimal("0"), Decimal("-100")])
def test_listing_price_must_be_positive(listing, price):
    listing.price = price
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_listing_price_unit_must_be_hour_or_day(listing):
    listing.price_unit = "week"
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_booking_end_must_be_after_start(listing, renter):
    with pytest.raises(IntegrityError):
        add_booking(listing, renter, START, START)


@pytest.mark.parametrize("existing_status", ACTIVE_STATUSES)
def test_overlapping_active_bookings_are_rejected(listing, renter, existing_status):
    add_booking(listing, renter, START, START + timedelta(days=2), status=existing_status)

    other = make_user("other@example.com")
    with pytest.raises(IntegrityError, match="no_overlap"):
        add_booking(listing, other, START + timedelta(days=1), START + timedelta(days=3))


@pytest.mark.parametrize("inactive_status", ["cancelled", "completed"])
def test_inactive_booking_does_not_block_dates(listing, renter, inactive_status):
    add_booking(listing, renter, START, START + timedelta(days=2), status=inactive_status)

    booking = add_booking(listing, renter, START, START + timedelta(days=2))
    assert booking.id is not None


def test_back_to_back_bookings_are_allowed(listing, renter):
    add_booking(listing, renter, START, START + timedelta(days=2))

    booking = add_booking(listing, renter, START + timedelta(days=2), START + timedelta(days=4))
    assert booking.id is not None


def test_same_dates_on_different_listings_are_allowed(listing, renter, owner):
    second = Listing(
        owner=owner,
        category=listing.category,
        title="Honda Fit",
        description="Another car",
        price=Decimal("2000"),
        price_unit="day",
        city="Бишкек",
        address="пр. Манаса, 40",
    )
    db.session.add(second)
    db.session.commit()

    add_booking(listing, renter, START, START + timedelta(days=2))
    booking = add_booking(second, renter, START, START + timedelta(days=2))
    assert booking.id is not None


@pytest.mark.parametrize("rating", [0, 6])
def test_review_rating_must_be_between_1_and_5(listing, renter, rating):
    booking = add_booking(listing, renter, START, START + timedelta(days=1), status="completed")
    db.session.add(
        Review(booking=booking, author=renter, listing=listing, rating=rating, text="Отлично")
    )
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_only_one_review_per_booking(listing, renter):
    booking = add_booking(listing, renter, START, START + timedelta(days=1), status="completed")
    db.session.add(Review(booking=booking, author=renter, listing=listing, rating=5, text="Да"))
    db.session.commit()

    db.session.add(
        Review(booking_id=booking.id, author=renter, listing=listing, rating=4, text="Ещё")
    )
    with pytest.raises(IntegrityError):
        db.session.commit()
