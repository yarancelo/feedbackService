"""Application entrypoint / composition root.

A single factory wires the app together: logging, middleware, routers and the
domain-exception handlers. Optionally it also bootstraps a local SQLite database
and serves a built SPA, so the whole app can run as one process without Docker.
"""
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from feedback_app.controllers import (
    auth_controller,
    employee_controller,
    idea_controller,
    wall_controller,
    leaderboard_controller,
    manual_author_controller,
)
from feedback_app.controllers.error_handlers import register_error_handlers
from feedback_app.core.config import settings
from feedback_app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


def _build_api_router() -> APIRouter:
    """Compose all controllers under the /api prefix."""
    api = APIRouter(prefix="/api")

    @api.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok"}

    api.include_router(auth_controller.router)
    api.include_router(idea_controller.router)
    api.include_router(wall_controller.router)
    api.include_router(leaderboard_controller.router)
    api.include_router(employee_controller.router)
    api.include_router(manual_author_controller.router)
    return api


def _bootstrap_local_database() -> None:
    """On non-PostgreSQL engines (local SQLite), create tables and seed an admin.

    On PostgreSQL this is a no-op: schema is owned by Alembic migrations.
    """
    if settings.database_url.startswith("postgresql"):
        return

    from feedback_app.core.database import Base, SessionLocal, engine
    from feedback_app.models.idea import Idea
    from feedback_app.models.reaction import IdeaReaction
    from feedback_app.models.user import User
    from feedback_app.models.manual_author import ManualAuthor

    logger.info("Local mode: ensuring SQLite schema and seed admin")
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        exists = session.query(User).filter_by(login="admin").first()
        if exists is None:
            session.add(User(login="admin", password="password"))
            session.commit()
            logger.info("Seeded default admin (admin/password)")


def _mount_spa(app: FastAPI, static_dir: str) -> None:
    """Serve a built SPA: static assets + index.html fallback for client routes."""
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    index_file = os.path.join(static_dir, "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(index_file)

    logger.info("Serving SPA from %s", static_dir)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    configure_logging(settings.log_level)
    logger.info("Starting Anonymous Feedback API")

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        _bootstrap_local_database()
        yield

    app = FastAPI(title="Anonymous Feedback API", version="2.0.0", lifespan=lifespan)

    # Permissive CORS: internal tool, backend also reachable directly on :8080.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(_build_api_router())

    if settings.serve_static_dir and os.path.isdir(settings.serve_static_dir):
        _mount_spa(app, settings.serve_static_dir)

    return app


app = create_app()
