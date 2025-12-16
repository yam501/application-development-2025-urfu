from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    description: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID4
    username: str
    email: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UsersResponse(BaseModel):
    users: List[UserResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
