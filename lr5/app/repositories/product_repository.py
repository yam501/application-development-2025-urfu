from typing import Any, Dict, List, Optional
from uuid import UUID

from models import Product
from pydantic import ConfigDict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: UUID) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        stmt = select(Product).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(
        self, name: str, price: float, description: str = None, stock_quantity: int = 0
    ) -> Product:
        product = Product(
            name=name,
            price=price,
            description=description,
            stock_quantity=stock_quantity,
        )
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product_id: UUID, **kwargs) -> Product:
        product = await self.get_by_id(product_id)
        if not product:
            return None

        for field, value in kwargs.items():
            if hasattr(product, field):
                setattr(product, field, value)

        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product_id: UUID) -> None:
        product = await self.get_by_id(product_id)
        if product:
            await self.session.delete(product)
            await self.session.commit()

    async def update_stock(self, product_id: UUID, quantity: int) -> Product:
        product = await self.get_by_id(product_id)
        if product:
            product.stock_quantity = quantity
            await self.session.commit()
            await self.session.refresh(product)
        return product

    async def get_paginated(
        self, page: int = 1, page_size: int = 10, category: Optional[str] = None
    ) -> Dict[str, Any]:
        offset = (page - 1) * page_size

        query = select(Product)

        if category:
            query = query.where(Product.category == category)

        products_query = query.offset(offset).limit(page_size)
        result = await self.session.execute(products_query)
        items = result.scalars().all()

        count_query = select(func.count()).select_from(Product)
        if category:
            count_query = count_query.where(Product.category == category)

        total_result = await self.session.execute(count_query)
        total_items = total_result.scalar()

        total_pages = (total_items + page_size - 1) // page_size

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_items": total_items,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
