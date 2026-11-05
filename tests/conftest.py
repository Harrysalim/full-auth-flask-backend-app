import pytest

from app import create_app
from extensions import db

class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def registered_user(client):
    response = client.post(
        "/signup",
        json={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 201
    return response.get_json()["user"]