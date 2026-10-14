from flask import jsonify, render_template

from app.main import bp
from app.services.health import database_is_up


@bp.get("/")
def index():
    return render_template("main/index.html")


@bp.get("/health")
def health():
    if database_is_up():
        return jsonify(status="ok"), 200
    return jsonify(status="error", database="unavailable"), 503
