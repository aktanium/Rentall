from flask import jsonify, render_template

from app.main import bp
from app.services import listings as listing_service
from app.services.health import database_is_up


@bp.get("/")
def index():
    latest = listing_service.latest_listings()
    return render_template(
        "main/index.html",
        categories=listing_service.get_categories(),
        latest=latest,
        ratings=listing_service.rating_summaries(latest),
    )


@bp.get("/health")
def health():
    if database_is_up():
        return jsonify(status="ok"), 200
    return jsonify(status="error", database="unavailable"), 503
