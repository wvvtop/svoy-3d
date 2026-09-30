from typing import Annotated
from fastapi import Depends
from app.auth.dependencies import get_current_user_from_token
from app.database.models.user import User
from app.exceptions.auth import ForbiddenError
from app.schemas.enums.user_role import UserRole

async def get_current_admin(
    user: Annotated[
        User,
        Depends(get_current_user_from_token),
    ],
) -> User:
    if user.role != UserRole.ADMIN:
        raise ForbiddenError(
            message="Admin access required",
        )

    return user


CurrentAdmin = Annotated[
    User,
    Depends(get_current_admin),
]