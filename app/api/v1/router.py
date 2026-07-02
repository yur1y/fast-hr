from fastapi import APIRouter

from app.api.v1.endpoints import fuzzer, health, screenings

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(screenings.router, prefix="/screenings", tags=["screenings"])
api_router.include_router(fuzzer.router, prefix="/fuzzer", tags=["fuzzer"])
