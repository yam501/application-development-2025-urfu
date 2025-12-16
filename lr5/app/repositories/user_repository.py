from typing import List, Tuple
from uuid import UUID

from dto.user_dto import UserCreate, UserUpdate
from models import User
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_filter_with_count(
        self, count: int = 10, page: int = 1, **kwargs
    ) -> Tuple[List[User], int]:

        stmt = select(User)

        if "username" in kwargs and kwargs["username"]:
            stmt = stmt.where(User.username.ilike(f"%{kwargs['username']}%"))
        if "email" in kwargs and kwargs["email"]:
            stmt = stmt.where(User.email.ilike(f"%{kwargs['email']}%"))

        offset = (page - 1) * count
        stmt = stmt.offset(offset).limit(count)

        result = await self.session.execute(stmt)
        users = result.scalars().all()

        count_stmt = select(func.count(User.id))

        if "username" in kwargs and kwargs["username"]:
            count_stmt = count_stmt.where(
                User.username.ilike(f"%{kwargs['username']}%")
            )
        if "email" in kwargs and kwargs["email"]:
            count_stmt = count_stmt.where(User.email.ilike(f"%{kwargs['email']}%"))

        total_result = await self.session.execute(count_stmt)
        total_count = total_result.scalar_one()

        return users, total_count

    async def create(self, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            description=user_data.description,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
