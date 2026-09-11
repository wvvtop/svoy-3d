from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.auth import AuthError


async def auth_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, AuthError):
        raise exc

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        },
    )