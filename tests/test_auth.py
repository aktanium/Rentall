import time

import pytest
from flask_login import login_user
from itsdangerous import TimestampSigner
from sqlalchemy import func, select
from werkzeug.exceptions import Forbidden

from app.auth.decorators import admin_required, owner_required
from app.extensions import db
from app.models import User
from app.services import auth as auth_service
from tests.factories import login, make_user

REGISTRATION = {
    "name": "Айгерим",
    "email": "aigerim@example.com",
    "password": "secret123",
    "confirm": "secret123",
}


def user_count() -> int:
    return db.session.scalar(select(func.count()).select_from(User))


# --- Registration ---------------------------------------------------------------------------


def test_successful_registration_logs_user_in(client):
    response = client.post("/auth/register", data=REGISTRATION)

    assert response.status_code == 302
    user = auth_service.get_user_by_email("aigerim@example.com")
    assert user is not None
    assert user.name == "Айгерим"
    assert user.password_hash != "secret123"
    assert user.check_password("secret123")
    assert not user.is_owner

    page = client.get("/").get_data(as_text=True)
    assert "Айгерим" in page
    assert "Выйти" in page


@pytest.mark.parametrize("email", ["aigerim@example.com", "  AIGERIM@Example.com "])
def test_duplicate_email_is_rejected(client, email):
    make_user("aigerim@example.com")

    response = client.post("/auth/register", data={**REGISTRATION, "email": email})

    assert response.status_code == 200
    assert "Этот email уже зарегистрирован." in response.get_data(as_text=True)
    assert user_count() == 1


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"password": "short", "confirm": "short"}, "Пароль должен быть не короче 8 символов."),
        ({"confirm": "different123"}, "Пароли не совпадают."),
        ({"email": "not-an-email"}, "Введите корректный email."),
        ({"name": ""}, "Введите имя."),
    ],
)
def test_registration_validation_errors(client, changes, message):
    response = client.post("/auth/register", data={**REGISTRATION, **changes})

    assert response.status_code == 200
    assert message in response.get_data(as_text=True)
    assert user_count() == 0


# --- Login / logout -------------------------------------------------------------------------


def test_login_with_correct_password(client, renter):
    response = login(client, renter.email)

    assert response.status_code == 302
    assert client.get("/me/profile").status_code == 200


def test_login_with_wrong_password(client, renter):
    response = login(client, renter.email, "wrong-password")

    assert response.status_code == 200
    assert "Неверный email или пароль." in response.get_data(as_text=True)
    assert client.get("/me/profile").status_code == 302


def test_login_with_unknown_email_shows_same_error(client):
    response = login(client, "nobody@example.com")

    assert "Неверный email или пароль." in response.get_data(as_text=True)


def test_remember_me_sets_cookie(client, renter):
    login(client, renter.email, remember="y")

    assert client.get_cookie("remember_token") is not None


def test_login_without_remember_me_sets_no_cookie(client, renter):
    login(client, renter.email)

    assert client.get_cookie("remember_token") is None


def test_login_follows_safe_next_url(client, renter):
    response = client.post(
        "/auth/login?next=/me/profile", data={"email": renter.email, "password": "password123"}
    )

    assert response.headers["Location"] == "/me/profile"


@pytest.mark.parametrize("next_url", ["https://evil.example.com", "//evil.example.com"])
def test_login_ignores_external_next_url(client, renter, next_url):
    response = client.post(
        f"/auth/login?next={next_url}", data={"email": renter.email, "password": "password123"}
    )

    assert response.headers["Location"] == "/"


def test_logout(client, renter):
    login(client, renter.email)

    response = client.post("/auth/logout")

    assert response.status_code == 302
    assert client.get("/me/profile").status_code == 302


def test_login_rate_limit_after_5_attempts(client, renter):
    for _ in range(5):
        assert login(client, renter.email, "wrong-password").status_code == 200

    response = login(client, renter.email, "wrong-password")

    assert response.status_code == 429
    assert "Слишком много попыток" in response.get_data(as_text=True)


def test_rate_limit_does_not_block_login_page(client, renter):
    for _ in range(6):
        login(client, renter.email, "wrong-password")

    assert client.get("/auth/login").status_code == 200


# --- Navbar ---------------------------------------------------------------------------------


def test_navbar_for_guest(client):
    page = client.get("/").get_data(as_text=True)

    assert "Войти" in page
    assert "Регистрация" in page
    assert "Кабинет" not in page


def test_navbar_for_logged_in_user(client, renter):
    login(client, renter.email)

    page = client.get("/").get_data(as_text=True)

    assert renter.name in page
    assert "Кабинет" in page
    assert "Выйти" in page
    assert "Регистрация" not in page


# --- Profile --------------------------------------------------------------------------------


@pytest.mark.parametrize("url", ["/me", "/me/profile"])
def test_profile_redirects_anonymous_user_to_login(client, url):
    response = client.get(url)

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login")


