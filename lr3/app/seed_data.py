import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import User, Address, Product, Order


async def seed_initial_data():
    """Асинхронная версия вашего seed_data.py"""
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:123@localhost:5432/lr2_db")
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(User))
        existing_users = result.scalars().all()

        if existing_users:
            print(f"В базе уже есть {len(existing_users)} пользователей")
            return

        print("Добавляем начальные данные...")

        users_data = [
            {"username": "mikhail_ryzhov", "email": "m.ryzhov@mail.net"},
            {"username": "clare_davis", "email": "clare.d@inbox.org"},
            {"username": "kenji_tanaka", "email": "k.tanaka@global.jp"},
            {"username": "fatima_nkosi", "email": "fatima.nkosi@africa.co.za"},
            {"username": "lucas_fernandez", "email": "lucasf@correo.es"},
        ]

        users = []
        for data in users_data:
            user = User(username=data["username"], email=data["email"])
            session.add(user)
            users.append(user)

        await session.commit()

        addresses_data = [
            {"user_id": users[0].id, "street": "7 Sunset Boulevard", "city": "Sydney", "country": "Australia"},
            {"user_id": users[1].id, "street": "45 Canal Street", "city": "Amsterdam", "country": "Netherlands"},
            {"user_id": users[2].id, "street": "18 Nevsky Prospect", "city": "Saint Petersburg", "country": "Russia"},
            {"user_id": users[3].id, "street": "99 Queen Street", "city": "Toronto", "country": "Canada"},
            {"user_id": users[4].id, "street": "3 Al-Rashid Street", "city": "Dubai", "country": "United Arab Emirates"},
        ]

        for data in addresses_data:
            address = Address(
                user_id=data["user_id"],
                street=data["street"],
                city=data["city"],
                country=data["country"]
            )
            session.add(address)

        await session.commit()
        print("Начальные данные добавлены!")


if __name__ == "__main__":
    asyncio.run(seed_initial_data())