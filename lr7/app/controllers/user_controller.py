from typing import Optional
from uuid import UUID

from dto.user_dto import UserCreate, UserResponse, UsersResponse, UserUpdate
from litestar import Controller, delete, get, post, put
from litestar.enums import RequestEncodingType
from litestar.exceptions import NotFoundException
from litestar.params import Body
from services.user_service import UserService


class UserController(Controller):
    path = "/users"

    @get("/{user_id:uuid}")
    async def get_user_by_id(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> UserResponse:
        """Получить пользователя по ID"""
        user = await user_service.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @get()
    async def get_all_users(
        self,
        user_service: UserService,
        count: int = 10,
        page: int = 1,
        username: Optional[str] = None,
        email: Optional[str] = None,
    ) -> UsersResponse:
        """Получить список пользователей с пагинацией и общим количеством"""
        filters = {}
        if username:
            filters["username"] = username
        if email:
            filters["email"] = email

        users, total_count = await user_service.get_by_filter_with_count(
            count, page, **filters
        )

        total_pages = (total_count + count - 1) // count if count > 0 else 1

        return UsersResponse(
            users=[UserResponse.model_validate(user) for user in users],
            total_count=total_count,
            page=page,
            page_size=count,
            total_pages=total_pages,
        )

    @post()
    async def create_user(
        self,
        user_service: UserService,
        data: UserCreate,
    ) -> UserResponse:
        """Создать нового пользователя"""
        user = await user_service.create(data)
        return UserResponse.model_validate(user)

    @delete("/{user_id:uuid}")
    async def delete_user(
        self,
        user_service: UserService,
        user_id: UUID,
    ) -> None:
        """Удалить пользователя по ID"""
        await user_service.delete(user_id)

    @put("/{user_id:uuid}")
    async def update_user(
        self,
        user_service: UserService,
        user_id: UUID,
        data: UserUpdate = Body(media_type=RequestEncodingType.JSON),
    ) -> UserResponse:
        """Обновить пользователя по ID"""
        user = await user_service.update(user_id, data)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)
