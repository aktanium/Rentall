from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import event

from app.extensions import db
from app.models import Booking, Review
from app.services.listings import rating_summaries
from tests.factories import make_category, make_listing, make_user


def card_count(html: str) -> int:
    return html.count('class="card h-100 shadow-sm listing-card"')


@pytest.fixture
def categories(app):
    return {
        "cars": make_category("cars", "Машины", "day"),
        "bikes": make_category("bikes", "Велосипеды", "hour"),
    }


# --- Catalog --------------------------------------------------------------------------------


def test_catalog_shows_all_active_listings(client, owner, categories):
    make_listing(owner, categories["cars"], "Toyota Camry")
    make_listing(owner, categories["bikes"], "Merida Big Nine", price="150", price_unit="hour")

    html = client.get("/listings").get_data(as_text=True)

    assert "Toyota Camry" in html
    assert "Merida Big Nine" in html
    assert "Найдено: 2 объявления" in html


def test_catalog_filtered_by_category(client, owner, categories):
    make_listing(owner, categories["cars"], "Toyota Camry")
    make_listing(owner, categories["bikes"], "Merida Big Nine", price="150", price_unit="hour")

    response = client.get("/listings?category=bikes")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Merida Big Nine" in html
    assert "Toyota Camry" not in html
    assert "150 сом / час" in html
    # The current category pill is highlighted.
    assert 'class="nav-link active" href="/listings?category=bikes"' in html


def test_catalog_unknown_category_returns_404(client, categories):
    assert client.get("/listings?category=boats").status_code == 404


def test_catalog_hides_inactive_listings(client, owner, categories):
    make_listing(owner, categories["cars"], "Visible car")
    make_listing(owner, categories["cars"], "Hidden car", is_active=False)

    html = client.get("/listings").get_data(as_text=True)

    assert "Visible car" in html
    assert "Hidden car" not in html


def test_catalog_pagination(client, owner, categories):
    for i in range(15):
        make_listing(owner, categories["cars"], f"Car {i:02d}")

    page1 = client.get("/listings?category=cars").get_data(as_text=True)
    page2 = client.get("/listings?category=cars&page=2").get_data(as_text=True)

    assert card_count(page1) == 12
    assert card_count(page2) == 3
    # Newest first: the last created listing is on page 1, the first one on page 2.
    assert "Car 14" in page1
    assert "Car 00" not in page1
    assert "Car 00" in page2
    # Pagination links keep the category filter.
    assert 'href="/listings?page=2&amp;category=cars"' in page1


def test_catalog_page_out_of_range_returns_404(client, owner, categories):
    make_listing(owner, categories["cars"])

    assert client.get("/listings?page=5").status_code == 404


def test_catalog_empty_category(client, categories):
    html = client.get("/listings?category=bikes").get_data(as_text=True)

    assert "В этой категории пока нет объявлений." in html


def test_catalog_avoids_n_plus_one_queries(client, owner, categories):
    def count_queries(url: str) -> int:
        statements = []

        def before_execute(conn, cursor, statement, *args):
            statements.append(statement)

        event.listen(db.engine, "before_cursor_execute", before_execute)
        try:
            assert client.get(url).status_code == 200
        finally:
            event.remove(db.engine, "before_cursor_execute", before_execute)
        return len(statements)

    make_listing(owner, categories["cars"], "Car A", images=2)
    db.session.expire_all()
    queries_for_one = count_queries("/listings")

    for i in range(11):
        make_listing(owner, categories["bikes"], f"Bike {i}", images=2)
    db.session.expire_all()  # nothing may be served from the identity map
    queries_for_twelve = count_queries("/listings")

    assert queries_for_twelve == queries_for_one


# --- Home page ------------------------------------------------------------------------------


def test_home_shows_categories_and_8_latest_listings(client, owner, categories):
    for i in range(10):
        make_listing(owner, categories["cars"], f"Car {i:02d}")
    make_listing(owner, categories["cars"], "Hidden car", is_active=False)

    html = client.get("/").get_data(as_text=True)

    assert "Новые объявления" in html
    assert card_count(html) == 8
    assert "Car 09" in html
    assert "Car 02" in html
    assert "Car 01" not in html
    assert "Car 00" not in html
    assert "Hidden car" not in html
    assert 'href="/listings?category=bikes"' in html
    assert "bi-bicycle" in html


# --- Listing details ------------------------------------------------------------------------


def test_listing_page(client, owner, categories):
    listing = make_listing(owner, categories["cars"], "Toyota Camry", price="2500", images=3)

    response = client.get(f"/listings/{listing.id}")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Toyota Camry" in html
    assert "2 500 сом / сутки" in html
    assert owner.name in html
    assert html.count('class="carousel-item') == 3
    assert 'id="listing-map"' in html
    assert 'data-lat="42.8761"' in html
    assert "leaflet.js" in html
    assert "Забронировать" in html
    assert "Отзывов пока нет." in html


def test_listing_page_without_coordinates_has_no_map(client, owner, categories):
    listing = make_listing(owner, categories["cars"], lat=None, lng=None, images=0)

    html = client.get(f"/listings/{listing.id}").get_data(as_text=True)

    assert 'id="listing-map"' not in html
    assert "bi-image" in html  # photo placeholder


def test_missing_listing_returns_404(client):
    assert client.get("/listings/999999").status_code == 404


def test_inactive_listing_returns_404(client, owner, categories):
    listing = make_listing(owner, categories["cars"], is_active=False)

    assert client.get(f"/listings/{listing.id}").status_code == 404


# --- Ratings --------------------------------------------------------------------------------


def test_rating_summaries(owner, categories):
    rated = make_listing(owner, categories["cars"], "Rated")
    unrated = make_listing(owner, categories["cars"], "Unrated")
    renter = make_user("renter@example.com")
    start = datetime(2026, 1, 1, tzinfo=UTC)
    for day, rating in enumerate([4, 5]):
        booking = Booking(
            listing=rated,
            renter=renter,
            start_at=start + timedelta(days=day),
            end_at=start + timedelta(days=day, hours=12),
            total_price=Decimal("3500"),
            status="completed",
        )
        db.session.add(
            Review(booking=booking, author=renter, listing=rated, rating=rating, text="Ок")
        )
    db.session.commit()

    summaries = rating_summaries([rated, unrated])

    assert (summaries[rated.id].average, summaries[rated.id].count) == (4.5, 2)
    assert (summaries[unrated.id].average, summaries[unrated.id].count) == (0.0, 0)


def test_card_shows_zero_reviews(client, listing):
    html = client.get("/listings").get_data(as_text=True)

    assert 'title="0 отзывов"' in html
    assert "0.0" in html
