import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root path redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Use a test email
    test_email = "test@mergington.edu"
    activity = "Chess Club"

    # Get initial participants
    response = client.get("/activities")
    initial_participants = response.json()[activity]["participants"]
    initial_count = len(initial_participants)

    # Signup
    response = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 200
    assert f"Signed up {test_email} for {activity}" in response.json()["message"]

    # Verify participant was added
    response = client.get("/activities")
    updated_participants = response.json()[activity]["participants"]
    assert len(updated_participants) == initial_count + 1
    assert test_email in updated_participants


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_signed_up():
    """Test signup when already signed up"""
    test_email = "duplicate@mergington.edu"
    activity = "Programming Class"

    # First signup
    client.post(f"/activities/{activity}/signup?email={test_email}")

    # Try to signup again
    response = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 400
    assert "Student already signed up" in response.json()["detail"]


def test_delete_success():
    """Test successful deletion from an activity"""
    test_email = "delete_test@mergington.edu"
    activity = "Gym Class"

    # First signup
    client.post(f"/activities/{activity}/signup?email={test_email}")

    # Get count after signup
    response = client.get("/activities")
    after_signup = len(response.json()[activity]["participants"])

    # Delete
    response = client.delete(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 200
    assert f"Unregistered {test_email} from {activity}" in response.json()["message"]

    # Verify participant was removed
    response = client.get("/activities")
    after_delete = len(response.json()[activity]["participants"])
    assert after_delete == after_signup - 1
    assert test_email not in response.json()[activity]["participants"]


def test_delete_activity_not_found():
    """Test delete from non-existent activity"""
    response = client.delete("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_delete_not_signed_up():
    """Test delete when not signed up"""
    test_email = "not_signed@mergington.edu"
    activity = "Basketball Team"

    response = client.delete(f"/activities/{activity}/signup?email={test_email}")
    assert response.status_code == 400
    assert "Student is not signed up" in response.json()["detail"]