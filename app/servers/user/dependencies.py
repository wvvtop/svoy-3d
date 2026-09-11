from typing import Annotated, AsyncGenerator
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from app.core.config import config
from app.database.dependencies import get_session
from app.database.models.user import User
from app.exceptions.auth import InactiveUserError, InvalidTokenError, TokenExpiredError
from app.repositories.user import get_user_by_id

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/api/auth/login"
# )
bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,
            algorithms=[config.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidTokenError()

        user_id = int(user_id)

    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise InvalidTokenError()

    user = await get_user_by_id(
        session=session,
        user_id=user_id,
    )

    if user is None:
        raise InvalidTokenError()

    if not user.is_active:
        raise InactiveUserError()

    return user

