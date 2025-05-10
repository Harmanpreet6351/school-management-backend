from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database.core import get_db_engine
from app.exceptions import init_exception_middlewares
from app.middlewares import init_middlewares
from .router import api_router_v1

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

init_exception_middlewares(app)

init_middlewares(app)

app.include_router(api_router_v1)


@app.get("/", tags=["Health"])
async def health_check():
    """
    Checks System health
    """
    return {"health": "ok"}
