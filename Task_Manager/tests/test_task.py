from tests.utils import login_headers


def _register(client, *, email: str, username: str, password: str = "password123"):
    r = client.post(
        "/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert r.status_code == 201, r.text


def _team_with_member(client):
    _register(client, email="lead@example.com", username="lead")
    _register(client, email="dev@example.com", username="dev")
    lead_h = login_headers(client, email="lead@example.com", password="password123")
    team_id = client.post("/teams/", json={"name": "Engineering"}, headers=lead_h).json()["id"]
    dev_h = login_headers(client, email="dev@example.com", password="password123")
    client.post(f"/teams/{team_id}/join", headers=dev_h)
    return team_id, lead_h, dev_h


def test_create_task_and_list(client):
    team_id, _, dev_h = _team_with_member(client)

    created = client.post(
        "/tasks/",
        headers=dev_h,
        json={
            "title": "Ship MVP",
            "description": "Backend polish",
            "team_id": team_id,
            "status": "pending",
            "priority": "high",
        },
    )
    assert created.status_code == 201

    page = client.get(f"/tasks/team/{team_id}?page=1&limit=10", headers=dev_h)
    assert page.status_code == 200
    body = page.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_task_filter_by_status(client):
    team_id, _, dev_h = _team_with_member(client)

    client.post(
        "/tasks/",
        headers=dev_h,
        json={"title": "A", "team_id": team_id, "status": "pending"},
    )
    t2 = client.post(
        "/tasks/",
        headers=dev_h,
        json={"title": "B", "team_id": team_id, "status": "done"},
    )
    assert t2.status_code == 201

    pending_only = client.get(
        f"/tasks/team/{team_id}?status=pending",
        headers=dev_h,
    )
    assert pending_only.json()["total"] == 1
    assert pending_only.json()["items"][0]["title"] == "A"


def test_tasks_forbidden_non_member(client):
    team_id, _, _ = _team_with_member(client)
    _register(client, email="outsider@example.com", username="outsider")
    out_h = login_headers(client, email="outsider@example.com", password="password123")

    denied = client.get(f"/tasks/team/{team_id}", headers=out_h)
    assert denied.status_code == 403


def test_update_task_status_permission_denied(client):
    team_id, _, dev_h = _team_with_member(client)
    task_id = client.post(
        "/tasks/",
        headers=dev_h,
        json={"title": "Doc API", "team_id": team_id},
    ).json()["id"]

    _register(client, email="other@example.com", username="other")
    other_h = login_headers(client, email="other@example.com", password="password123")

    patch = client.patch(
        f"/tasks/{task_id}/status?status=in_progress",
        headers=other_h,
    )
    assert patch.status_code == 403
