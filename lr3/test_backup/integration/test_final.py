import pytest
from litestar.testing import TestClient
from app.main import app


class TestFinalAPI:
    def test_create_user_success(self):
        with TestClient(app=app) as client:
            user_data = {
                "username": "finaluser",
                "email": "final@example.com",
                "description": "Test user for final lab"
            }

            response = client.post("/users", json=user_data)
            assert response.status_code == 201

            data = response.json()
            assert data["username"] == "finaluser"
            assert data["email"] == "final@example.com"
            assert "id" in data

    def test_get_users_list(self):
        with TestClient(app=app) as client:
            response = client.get("/users")
            assert response.status_code == 200

            data = response.json()
            assert isinstance(data, list)

    def test_create_multiple_users(self):
        with TestClient(app=app) as client:
            users = [
                {"username": "user1", "email": "user1@example.com"},
                {"username": "user2", "email": "user2@example.com"},
                {"username": "user3", "email": "user3@example.com"}
            ]

            for user_data in users:
                response = client.post("/users", json=user_data)
                assert response.status_code == 201
                assert response.json()["username"] == user_data["username"]

    def test_get_nonexistent_user_404(self):
        with TestClient(app=app) as client:
            response = client.get("/users/00000000-0000-0000-0000-000000000000")
            assert response.status_code == 404

    def test_update_user(self):
        with TestClient(app=app) as client:

            create_data = {"username": "update_test", "email": "update@example.com"}
            create_response = client.post("/users", json=create_data)
            assert create_response.status_code == 201
            user_id = create_response.json()["id"]

            update_data = {"username": "updated_user", "description": "Updated via API"}
            update_response = client.put(f"/users/{user_id}", json=update_data)

            assert update_response.status_code == 200
            updated_user = update_response.json()
            assert updated_user["username"] == "updated_user"
            assert updated_user["description"] == "Updated via API"

    def test_delete_user(self):
        with TestClient(app=app) as client:
            create_data = {"username": "delete_test", "email": "delete@example.com"}
            create_response = client.post("/users", json=create_data)
            assert create_response.status_code == 201
            user_id = create_response.json()["id"]

            delete_response = client.delete(f"/users/{user_id}")
            assert delete_response.status_code == 204

            get_response = client.get(f"/users/{user_id}")
            assert get_response.status_code == 404