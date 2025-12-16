import pytest
from unittest.mock import Mock, AsyncMock
from app.services.user_service import UserService
from app.dto.user_dto import UserCreate
from uuid import uuid4

class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user_success(self):
        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = Mock(
            id=uuid4(), username="testuser", email="test@example.com"
        )

        user_service = UserService(user_repository=mock_user_repo)

        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            description="Test user"
        )

        result = await user_service.create(user_data)

        assert result is not None
        assert result.username == "testuser"
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self):
        mock_user_repo = AsyncMock()
        mock_user_repo.get_by_email.return_value = Mock(email="existing@example.com")

        user_service = UserService(user_repository=mock_user_repo)

        user_data = UserCreate(
            username="newuser",
            email="existing@example.com",
            description="Test user"
        )

        with pytest.raises(ValueError, match="already exists"):
            await user_service.create(user_data)