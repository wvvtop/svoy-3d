from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def get_session(
        request: Request
) -> AsyncGenerator[AsyncSession, None]:
    """Функция-зависимость для получения сессии базы данных"""
    session_factory = request.app.state.session_factory

    async with session_factory() as session:
        yield session