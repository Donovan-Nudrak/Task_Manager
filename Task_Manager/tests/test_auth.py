from tests.utils import login_headers


def test_register_and_login(client):
    email = "alice@example.com"
    password = "password123"
    reg = client.post(
        "/auth/register",
        json={"email": email, "username": "alice", "password": password},
    )
    assert reg.status_code == 201

    tok = login_headers(client, email=email, password=password)
    me_probe = client.get("/teams/", headers=tok)
    assert me_probe.status_code == 200


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "username": "u1", "password": "password123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    dup = client.post("/auth/register", json={**payload, "username": "u2"})
    assert dup.status_code == 400


def test_login_invalid_credentials(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    bad = client.post(
        "/auth/login",
        data={"username": "bob@example.com", "password": "wrong-password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert bad.status_code == 401


def test_protected_route_without_token(client):
    assert client.get("/teams/").status_code == 401
