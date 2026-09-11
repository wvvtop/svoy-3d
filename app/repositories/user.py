from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Метод для получения user по email"""
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

async def get_user_by_id(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    """Метод для получения user по id"""

    result = await session.execute(
        select(User).where(
            User.id == user_id
        )
    )

    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    email: str,
    password_hash: str,
) -> User:
    """Метод создания user в базе данных"""
    user = User(
        email=email,
        password_hash=password_hash,
    )

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user