from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core import logger
from app.exceptions.base_exception import AppBaseException

def init_middlewares(app: FastAPI):
    """
    Initialize all middlewares
    NOTE: All middlewares will run in order from top to bottom

    Args:
        app (FastAPI): FastAPI app instance
    """

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        logger.info(f"{request.method} {request.url}")
        response = await call_next(request)
        return response
    

def init_exception_middlewares(app: FastAPI):
    """
    Initialize all exceptions handler
    NOTE: All handlers will run in order from top to bottom

    Args:
        app (FastAPI): FastAPI app instance
    """

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(request: Request, exc: RequestValidationError):
        """
        Exception Handler for FastAPI Request Validations

        Args:
            request (Request): FastAPI/Starllete Request Object
            exc (HTTPException): FastAPI HTTPException

        Returns:
            JSONResponse: Response with error data
        """
        logger.exception("Invalid Request Body", exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "detail": exc.args
                }
            }
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        """
        Exception Handler for FastAPI HTTPExceptions

        Args:
            request (Request): FastAPI/Starllete Request Object
            exc (HTTPException): FastAPI HTTPException

        Returns:
            JSONResponse: Response with error data
        """
        logger.exception("Custom Exceptions", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_EXCEPTION",
                    "detail": exc.detail
                }
            }
        )

    @app.exception_handler(AppBaseException)
    async def handle_base_exception(request: Request, exc: AppBaseException):
        """
        Exception Handler for Custom Exceptions

        Args:
            request (Request): FastAPI/Starllete Request Object
            exc (HTTPException): FastAPI HTTPException

        Returns:
            JSONResponse: Response with error data
        """
        logger.exception("App Exception", exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "detail": exc.detail
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def handle_unhandled_exception(request: Request, exc: Exception):
        """
        Exception Handler for unhandled exceptions

        Args:
            request (Request): FastAPI/Starllete Request Object
            exc (HTTPException): FastAPI HTTPException

        Returns:
            JSONResponse: Response with error data
        """
        logger.exception("Unhandled exception", exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "UNHANDLED_EXCEPTION",
                    "detail": str(exc)
                }
            }
        )