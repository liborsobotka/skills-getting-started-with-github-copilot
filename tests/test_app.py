import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities_state():
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities_returns_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = activities["Chess Club"]["participants"][0]

    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    assert response.status_code == 400


def test_unregister_removes_participant(client):
    email = activities["Soccer Club"]["participants"][0]

    response = client.delete("/activities/Soccer%20Club/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in activities["Soccer Club"]["participants"]


def test_unregister_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Drama%20Club/signup",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
