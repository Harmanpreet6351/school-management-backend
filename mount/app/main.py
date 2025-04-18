from fastapi import FastAPI

from app.exceptions import ExceptionHandlerMiddleware
from .router import api_router_v1

app_description = """
A FastAPI-powered backend for managing school financial operations, including budgeting, fee collection, staff salaries, and expense tracking. This system supports secure user roles, detailed financial reporting, and real-time updates to ensure transparency and efficiency in school finance workflows.
"""

app = FastAPI(
    title="School Management System API 🎟️", description=app_description
)


app.include_router(api_router_v1)


app.add_middleware(ExceptionHandlerMiddleware)


@app.get("/", tags=["Health"])
async def health_check():
    """
    Checks System health
    """
    return {"health": "ok"}
