"""Application entrypoint / composition root.

A single factory wires the app together: logging, middleware, routers and the
domain-exception handlers. Optionally it also bootstraps a local SQLite database
and serves a built SPA, so the whole app can run as one process without Docker.
"""
import os
import bcrypt
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from feedback_app.controllers import (
    auth_controller,
    employee_controller,
    category_controller,
    comment_controller,
    idea_bank_controller,
    idea_controller,
    wall_controller,
    leaderboard_controller,
    manual_author_controller,
)
from feedback_app.controllers.error_handlers import register_error_handlers
from feedback_app.core.config import settings
from feedback_app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)
_write_requests: dict[str, deque[float]] = defaultdict(deque)
_WRITE_WINDOW_SECONDS = 60
_WRITE_MAX_REQUESTS = 12


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
    api.include_router(category_controller.router)
    api.include_router(comment_controller.router)
    api.include_router(idea_bank_controller.router)
    api.include_router(manual_author_controller.router)
    return api


def _bootstrap_local_database() -> None:
    """On non-PostgreSQL engines (local SQLite), create tables and seed an admin.

    On PostgreSQL this is a no-op: schema is owned by Alembic migrations.
    """
    from feedback_app.core.database import Base, SessionLocal, engine
    from feedback_app.models.idea import Idea
    from feedback_app.models.reaction import IdeaReaction
    from feedback_app.models.category import IdeaCategory
    from feedback_app.models.comment import IdeaComment
    from feedback_app.models.user import User
    from feedback_app.models.manual_author import ManualAuthor

    if not settings.database_url.startswith("postgresql"):
        logger.info("Local mode: ensuring SQLite schema")
        Base.metadata.create_all(engine)
    with SessionLocal() as session:
        exists = session.query(User).filter_by(login=settings.admin_login).first() if settings.admin_login else None
        if exists is None and settings.admin_login and settings.admin_password:
            session.add(User(login=settings.admin_login, password_hash=bcrypt.hashpw(settings.admin_password.encode(), bcrypt.gensalt()).decode()))
            session.commit()
            logger.info("Seeded configured admin")


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

    @app.middleware("http")
    async def request_size_limit(request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            length = request.headers.get("content-length")
            if length and int(length) > settings.request_max_bytes:
                return JSONResponse(status_code=413, content={"detail": "Слишком большой запрос."})
        if request.method == "POST" and request.url.path.startswith("/api/") and request.url.path != "/api/auth/login":
            ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "unknown")
            now = time.monotonic(); history = _write_requests[ip]
            while history and now - history[0] > _WRITE_WINDOW_SECONDS: history.popleft()
            if len(history) >= _WRITE_MAX_REQUESTS:
                return JSONResponse(status_code=429, content={"detail": "Слишком много отправок. Попробуйте через минуту."})
            history.append(now)
        return await call_next(request)

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
