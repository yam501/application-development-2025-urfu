import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from models import User, Address, Product, Order


async def seed_additional_data():
    """Асинхронная версия вашего seed_more_data.py"""
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:secret@localhost:5432/lr2_db")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        print("Добавляем дополнительные данные...")

        result = await session.execute(select(User))
        users = result.scalars().all()

        descriptions = [
            "Кассир пятерочки",
            "Настоящий пират",
            "Дантист",
            "Личный водитель",
            "Программист",
        ]

        for i, user in enumerate(users):
            if i < len(descriptions):
                user.description = descriptions[i]

        await session.commit()

        products_data = [
            {"name": "Ноутбук", "price": 120000.00, "description": "Мощный игровой ноутбук"},
            {"name": "Беспроводные наушники", "price": 6500.00, "description": "Шумоподавление"},
            {"name": "Футболка с бананом", "price": 3359.00, "description": "Хлопок, размер XXL"},
            {"name": "Библия", "price": 250.00, "description": "Хорошая книга"},
            {"name": "Кофемашина", "price": 18999.00, "description": "С капучинатором"},
        ]

        products = []
        for data in products_data:
            product = Product(name=data["name"], price=data["price"], description=data["description"])
            session.add(product)
            products.append(product)

        await session.commit()

        addresses_result = await session.execute(select(Address))
        addresses = addresses_result.scalars().all()

        for i in range(5):
            if i < len(users) and i < len(addresses) and i < len(products):
                order = Order(
                    user_id=users[i].id,
                    address_id=addresses[i].id,
                    product_id=products[i].id,
                    quantity=1,
                    status="pending"
                )
                session.add(order)

        await session.commit()
        print("Дополнительные данные добавлены!")


if __name__ == "__main__":
    asyncio.run(seed_additional_data())