from contextlib import asynccontextmanager
import asyncio
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.deps import init_db, db_reconnect_loop
from app.api.v1.router import api_router
from app.clients.observability_factory import observability
from app.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.core.redis import redis_reconnect_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    stop_event = asyncio.Event()
    db_task = asyncio.create_task(db_reconnect_loop(stop_event))
    redis_task = asyncio.create_task(redis_reconnect_loop(stop_event))
    await init_db()
    yield
    stop_event.set()
    for task in (db_task, redis_task):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    observability.flush()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI Screening Observability Platform with Langfuse tracing",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_middleware(app)
    app.include_router(api_router, prefix=settings.api_v1_str)

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": settings.app_version}

    BASE_DIR = Path(__file__).resolve().parent.parent
    FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

    assets_dir = str(FRONTEND_DIST / "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        if full_path.startswith(("api/", "health", "assets/")):
            return {"detail": "Not found"}
        index_path = FRONTEND_DIST / "index.html"
        if not index_path.exists():
            return {"detail": "Frontend not built"}
        return FileResponse(str(index_path))

    return app


app = create_app()
