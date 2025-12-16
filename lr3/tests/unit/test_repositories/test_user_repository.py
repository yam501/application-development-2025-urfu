import pytest
from app.repositories.user_repository import UserRepository

class TestUserRepository:

    @pytest.mark.asyncio
    async def test_create_user(self, user_repository: UserRepository):
        user = await user_repository.create(
            username="john_doe",
            email="test@example.com",
            description="Test user"
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "john_doe"

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_repository: UserRepository):
        user = await user_repository.create(
            email="unique@example.com",
            username="user_test",
            description="Test user"
        )

        found_user = await user_repository.get_by_email("unique@example.com")

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "unique@example.com"

    @pytest.mark.asyncio
    async def test_update_user(self, user_repository: UserRepository):
        user = await user_repository.create(
            email="update@example.com",
            username="test",
            description="Original"
        )

        updated_user = await user_repository.update(
            user.id,
            {"username": "updated_username"}
        )

        assert updated_user.username == "updated_username"
        assert updated_user.email == "update@example.com"

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository: UserRepository):
        user = await user_repository.create(
            email="delete@example.com",
            username="to_delete",
            description="To be deleted"
        )

        await user_repository.delete(user.id)

        deleted_user = await user_repository.get_by_id(user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, user_repository: UserRepository):
        await user_repository.create(email="user1@example.com", username="user1")
        await user_repository.create(email="user2@example.com", username="user2")

        users = await user_repository.get_all()

        assert len(users) >= 2