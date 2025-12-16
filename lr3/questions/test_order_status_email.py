import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.order_service import OrderService
from app.services.email_service import EmailService

class TestOrderStatusEmail:
    @pytest.mark.asyncio
    async def test_order_status_shipped_sends_email(self):
        mock_order_repo = AsyncMock()
        mock_email_service = AsyncMock()

        mock_order = Mock(
            id=1,
            user_id=1,
            status="pending",
            user=Mock(email="customer@example.com", username="testuser")
        )
        mock_updated_order = Mock(
            id=1,
            user_id=1,
            status="shipped",
            user=Mock(email="customer@example.com", username="testuser")
        )

        mock_order_repo.get_by_id.return_value = mock_order
        mock_order_repo.update_status.return_value = mock_updated_order
        mock_email_service.send_order_shipped.return_value = True

        order_service = OrderService(
            order_repository=mock_order_repo,
            email_service=mock_email_service
        )

        result = await order_service.update_order_status(1, "shipped")

        assert result.status == "shipped"

        mock_email_service.send_order_shipped.assert_called_once_with(
            email="customer@example.com",
            order_id=1,
            username="testuser"
        )

    @pytest.mark.asyncio
    async def test_order_status_other_no_email(self):
        mock_order_repo = AsyncMock()
        mock_email_service = AsyncMock()

        mock_order = Mock(id=1, user_id=1, status="pending")
        mock_updated_order = Mock(id=1, user_id=1, status="processing")

        mock_order_repo.get_by_id.return_value = mock_order
        mock_order_repo.update_status.return_value = mock_updated_order

        order_service = OrderService(
            order_repository=mock_order_repo,
            email_service=mock_email_service
        )

        result = await order_service.update_order_status(1, "processing")

        assert result.status == "processing"

        mock_email_service.send_order_shipped.assert_not_called()

    @pytest.mark.asyncio
    async def test_order_status_shipped_email_failure(self):
        mock_order_repo = AsyncMock()
        mock_email_service = AsyncMock()

        mock_order = Mock(
            id=1,
            user_id=1,
            status="pending",
            user=Mock(email="customer@example.com", username="testuser")
        )
        mock_updated_order = Mock(
            id=1,
            user_id=1,
            status="shipped",
            user=Mock(email="customer@example.com", username="testuser")
        )

        mock_order_repo.get_by_id.return_value = mock_order
        mock_order_repo.update_status.return_value = mock_updated_order
        mock_email_service.send_order_shipped.side_effect = Exception("SMTP error")

        order_service = OrderService(
            order_repository=mock_order_repo,
            email_service=mock_email_service
        )

        result = await order_service.update_order_status(1, "shipped")

        assert result.status == "shipped"
        mock_email_service.send_order_shipped.assert_called_once()