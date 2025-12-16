import pytest
from app.repositories.order_repository import OrderRepository
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.models import User, Product, Address

class TestOrderRepository:
    @pytest.mark.asyncio
    async def test_create_order_with_products(self, order_repository: OrderRepository, user_repository: UserRepository, product_repository: ProductRepository, session):
        user = await user_repository.create(
            email="order_user@example.com",
            username="order_user"
        )

        address = Address(
            user_id=user.id,
            street="Test Street",
            city="Test City",
            country="Test Country"
        )
        session.add(address)
        await session.commit()
        await session.refresh(address)

        product1 = await product_repository.create(
            name="Product 1",
            price=100.0,
            stock_quantity=10
        )

        product_items = [
            {"product_id": product1.id, "quantity": 2, "price_at_time": 100.0}
        ]

        order = await order_repository.create(
            user_id=user.id,
            address_id=address.id,
            product_items=product_items,
            total_amount=200.0
        )

        assert order.id is not None
        assert order.user_id == user.id
        assert order.total_amount == 200.0

    @pytest.mark.asyncio
    async def test_get_order_by_id(self, order_repository: OrderRepository, user_repository: UserRepository, session):
        """Тест получения заказа по ID"""
        user = await user_repository.create(email="test@example.com", username="testuser")

        address = Address(user_id=user.id, street="S", city="C", country="Co")
        session.add(address)
        await session.commit()
        await session.refresh(address)

        order = await order_repository.create(
            user_id=user.id,
            address_id=address.id,
            product_items=[],
            total_amount=0
        )

        found_order = await order_repository.get_by_id(order.id)

        assert found_order is not None
        assert found_order.id == order.id

    @pytest.mark.asyncio
    async def test_update_order_status(self, order_repository: OrderRepository, user_repository: UserRepository, session):
        user = await user_repository.create(email="status@example.com", username="statususer")

        address = Address(user_id=user.id, street="S", city="C", country="Co")
        session.add(address)
        await session.commit()
        await session.refresh(address)

        order = await order_repository.create(
            user_id=user.id,
            address_id=address.id,
            product_items=[],
            total_amount=0
        )

        updated_order = await order_repository.update_status(order.id, "completed")

        assert updated_order.status == "completed"

    @pytest.mark.asyncio
    async def test_get_orders_by_user_id(self, order_repository: OrderRepository, user_repository: UserRepository, session):
        user = await user_repository.create(email="multi@example.com", username="multiuser")

        address = Address(user_id=user.id, street="S", city="C", country="Co")
        session.add(address)
        await session.commit()
        await session.refresh(address)

        await order_repository.create(user_id=user.id, address_id=address.id, product_items=[], total_amount=100)

        user_orders = await order_repository.get_by_user_id(user.id)

        assert len(user_orders) >= 1
        assert all(order.user_id == user.id for order in user_orders)

    @pytest.mark.asyncio
    async def test_delete_order(self, order_repository: OrderRepository, user_repository: UserRepository, session):
        user = await user_repository.create(email="delete@example.com", username="deleteuser")

        address = Address(user_id=user.id, street="S", city="C", country="Co")
        session.add(address)
        await session.commit()
        await session.refresh(address)

        order = await order_repository.create(
            user_id=user.id,
            address_id=address.id,
            product_items=[],
            total_amount=150.0
        )

        await order_repository.delete(order.id)

        deleted_order = await order_repository.get_by_id(order.id)
        assert deleted_order is None

    @pytest.mark.asyncio
    async def test_get_all_orders(self, order_repository: OrderRepository, user_repository: UserRepository, session):
        user = await user_repository.create(email="all@example.com", username="alluser")

        address = Address(user_id=user.id, street="S", city="C", country="Co")
        session.add(address)
        await session.commit()
        await session.refresh(address)

        await order_repository.create(user_id=user.id, address_id=address.id, product_items=[], total_amount=100)

        orders = await order_repository.get_all()

        assert len(orders) >= 1