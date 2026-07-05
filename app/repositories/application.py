from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.screening import Application, Job


class ApplicationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, **kwargs: Any) -> Application:
        application = Application(**kwargs)
        self._session.add(application)
        await self._session.flush()
        await self._session.refresh(application)
        return application

    async def get_by_id(self, application_id: str) -> Application | None:
        result = await self._session.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    async def list_by_job(self, job_id: str, limit: int = 100) -> list[Application]:
        result = await self._session.execute(
            select(Application)
            .where(Application.job_id == job_id)
            .order_by(Application.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Application]:
        result = await self._session.execute(
            select(Application)
            .order_by(Application.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_aggregates(self) -> dict[str, Any]:
        total_jobs = await self._session.execute(select(func.count(Job.id)))
        active_jobs = await self._session.execute(
            select(func.count(Job.id)).where(Job.status == "active")
        )
        total_apps = await self._session.execute(select(func.count(Application.id)))
        return {
            "total_jobs": total_jobs.scalar_one(),
            "active_jobs": active_jobs.scalar_one(),
            "total_applications": total_apps.scalar_one(),
        }
