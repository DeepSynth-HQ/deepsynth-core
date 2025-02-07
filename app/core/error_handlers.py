from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from .exceptions import AppException, ErrorCode


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "extra": exc.extra,
        },
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    error_message = str(exc.orig)
    if "ix_users_email" in error_message:
        return JSONResponse(
            status_code=409,
            content={
                "error_code": ErrorCode.DUPLICATE_EMAIL,
                "message": "Email address already exists",
                "extra": {"field": "email"},
            },
        )
    elif "ix_users_username" in error_message:
        return JSONResponse(
            status_code=409,
            content={
                "error_code": ErrorCode.DUPLICATE_USERNAME,
                "message": "Username already exists",
                "extra": {"field": "username"},
            },
        )
    return JSONResponse(
        status_code=409,
        content={
            "error_code": ErrorCode.DATABASE_ERROR,
            "message": "Database constraint violation",
            "extra": {"original_error": str(exc.orig)},
        },
    )
