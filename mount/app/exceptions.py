from typing import Awaitable, Callable
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class HTTPExceptionResponseModel(BaseModel):
    detail: str


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            response = await call_next(request)
        except Exception as e:
            response = JSONResponse(status_code=500, content={"msg": str(e)})

        return response
