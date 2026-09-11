from fastapi import status

class AuthError(Exception):
    """Базовый класс ошибок аутентифиации"""
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_error"
    message = "Authentication failed"
    pass


# Authentication
class AuthenticationError(AuthError):
    """Не удалось установить личность пользователя."""
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_error"
    message = "Authentication failed"


class InvalidCredentialsError(AuthenticationError):
    """
    Неверная пара email/пароль.

    ВАЖНО: намеренно не разделяем на "неверный email" и "неверный пароль",
    чтобы не давать возможности перебирать существующих пользователей
    (user enumeration).
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "invalid_credentials"
    message = "Invalid email or password"


class InvalidTokenError(AuthenticationError):
    """Токен отсутствует, повреждён, подделан или невалиден."""
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "invalid_token"
    message = "Invalid or malformed token"


class TokenExpiredError(InvalidTokenError):
    """
    Токен был валиден, но истёк.

    Наследуемся от InvalidTokenError, потому что для клиента это тот же
    кейс "перелогинься", но код другой — удобно для фронта и для метрик.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "token_expired"
    message = "Token has expired"


class UserNotFoundError(AuthenticationError):
    """
    Пользователь не найден.

    Используется, например, при запросе профиля по токену, если юзер
    был удалён, или при /password-reset для несуществующего email
    (если хотим явно сообщить — обычно НЕ хотим, см. комментарий выше).
    """
    status_code = status.HTTP_404_NOT_FOUND
    code = "user_not_found"
    message = "User not found"


class EmailAlreadyExistsError(AuthenticationError):
    """
    Попытка регистрации на уже занятый email.

    409 Conflict, а не 401 — это не про "кто ты", а про конфликт
    состояния ресурса. Но логически относится к auth-флоу (регистрация),
    поэтому живёт в этой ветке.
    """
    status_code = status.HTTP_409_CONFLICT
    code = "email_already_exists"
    message = "User with this email already exists"



# Authorization
class AuthorizationError(AuthError):
    """Личность установлена, но прав на действие нет."""
    status_code = status.HTTP_403_FORBIDDEN
    code = "authorization_error"
    message = "You don't have permission to perform this action"


class InactiveUserError(AuthorizationError):
    """
    Пользователь аутентифицирован, но аккаунт деактивирован/забанен.

    Не 401 — потому что токен валиден, дело именно в статусе аккаунта.
    """
    status_code = status.HTTP_403_FORBIDDEN
    code = "inactive_user"
    message = "User account is inactive"


class PermissionDeniedError(AuthorizationError):
    """
    Общий случай: у пользователя нет нужной роли/скоупа/права.

    Используй, когда не подходит более специфичный класс
    (например, NotOwnerError).
    """
    status_code = status.HTTP_403_FORBIDDEN
    code = "permission_denied"
    message = "Permission denied"


class NotOwnerError(AuthorizationError):
    """
    Ресурс существует и в целом доступен, но принадлежит другому юзеру.

    Часто используется для DELETE/PATCH "своих" сущностей.

    NB: некоторые API намеренно возвращают 404 вместо 403, чтобы не
    раскрывать существование чужих ресурсов. Тогда лучше кидать
    UserNotFoundError-подобное или отдельный ResourceNotFoundError.
    """
    status_code = status.HTTP_403_FORBIDDEN
    code = "not_owner"
    message = "You are not the owner of this resource"




