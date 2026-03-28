from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppException(Exception):

    def __init__(self, message: str, status_code: int = 400, details: Any | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            status_code=404,
        )



def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация обработчиков исключений."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message, "details": exc.details},
        )