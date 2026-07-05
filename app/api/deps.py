import asyncio
import logging
from datetime import datetime, timedelta
from typing import AsyncGenerator

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import text, delete

from app.config import settings
from app.models.screening import Application, Base, FuzzerRun, Job, Screening

_engine = None
async_session_maker = None
_reconnect_lock = asyncio.Lock()
logger = logging.getLogger(__name__)
_last_cleanup_day: int = -1


def _get_engine():
    return _engine, async_session_maker


async def _dispose_engine():
    global _engine, async_session_maker
    if _engine is not None:
        try:
            await _engine.dispose()
        except Exception as exc:
            logger.warning("db_dispose_failed: %s", exc)
        _engine = None
        async_session_maker = None


async def _ensure_db_connection() -> None:
    global _engine, async_session_maker
    if settings.database_url is None:
        return
    async with _reconnect_lock:
        engine, _ = _engine, async_session_maker
        if engine is not None:
            try:
                async with engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                return
            except Exception:
                await _dispose_engine()

        from sqlalchemy.ext.asyncio import create_async_engine

        try:
            _engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                pool_pre_ping=True,
                pool_recycle=1800,
            )
            async_session_maker = async_sessionmaker(
                _engine, class_=AsyncSession, expire_on_commit=False
            )
            async with _engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("db_connection_ok url=%s", _engine.url)
        except Exception as exc:
            logger.warning("db_reconnect_failed: %s", exc)
            await _dispose_engine()


async def _run_cleanup() -> None:
    global _last_cleanup_day
    if _engine is None or async_session_maker is None:
        return
    today = datetime.utcnow().date().toordinal()
    if today == _last_cleanup_day:
        return
    _last_cleanup_day = today

    retention = timedelta(days=settings.cleanup_retention_days)
    cutoff = datetime.utcnow() - retention

    async with async_session_maker() as session:
        try:
            await session.execute(
                delete(Application).where(
                    Application.created_at < cutoff,
                    Application.status.in_(["rejected", "screening_failed", "withdrawn"]),
                )
            )
            await session.execute(
                delete(Screening).where(
                    Screening.created_at < cutoff,
                )
            )
            await session.execute(
                delete(Job).where(
                    Job.status == "closed",
                    Job.closed_at < cutoff,
                )
            )
            await session.execute(
                delete(FuzzerRun).where(
                    FuzzerRun.created_at < cutoff,
                )
            )
            await session.commit()
            logger.info("db_cleanup_ok cutoff=%s", cutoff.isoformat())
        except Exception as exc:
            await session.rollback()
            logger.warning("db_cleanup_failed: %s", exc)


async def db_reconnect_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await _ensure_db_connection()
            await _run_cleanup()
        except Exception as exc:
            logger.warning("db_reconnect_loop_error: %s", exc)
        await asyncio.sleep(60)


async def init_db() -> None:
    await _ensure_db_connection()
    if _engine is None:
        logging.getLogger(__name__).warning("init_db_skipped db_unavailable")
        return
    try:
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        logging.getLogger(__name__).warning("init_db_failed: %s", exc)
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    engine, session_maker = _engine, async_session_maker
    if session_maker is None:
        yield None
        return
    try:
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except DBAPIError:
                await session.rollback()
                await _dispose_engine()
                raise
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    except Exception:
        if settings.database_url is not None:
            await _ensure_db_connection()
        raise


def get_settings():
    from app.config import settings

    return settings
