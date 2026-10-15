from flask import render_template, request

from app.listings import bp
from app.services import listings as listing_service


@bp.get("")
def index():
    slug = request.args.get("category")
    category = listing_service.get_category_or_404(slug) if slug else None
    page = request.args.get("page", 1, type=int)
    pagination = listing_service.paginate_listings(category, page)
    return render_template(
        "listings/index.html",
        categories=listing_service.get_categories(),
        current_category=category,
        pagination=pagination,
        ratings=listing_service.rating_summaries(pagination.items),
    )


@bp.get("/<int:listing_id>")
def detail(listing_id: int):
    listing = listing_service.get_active_listing_or_404(listing_id)
    return render_template(
        "listings/detail.html",
        listing=listing,
        rating=listing_service.rating_summaries([listing])[listing.id],
    )
