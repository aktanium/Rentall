from app.extensions import db
from app.models import User


def make_user(email: str, *, is_owner: bool = False) -> User:
    user = User(email=email, name="Test User", is_owner=is_owner)
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    return user
