from dto.user_dto import UserCreate, UserUpdate
from typing import List, Tuple
from uuid import UUID
from models import User
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def get_by_filter_with_count(self, count: int = 10, page: int = 1, **kwargs) -> Tuple[List[User], int]:
        return await self.user_repository.get_by_filter_with_count(count, page, **kwargs)

    # Остальные методы остаются без изменений
    async def create(self, user_data: UserCreate) -> User:
        return await self.user_repository.create(user_data)

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        return await self.user_repository.update(user_id, user_data)

    async def delete(self, user_id: UUID) -> None:
        await self.user_repository.delete(user_id)