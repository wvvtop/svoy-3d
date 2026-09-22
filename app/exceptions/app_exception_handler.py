from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.app_exception import AppError

async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, AppError):
        raise exc
    content = {
        "error": {
            "code": exc.code,
            "message": exc.message,
        }
    }

    if exc.details:
        content["error"] = exc.details

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )