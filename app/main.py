"""TaskFlow API — main application entry point."""

import logging

from fastapi import FastAPI

from app.database import init_db
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routes import projects, tasks, users, workflows

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="TaskFlow API",
    description="A task management API for teams",
    version="0.1.0",
)

# Middleware
app.add_middleware(RequestLoggerMiddleware)

# Routes
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
