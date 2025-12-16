import pytest
from unittest.mock import Mock, AsyncMock
from app.services.order_service import OrderService
from uuid import uuid4


class TestOrderService:
    @pytest.mark.asyncio
    async def test_create_order_success(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1, email="test@example.com")
        mock_product_repo.get_by_id.return_value = Mock(
            id=1, name="Test Product", price=100.0, stock_quantity=5
        )

        mock_order = Mock()
        mock_order.id = uuid4()
        mock_order.user_id = 1
        mock_order.total_amount = 200.0
        mock_order.status = "pending"

        mock_order_repo.create.return_value = mock_order

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2}]
        }

        result = await order_service.create_order(order_data)

        assert result is not None
        assert result.total_amount == 200.0
        mock_order_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1)
        mock_product_repo.get_by_id.return_value = Mock(
            id=1, name="Test Product", price=100.0, stock_quantity=1
        )

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 5}]
        }

        with pytest.raises(ValueError, match="Insufficient stock"):
            await order_service.create_order(order_data)


class TestOrderServiceEdgeCases:

    @pytest.mark.asyncio
    async def test_create_order_zero_quantity(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1)
        mock_product_repo.get_by_id.return_value = Mock(
            id=1, name="Test Product", price=100.0, stock_quantity=10
        )

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 0}]
        }

        with pytest.raises(ValueError, match="Quantity must be positive"):
            await order_service.create_order(order_data)

    @pytest.mark.asyncio
    async def test_create_order_negative_quantity(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1)
        mock_product = Mock()
        mock_product.stock_quantity = 10
        mock_product.price = 100.0
        mock_product.name = "Test Product"
        mock_product_repo.get_by_id.return_value = mock_product

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": -5}]
        }

        with pytest.raises(ValueError, match="Quantity must be positive"):
            await order_service.create_order(order_data)

    @pytest.mark.asyncio
    async def test_create_order_empty_items(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1)

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        order_data = {
            "user_id": 1,
            "items": []
        }

        with pytest.raises(ValueError, match="Order must contain at least one item"):
            await order_service.create_order(order_data)

    @pytest.mark.asyncio
    async def test_create_order_concurrent_stock_update(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1)
        mock_product = Mock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.price = 100.0
        mock_product.stock_quantity = 1

        mock_product_repo.get_by_id.return_value = mock_product

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2}]
        }

        with pytest.raises(ValueError, match="Insufficient stock"):
            await order_service.create_order(order_data)

class TestOrderStatusEmail:
    @pytest.mark.asyncio
    async def test_order_status_shipped_sends_email(self):
        mock_order_repo = AsyncMock()
        mock_email_service = AsyncMock()

        mock_user = Mock()
        mock_user.email = "customer@example.com"
        mock_user.username = "testuser"

        mock_order = Mock()
        mock_order.id = 1
        mock_order.user_id = 1
        mock_order.status = "pending"
        mock_order.user = mock_user

        mock_updated_order = Mock()
        mock_updated_order.id = 1
        mock_updated_order.status = "shipped"

        mock_order_repo.get_by_id.return_value = mock_order
        mock_order_repo.update_status.return_value = mock_updated_order
        mock_email_service.send_order_shipped.return_value = True

        order_service = OrderService(
            order_repository=mock_order_repo,
            email_service=mock_email_service
        )

        result = await order_service.update_order_status(1, "shipped")

        assert result.status == "shipped"

        mock_order_repo.get_by_id.assert_called_once_with(1)
        mock_order_repo.update_status.assert_called_once_with(1, "shipped")
        mock_email_service.send_order_shipped.assert_called_once_with(
            email="customer@example.com",
            order_id=1,
            username="testuser"
        )

    @pytest.mark.asyncio
    async def test_order_status_shipped_email_failure(self):
        # Создаем моки
        mock_order_repo = AsyncMock()
        mock_email_service = AsyncMock()

        mock_user = Mock()
        mock_user.email = "customer@example.com"
        mock_user.username = "testuser"

        mock_order = Mock()
        mock_order.id = 1
        mock_order.user_id = 1
        mock_order.status = "pending"
        mock_order.user = mock_user

        mock_updated_order = Mock()
        mock_updated_order.id = 1
        mock_updated_order.status = "shipped"

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
        mock_order_repo.get_by_id.assert_called_once_with(1)
        mock_order_repo.update_status.assert_called_once_with(1, "shipped")

    @pytest.mark.asyncio
    async def test_order_status_other_no_email(self):
        mock_order_repo = AsyncMock()
        mock_email_service = AsyncMock()

        mock_user = Mock()
        mock_user.email = "customer@example.com"
        mock_user.username = "testuser"

        mock_order = Mock()
        mock_order.id = 1
        mock_order.user_id = 1
        mock_order.status = "pending"
        mock_order.user = mock_user

        mock_updated_order = Mock()
        mock_updated_order.id = 1
        mock_updated_order.status = "processing"

        mock_order_repo.get_by_id.return_value = mock_order
        mock_order_repo.update_status.return_value = mock_updated_order

        order_service = OrderService(
            order_repository=mock_order_repo,
            email_service=mock_email_service
        )

        result = await order_service.update_order_status(1, "processing")

        assert result.status == "processing"
        mock_email_service.send_order_shipped.assert_not_called()