from contextlib import asynccontextmanager
from fastapi import FastAPI, status

from app.api.dependencies import CurrentUserDep
from app.database.core import get_db_engine
from app.core.middlewares import init_middlewares, init_exception_middlewares
from app.api import api_router
from app.schemas.base_schema import ErrorResponseModel

app_description = """
A FastAPI-powered backend for managing school financial operations, including budgeting, fee collection, staff salaries, and expense tracking. This system supports secure user roles, detailed financial reporting, and real-time updates to ensure transparency and efficiency in school finance workflows.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = get_db_engine()
    yield
    await app.state.db_pool.dispose()

app = FastAPI(
    title="School Management System API 🎟️", description=app_description, lifespan=lifespan
)

default_responses: dict = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ErrorResponseModel,
        "description": "Unprocessable Entity"
    },
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorResponseModel,
        "description": "Bad Request"
    }
}

init_exception_middlewares(app)

init_middlewares(app)

app.include_router(api_router, responses=default_responses)


@app.get("/", tags=["Health"])
async def health_check():
    """
    Checks System health
    """
    return {"health": "ok"}
