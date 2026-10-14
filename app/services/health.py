from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


def database_is_up() -> bool:
    try:
        db.session.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False
