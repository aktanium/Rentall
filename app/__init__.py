import os

from flask import Flask, render_template

from app.extensions import csrf, db, login_manager, migrate
from config import CONFIGS


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_CONFIG", "dev")
    config_class = CONFIGS[config_name]

    app = Flask(__name__)
    app.config.from_object(config_class)

    missing = [key for key in ("SECRET_KEY", "SQLALCHEMY_DATABASE_URI") if not app.config.get(key)]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models  # noqa: F401  (register models with SQLAlchemy metadata)

    _register_blueprints(app)
    _register_error_handlers(app)

    return app


def _register_blueprints(app: Flask) -> None:
    from app.auth import bp as auth_bp
    from app.bookings import bp as bookings_bp
    from app.dashboard import bp as dashboard_bp
    from app.listings import bp as listings_bp
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(listings_bp, url_prefix="/listings")
    app.register_blueprint(bookings_bp, url_prefix="/bookings")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500