def test_edit_profile(client, renter):
    login(client, renter.email)

    response = client.post("/me/profile", data={"name": "Бекзат", "phone": "+996 555 123 456"})

    assert response.status_code == 302
    db.session.refresh(renter)
    assert renter.name == "Бекзат"
    assert renter.phone == "+996 555 123 456"


def test_edit_profile_rejects_invalid_phone(client, renter):
    login(client, renter.email)

    response = client.post("/me/profile", data={"name": "Бекзат", "phone": "abc"})

    assert response.status_code == 200
    assert "Введите номер в формате" in response.get_data(as_text=True)


def test_become_owner(client, renter):
    login(client, renter.email)
    assert "Стать арендодателем" in client.get("/me/profile").get_data(as_text=True)

    response = client.post("/me/become-owner")

    assert response.status_code == 302
    db.session.refresh(renter)
    assert renter.is_owner
    assert "Вы арендодатель" in client.get("/me/profile").get_data(as_text=True)


def test_become_owner_requires_login(client):
    response = client.post("/me/become-owner")

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login")


# --- Decorators -----------------------------------------------------------------------------


def _view():
    return "ok"


@pytest.mark.parametrize(
    ("decorator", "flags"),
    [(owner_required, {"is_owner": True}), (admin_required, {"is_admin": True})],
)
def test_role_decorators_allow_users_with_role(app, decorator, flags):
    user = make_user("role@example.com")
    for name, value in flags.items():
        setattr(user, name, value)
    db.session.commit()

    with app.test_request_context():
        login_user(user)
        assert decorator(_view)() == "ok"


@pytest.mark.parametrize("decorator", [owner_required, admin_required])
def test_role_decorators_return_403_without_role(app, decorator):
    user = make_user("plain@example.com")

    with app.test_request_context():
        login_user(user)
        with pytest.raises(Forbidden):
            decorator(_view)()


@pytest.mark.parametrize("decorator", [owner_required, admin_required])
def test_role_decorators_redirect_anonymous_to_login(app, decorator):
    with app.test_request_context():
        response = decorator(_view)()

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_403_page_is_in_russian(app):
    with app.test_request_context():
        response = app.make_response(app.handle_http_exception(Forbidden()))

    assert response.status_code == 403
    assert "У вас нет доступа" in response.get_data(as_text=True)


# --- Password reset -------------------------------------------------------------------------


def test_reset_request_sends_email_with_link(client, renter, monkeypatch):
    sent = []
    monkeypatch.setattr(auth_service, "send_email", lambda **kwargs: sent.append(kwargs))

    response = client.post("/auth/reset-password", data={"email": renter.email})

    assert response.status_code == 302
    assert len(sent) == 1
    assert sent[0]["to"] == renter.email
    assert "/auth/reset-password/" in sent[0]["body"]


def test_reset_request_for_unknown_email_sends_nothing(client, monkeypatch):
    sent = []
    monkeypatch.setattr(auth_service, "send_email", lambda **kwargs: sent.append(kwargs))

    response = client.post(
        "/auth/reset-password", data={"email": "nobody@example.com"}, follow_redirects=True
    )

    assert sent == []
    assert "Если такой аккаунт существует" in response.get_data(as_text=True)


def test_send_email_logs_message(app, caplog):
    from app.services.email import send_email

    with caplog.at_level("INFO"):
        send_email(to="a@example.com", subject="Тема", body="https://link")

    assert "a@example.com" in caplog.text
    assert "https://link" in caplog.text


def test_valid_reset_token_changes_password(client, renter):
    token = auth_service.generate_reset_token(renter)
    assert auth_service.verify_reset_token(token) == renter

    response = client.post(
        f"/auth/reset-password/{token}", data={"password": "newpass123", "confirm": "newpass123"}
    )

    assert response.status_code == 302
    db.session.refresh(renter)
    assert renter.check_password("newpass123")
    assert login(client, renter.email, "newpass123").status_code == 302


def test_reset_token_cannot_be_used_twice(client, renter):
    token = auth_service.generate_reset_token(renter)
    client.post(
        f"/auth/reset-password/{token}", data={"password": "newpass123", "confirm": "newpass123"}
    )

    assert auth_service.verify_reset_token(token) is None


def test_expired_reset_token_is_rejected(client, renter, monkeypatch):
    issued_at = int(time.time()) - 3601  # just over 1 hour ago
    with monkeypatch.context() as m:
        m.setattr(TimestampSigner, "get_timestamp", lambda self: issued_at)
        token = auth_service.generate_reset_token(renter)

    assert auth_service.verify_reset_token(token) is None

    response = client.get(f"/auth/reset-password/{token}", follow_redirects=True)
    assert "недействительна или устарела" in response.get_data(as_text=True)


def test_tampered_reset_token_is_rejected(renter):
    token = auth_service.generate_reset_token(renter)

    assert auth_service.verify_reset_token(token[:-2] + "xx") is None
