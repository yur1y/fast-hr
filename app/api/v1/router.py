from fastapi import APIRouter

from app.api.v1.endpoints import admin, careers, fuzzer, health, hr, screenings, tasks

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(screenings.router, prefix="/screenings", tags=["screenings"])
api_router.include_router(fuzzer.router, prefix="/fuzzer", tags=["fuzzer"])
api_router.include_router(hr.router, prefix="/hr", tags=["hr"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(careers.router, prefix="/careers", tags=["careers"])

api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
