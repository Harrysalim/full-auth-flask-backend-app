from models import User


def test_signup_creates_user_and_hashes_password(client, app):
    response = client.post(
        "/signup", json={"username": "harry", "password": "password123"}
    )
    assert response.status_code == 201
    with app.app_context():
        user = User.query.filter_by(username="harry").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert user.check_password("password123")

def test_signup_rejects_duplicate_username(client, registered_user):
    response = client.post(
        "/signup", json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 409

def test_signup_validates_password(client):
    response = client.post("/signup", json={"username": "short", "password": "123"})
    assert response.status_code == 400


def test_login_and_check_session(client, registered_user):
    client.post("/logout")
    login = client.post(
        "/login", json={"username": "testuser", "password": "password123"}
    )
    assert login.status_code == 200
    check = client.get("/check_session")
    assert check.status_code == 200
    assert check.get_json()["user"]["username"] == "testuser"

def test_login_rejects_wrong_password(client, registered_user):
    response = client.post(
        "/login", json={"username": "testuser", "password": "wrong-password"}
    )
    assert response.status_code == 401

def test_logout_clears_session(client, registered_user):
    response = client.post("/logout")
    assert response.status_code == 200
    assert client.get("/check_session").status_code == 401


