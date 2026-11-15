from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password, verify_password, create_access_token
from app.database.models.user import User
from app.exceptions.auth import EmailAlreadyExistsError, PermissionDeniedError, UserNotFoundError, \
InvalidCredentialsError, InactiveUserError
from app.repositories.user import create_user, get_user_by_email
from app.schemas.enums.user_role import UserRole


async def register_user(
    session: AsyncSession,
    email: str,
    password: str
) -> User:
    """Сервис для регистрации пользователя (User)"""
    existing_user = await get_user_by_email(session, email)

    if existing_user:
        raise EmailAlreadyExistsError()

    password_hash = hash_password(password)

    user = await create_user(session=session, email=email,password_hash=password_hash)

    return user

async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User:
    """Сервис аутентификации пользователя (User)"""
    user = await get_user_by_email(session, email)

    if user is None:
        raise InvalidCredentialsError()

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()

    if not user.is_active:
        raise InactiveUserError()

    return user

async def login_user(session: AsyncSession, email: str, password: str) -> str:
    user = await authenticate_user(session, email, password)
    access_token = create_access_token(user.id, user.email)
    return access_token

async def login_admin(
    session: AsyncSession,
    email: str,
    password: str
) -> str:
    """Получение токена авторизации админстратора с проверкой роли пользователя"""
    user = await authenticate_user(session, email, password)

    if user.role != UserRole.ADMIN:
        raise PermissionDeniedError()

    access_token = create_access_token(user.id, user.email)

    return access_token