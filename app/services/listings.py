from dataclasses import dataclass

from flask import abort
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload

from app.extensions import db
from app.models import Category, Listing, Review

CATALOG_PER_PAGE = 12
LATEST_LIMIT = 8


@dataclass(frozen=True)
class RatingSummary:
    average: float = 0.0
    count: int = 0


def _active_listings_query():
    return (
        select(Listing)
        .where(Listing.is_active.is_(True))
        .options(selectinload(Listing.images), selectinload(Listing.category))
        .order_by(Listing.created_at.desc(), Listing.id.desc())
    )


def get_categories() -> list[Category]:
    return list(db.session.scalars(select(Category).order_by(Category.id)))


def get_category_or_404(slug: str) -> Category:
    category = db.session.scalar(select(Category).where(Category.slug == slug))
    if category is None:
        abort(404)
    return category


def latest_listings(limit: int = LATEST_LIMIT) -> list[Listing]:
    return list(db.session.scalars(_active_listings_query().limit(limit)))


def paginate_listings(category: Category | None, page: int) -> Pagination:
    query = _active_listings_query()
    if category is not None:
        query = query.where(Listing.category_id == category.id)
    return db.paginate(query, page=page, per_page=CATALOG_PER_PAGE, error_out=True)


def get_active_listing_or_404(listing_id: int) -> Listing:
    listing = db.session.scalar(
        select(Listing)
        .where(Listing.id == listing_id, Listing.is_active.is_(True))
        .options(
            selectinload(Listing.images),
            selectinload(Listing.category),
            joinedload(Listing.owner),
        )
    )
    if listing is None:
        abort(404)
    return listing


def rating_summaries(listings: list[Listing]) -> dict[int, RatingSummary]:
    """Average rating and review count for many listings in one query."""
    ids = [listing.id for listing in listings]
    summaries = {listing_id: RatingSummary() for listing_id in ids}
    if not ids:
        return summaries
    rows = db.session.execute(
        select(Review.listing_id, func.avg(Review.rating), func.count(Review.id))
        .where(Review.listing_id.in_(ids))
        .group_by(Review.listing_id)
    )
    for listing_id, average, count in rows:
        summaries[listing_id] = RatingSummary(round(float(average), 1), count)
    return summaries
