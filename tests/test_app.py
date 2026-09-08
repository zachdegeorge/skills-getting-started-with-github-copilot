from src.app import activities


class TestRoot:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestActivities:
    def test_get_activities_returns_activity_details(self, client):
        # Arrange
        expected_activity_names = set(activities)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        returned_activities = response.json()
        assert set(returned_activities) == expected_activity_names
        for activity in returned_activities.values():
            assert set(activity) == {
                "description",
                "schedule",
                "max_participants",
                "participants",
            }
            assert isinstance(activity["participants"], list)


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }
        assert email in activities[activity_name]["participants"]

    def test_signup_for_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Activity"
        email = "new.student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_participant_returns_bad_request(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Student already signed up for this activity"
        )

    def test_signup_without_email_returns_validation_error(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup")

        # Assert
        assert response.status_code == 422


class TestUnregister:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity_name}"
        }
        assert email not in activities[activity_name]["participants"]

    def test_unregister_from_unknown_activity_returns_not_found(self, client):
        # Arrange
        activity_name = "Unknown Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_non_participant_returns_bad_request(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "not.registered@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Student is not signed up for this activity"
        )

    def test_unregister_without_email_returns_validation_error(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity_name}/unregister")

        # Assert
        assert response.status_code == 422
