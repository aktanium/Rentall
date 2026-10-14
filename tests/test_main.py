from sqlalchemy.exc import OperationalError

from app.extensions import db


def test_home_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "RentAll" in response.get_data(as_text=True)


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_health_returns_503_when_database_is_down(client, monkeypatch):
    def broken_execute(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(db.session, "execute", broken_execute)

    response = client.get("/health")
    assert response.status_code == 503
    assert response.get_json()["status"] == "error"


def test_unknown_url_returns_404(client):
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert "Такой страницы нет" in response.get_data(as_text=True)
