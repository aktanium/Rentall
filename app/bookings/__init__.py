from flask import Blueprint

bp = Blueprint("bookings", __name__)

from app.bookings import routes  # noqa: E402, F401
