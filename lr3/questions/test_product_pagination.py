import pytest
from app.repositories.product_repository import ProductRepository

class TestProductPagination:
    @pytest.mark.asyncio
    async def test_get_products_pagination(self, product_repository: ProductRepository):
        for i in range(15):
            await product_repository.create(
                name=f"Product {i}",
                price=10.0 * (i + 1),
                stock_quantity=i
            )

        page_1 = await product_repository.get_paginated(page=1, page_size=5)
        page_2 = await product_repository.get_paginated(page=2, page_size=5)
        page_3 = await product_repository.get_paginated(page=3, page_size=5)

        assert len(page_1["items"]) == 5
        assert page_1["page"] == 1
        assert page_1["page_size"] == 5
        assert page_1["total_pages"] == 3
        assert page_1["total_items"] == 15
        assert page_1["has_next"] == True
        assert page_1["has_prev"] == False

        assert len(page_2["items"]) == 5
        assert page_2["page"] == 2
        assert page_2["has_next"] == True
        assert page_2["has_prev"] == True

        assert len(page_3["items"]) == 5
        assert page_3["page"] == 3
        assert page_3["has_next"] == False
        assert page_3["has_prev"] == True

    @pytest.mark.asyncio
    async def test_pagination_edge_cases(self, product_repository: ProductRepository):
        empty_page = await product_repository.get_paginated(page=1, page_size=10)
        assert len(empty_page["items"]) == 0
        assert empty_page["total_pages"] == 0
        assert empty_page["total_items"] == 0

        for i in range(5):
            await product_repository.create(
                name=f"Product {i}",
                price=10.0,
                stock_quantity=5
            )

        out_of_range = await product_repository.get_paginated(page=10, page_size=5)
        assert len(out_of_range["items"]) == 0
        assert out_of_range["page"] == 10

        page_size_3 = await product_repository.get_paginated(page=1, page_size=3)
        assert len(page_size_3["items"]) == 3
        assert page_size_3["total_pages"] == 2

        page_size_10 = await product_repository.get_paginated(page=1, page_size=10)
        assert len(page_size_10["items"]) == 5
        assert page_size_10["total_pages"] == 1

    @pytest.mark.asyncio
    async def test_pagination_with_filters(self, product_repository: ProductRepository):
        categories = ["electronics", "clothing", "electronics", "books", "electronics"]
        for i, category in enumerate(categories):
            await product_repository.create(
                name=f"Product {i}",
                price=10.0 * (i + 1),
                stock_quantity=5,
                category=category
            )

        filtered_page = await product_repository.get_paginated(
            page=1,
            page_size=2,
            category="electronics"
        )

        assert len(filtered_page["items"]) == 2
        assert filtered_page["total_items"] == 3
        assert all(item.category == "electronics" for item in filtered_page["items"])