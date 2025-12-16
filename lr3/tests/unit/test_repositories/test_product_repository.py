import pytest
from decimal import Decimal
from app.repositories.product_repository import ProductRepository
from app.models import Product

class TestProductRepository:
    @pytest.mark.asyncio
    async def test_create_product(self, product_repository: ProductRepository):
        product_data = {
            "name": "Test Product",
            "price": 99.99,
            "description": "Test description",
            "stock_quantity": 10
        }
        product = await product_repository.create(**product_data)

        assert product.id is not None
        assert product.name == "Test Product"
        assert product.price == Decimal('99.99')
        assert product.stock_quantity == 10

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, product_repository: ProductRepository):
        product = await product_repository.create(
            name="Unique Product",
            price=50.0,
            stock_quantity=5
        )

        found_product = await product_repository.get_by_id(product.id)

        assert found_product is not None
        assert found_product.id == product.id
        assert found_product.name == "Unique Product"
        assert found_product.price == Decimal('50.0')

    @pytest.mark.asyncio
    async def test_update_product(self, product_repository: ProductRepository):
        product = await product_repository.create(
            name="Original Product",
            price=100.0,
            stock_quantity=10
        )

        updated_product = await product_repository.update(
            product.id,
            name="Updated Product",
            price=150.0
        )

        assert updated_product.name == "Updated Product"
        assert updated_product.price == Decimal('150.0')
        assert updated_product.stock_quantity == 10

    @pytest.mark.asyncio
    async def test_update_stock(self, product_repository: ProductRepository):
        product = await product_repository.create(
            name="Stock Product",
            price=75.0,
            stock_quantity=20
        )

        updated_product = await product_repository.update_stock(product.id, 15)

        assert updated_product.stock_quantity == 15

    @pytest.mark.asyncio
    async def test_delete_product(self, product_repository: ProductRepository):
        product = await product_repository.create(
            name="To Delete",
            price=25.0,
            stock_quantity=3
        )

        await product_repository.delete(product.id)

        deleted_product = await product_repository.get_by_id(product.id)
        assert deleted_product is None

    @pytest.mark.asyncio
    async def test_get_all_products(self, product_repository: ProductRepository):
        await product_repository.create(name="Product 1", price=10.0, stock_quantity=5)
        await product_repository.create(name="Product 2", price=20.0, stock_quantity=8)

        products = await product_repository.get_all()

        assert len(products) >= 2
        assert any(product.name == "Product 1" for product in products)
        assert any(product.name == "Product 2" for product in products)