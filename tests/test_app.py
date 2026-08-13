"""
Tests for Mergington High School Activities API

Tests cover all endpoints with happy path and error scenarios.
Uses TestClient with fresh activity data per test via pytest fixtures.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Provides a fresh copy of activities data for each test.
    
    This fixture:
    - Creates a deep copy of the original activities
    - Monkeypatches the app's activities to use test data
    - Ensures complete isolation between tests (no cross-test pollution)
    """
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Practice teamwork and compete in interscholastic soccer matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swim laps, improve technique, and train for swim meets",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Society": {
            "description": "Rehearse performances and study theater production",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 20,
            "participants": ["sophia@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "logan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice public speaking and compete in debate tournaments",
            "schedule": "Wednesdays and Fridays, 4:30 PM - 6:00 PM",
            "max_participants": 14,
            "participants": ["oliver@mergington.edu", "emma@mergington.edu"]
        }
    }
    
    # Deep copy to ensure complete isolation
    test_activities = deepcopy(original_activities)
    
    # Monkeypatch the app's activities with test data
    monkeypatch.setattr("src.app.activities", test_activities)
    
    return test_activities


@pytest.fixture
def client():
    """Provides TestClient for making requests to the app."""
    return TestClient(app)


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """Verify GET /activities returns all activities with correct structure."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all activities are returned
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_response_structure(self, client, fresh_activities):
        """Verify activities have required fields: description, schedule, max_participants, participants."""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_participant_data(self, client, fresh_activities):
        """Verify participant lists are correct."""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        # Gym Class should have 2 participants
        assert len(data["Gym Class"]["participants"]) == 2
        assert "john@mergington.edu" in data["Gym Class"]["participants"]
    
    def test_root_redirect(self, client):
        """Verify GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, fresh_activities):
        """Happy path: Successfully sign up a new participant."""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
    
    def test_signup_adds_participant_to_list(self, client, fresh_activities):
        """Verify participant is added to the activity's participant list."""
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # Verify participant not in list before signup
        assert email not in fresh_activities["Chess Club"]["participants"]
        
        # Sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Verify participant is now in list
        assert email in fresh_activities["Chess Club"]["participants"]
        assert len(fresh_activities["Chess Club"]["participants"]) == 3
    
    def test_signup_invalid_email_format(self, client, fresh_activities):
        """Error case: Invalid email format should still be accepted by API (no email validation enforced)."""
        # Note: The API doesn't enforce email format validation, so we test with a basic string
        # This could be enhanced with Pydantic EmailStr for stricter validation
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "invalid-email"}
        )
        
        # API accepts any string as email
        assert response.status_code == 200
    
    def test_signup_activity_not_found(self, client, fresh_activities):
        """Error case: Signing up for non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self, client, fresh_activities):
        """Error case: Registering same email twice returns 400."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is already signed up for this activity"
    
    def test_signup_different_activities(self, client, fresh_activities):
        """Verify same student can sign up for multiple different activities."""
        email = "newstudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        assert email in fresh_activities["Chess Club"]["participants"]
        assert email in fresh_activities["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_unregister_success(self, client, fresh_activities):
        """Happy path: Successfully unregister a participant."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
    
    def test_unregister_removes_participant(self, client, fresh_activities):
        """Verify participant is removed from the activity's list."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify participant is in list before unregister
        assert email in fresh_activities["Chess Club"]["participants"]
        initial_count = len(fresh_activities["Chess Club"]["participants"])
        
        # Unregister
        client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Verify participant is removed
        assert email not in fresh_activities["Chess Club"]["participants"]
        assert len(fresh_activities["Chess Club"]["participants"]) == initial_count - 1
    
    def test_unregister_activity_not_found(self, client, fresh_activities):
        """Error case: Unregistering from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/participants/student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_email_not_registered(self, client, fresh_activities):
        """Error case: Unregistering email not in participants returns 400."""
        response = client.delete(
            "/activities/Chess Club/participants/notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
    
    def test_unregister_already_unregistered(self, client, fresh_activities):
        """Error case: Unregistering same participant twice returns 400 on second attempt."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response1 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student is not signed up for this activity"
