import os

from dotenv import load_dotenv

load_dotenv()


def _normalize_db_url(url: str | None) -> str | None:
    """Make sure SQLAlchemy uses the psycopg 3 driver (Render gives postgres:// URLs)."""
    if not url:
        return url
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.environ.get("DATABASE_URL"))
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    WTF_CSRF_ENABLED = True
    TESTING = False
    DEBUG = False
    # Flask-Limiter. memory:// is per process; use Redis when running several workers.
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    PASSWORD_RESET_MAX_AGE = 3600  # seconds
    # Trust X-Forwarded-For from one proxy (Render) so rate limits see the real client IP.
    PROXY_FIX = False


class DevConfig(BaseConfig):
    DEBUG = True


class TestConfig(BaseConfig):
    TESTING = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "test-secret-key"
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.environ.get("TEST_DATABASE_URL"))
    WTF_CSRF_ENABLED = False


class ProdConfig(BaseConfig):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PROXY_FIX = True


CONFIGS = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig,
}
