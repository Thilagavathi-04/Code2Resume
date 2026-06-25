import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db: AsyncSession, user_data: UserCreate, hashed_password: str) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        github_url=user_data.github_url,
        github_token=user_data.github_token,
        linkedin_id=user_data.linkedin_id,
        leetcode_id=user_data.leetcode_id,
        mobile_number=user_data.mobile_number,
        avatar_url=user_data.avatar_url,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username, User.is_deleted == False))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email, User.is_deleted == False))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user: User, user_data: UserUpdate) -> User:
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


async def soft_delete_user(db: AsyncSession, user: User) -> User:
    user.is_deleted = True
    user.is_active = False
    await db.flush()
    await db.refresh(user)
    return user
