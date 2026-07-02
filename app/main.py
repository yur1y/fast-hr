from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import init_db
from app.api.v1.router import api_router
from app.clients.observability_factory import observability
from app.config import settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    yield
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

    return app


app = create_app()
