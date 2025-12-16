import pytest
from unittest.mock import Mock, AsyncMock

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
    async def test_create_order_product_price_changed(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1)
        mock_product_repo.get_by_id.return_value = Mock(
            id=1, name="Test Product", price=150.0, stock_quantity=10
        )

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
        assert result["total_amount"] == 300.0  # 2 * 150.0

    @pytest.mark.asyncio
    async def test_create_order_concurrent_stock_update(self):
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=1)
        mock_product_repo.get_by_id.return_value = Mock(
            id=1, name="Test Product", price=100.0, stock_quantity=1
        )
        mock_product_repo.update_stock.side_effect = Exception("Insufficient stock")

        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )

        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1}]
        }

        with pytest.raises(Exception, match="Insufficient stock"):
            await order_service.create_order(order_data)