from flask import current_app, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import select

from app.extensions import db
from app.models import User
from app.services.email import send_email

RESET_SALT = "password-reset"


class EmailTakenError(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(email: str) -> User | None:
    return db.session.scalar(select(User).where(User.email == normalize_email(email)))


def register_user(name: str, email: str, password: str) -> User:
    if get_user_by_email(email) is not None:
        raise EmailTakenError(email)
    user = User(name=name.strip(), email=normalize_email(email))
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate(email: str, password: str) -> User | None:
    user = get_user_by_email(email)
    if user is None or not user.check_password(password):
        return None
    return user


def update_profile(user: User, name: str, phone: str | None) -> None:
    user.name = name.strip()
    user.phone = (phone or "").strip() or None
    db.session.commit()


def become_owner(user: User) -> None:
    user.is_owner = True
    db.session.commit()


# --- Password reset -------------------------------------------------------------------------


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=RESET_SALT)


def _password_fingerprint(user: User) -> str:
    # Part of the current hash: the token stops working once the password is changed.
    return user.password_hash[-16:]


def generate_reset_token(user: User) -> str:
    return _serializer().dumps({"uid": user.id, "pw": _password_fingerprint(user)})


def verify_reset_token(token: str) -> User | None:
    """Return the user for a valid, unexpired, unused token, otherwise None."""
    max_age = current_app.config["PASSWORD_RESET_MAX_AGE"]
    try:
        data = _serializer().loads(token, max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None
    user = db.session.get(User, data.get("uid"))
    if user is None or data.get("pw") != _password_fingerprint(user):
        return None
    return user


def send_password_reset(email: str) -> None:
    """Email a reset link if the account exists. Callers must not reveal whether it does."""
    user = get_user_by_email(email)
    if user is None:
        return
    link = url_for("auth.reset_password", token=generate_reset_token(user), _external=True)
    send_email(
        to=user.email,
        subject="RentAll: восстановление пароля",
        body=(
            f"Здравствуйте, {user.name}!\n\n"
            f"Чтобы задать новый пароль, перейдите по ссылке (действует 1 час):\n{link}\n\n"
            "Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо."
        ),
    )


def reset_password(user: User, new_password: str) -> None:
    user.set_password(new_password)
    db.session.commit()
