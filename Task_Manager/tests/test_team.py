from tests.utils import login_headers


def _register(client, *, email: str, username: str, password: str = "password123"):
    r = client.post(
        "/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert r.status_code == 201, r.text


def test_create_team_and_join(client):
    _register(client, email="owner@example.com", username="owner")
    _register(client, email="member@example.com", username="member")

    owner_headers = login_headers(client, email="owner@example.com", password="password123")
    created = client.post(
        "/teams/",
        json={"name": "Alpha", "description": "Core squad"},
        headers=owner_headers,
    )
    assert created.status_code == 201
    team_id = created.json()["id"]

    member_headers = login_headers(client, email="member@example.com", password="password123")
    joined = client.post(f"/teams/{team_id}/join", headers=member_headers)
    assert joined.status_code == 200
    assert joined.json()["role"] == "member"

    outsider_headers = login_headers(client, email="owner@example.com", password="password123")
    detail = client.get(f"/teams/{team_id}", headers=outsider_headers)
    assert detail.status_code == 200


def test_get_team_forbidden_non_member(client):
    _register(client, email="a@example.com", username="aa")
    _register(client, email="b@example.com", username="bb")

    a_headers = login_headers(client, email="a@example.com", password="password123")
    team_id = client.post("/teams/", json={"name": "Secret"}, headers=a_headers).json()["id"]

    b_headers = login_headers(client, email="b@example.com", password="password123")
    forbidden = client.get(f"/teams/{team_id}", headers=b_headers)
    assert forbidden.status_code == 403
