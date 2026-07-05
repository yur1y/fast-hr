from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.screening import Job


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self, limit: int = 50, offset: int = 0) -> list[Job]:
        result = await self._session.execute(
            select(Job)
            .where(Job.status == "active")
            .order_by(Job.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(self, job_id: str) -> Job | None:
        result = await self._session.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs: Any) -> Job:
        job = Job(**kwargs)
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[Job]:
        result = await self._session.execute(
            select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
