from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Order, order_product_association
from typing import List
from uuid import UUID
from pydantic import ConfigDict

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: UUID) -> Order | None:
        stmt = select(Order).where(Order.id == order_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        stmt = select(Order).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_user_id(self, user_id: UUID) -> List[Order]:
        stmt = select(Order).where(Order.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, user_id: UUID, address_id: UUID, product_items: List[dict],
                     total_amount: float = 0) -> Order:
        order = Order(
            user_id=user_id,
            address_id=address_id,
            total_amount=total_amount
        )
        self.session.add(order)
        await self.session.flush()

        for item in product_items:
            stmt = order_product_association.insert().values(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price_at_time=item.get('price_at_time', 0)
            )
            await self.session.execute(stmt)

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update_status(self, order_id: UUID, status: str) -> Order:
        order = await self.get_by_id(order_id)
        if order:
            order.status = status
            await self.session.commit()
            await self.session.refresh(order)
        return order

    async def delete(self, order_id: UUID) -> None:
        order = await self.get_by_id(order_id)
        if order:
            delete_stmt = order_product_association.delete().where(
                order_product_association.c.order_id == order_id
            )
            await self.session.execute(delete_stmt)
            await self.session.delete(order)
            await self.session.commit()