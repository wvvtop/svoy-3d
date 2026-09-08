from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request


async def get_db(
        request: Request
) -> AsyncGenerator[AsyncSession, None]:
    """Функция-зависимость для получения сессии базы данных"""
    session_factory = request.app.state.session_factory

    async with session_factory() as session:
        yield session