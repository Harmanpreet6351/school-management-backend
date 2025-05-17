from fastapi import FastAPI, Request
from app import logger

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