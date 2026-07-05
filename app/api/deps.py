import asyncio
import logging
from datetime import datetime, timedelta
from typing import AsyncGenerator

from sqlalchemy import delete, make_url, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import settings
from app.models.screening import Application, Base, FuzzerRun, Job, Screening

_engine = None
async_session_maker = None
_reconnect_lock = asyncio.Lock()
logger = logging.getLogger(__name__)
_last_cleanup_day: int = -1


def _mask_url(url: str) -> str:
    """Mask both username and password in a URL for logging."""
    try:
        if "@" in url:
            left, right = url.split("@", 1)
            if "://" in left:
                scheme, auth = left.split("://", 1)
                if ":" in auth:
                    # Has both user and password
                    return f"{scheme}://****:****@{right}"
                else:
                    # Has only user, no password
                    return f"{scheme}://****@{right}"
        return url
    except Exception:
        return "***"


# Keep old name for backward compatibility
_mask_url_password = _mask_url


def normalize_db_url(db_url: str) -> tuple[str, dict]:
    """Normalize database URL for asyncpg.
    
    - Converts postgresql:// to postgresql+asyncpg://
    - Handles sslmode query param by converting to asyncpg connect_args
    """
    import ssl
    
    url = make_url(db_url)
    backend = url.get_backend_name()
    connect_args: dict = {}
    
    # Convert to asyncpg driver if needed
    if backend in ("postgres", "postgresql") and "+" not in url.drivername:
        url = url.set(drivername="postgresql+asyncpg")
    
    # Handle sslmode for asyncpg
    if url.drivername.endswith("+asyncpg"):
        query = dict(url.query) if hasattr(url.query, "items") else {}
        sslmode = query.pop("sslmode", None)
        
        if sslmode in ("require", "prefer", "verify-ca", "verify-full"):
            # asyncpg needs ssl=SSLContext, not a string
            ssl_context = ssl.create_default_context()
            if sslmode == "require":
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ssl_context
        
        # Remove query params from URL (asyncpg doesn't like them in URL)
        # Use _replace to completely remove query parameters
        if url.query:
            # Create new URL without query params
            url = url._replace(query=None)
            # SQLAlchemy URL uses _replace, need to verify it worked
            if url.query:
                # Fallback: manually clear
                url = make_url(str(url).split('?')[0])
    
    return url.render_as_string(hide_password=False), connect_args


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

        db_url = settings.database_url
        connect_args: dict = {}
        if db_url is not None:
            db_url, connect_args = normalize_db_url(db_url)

        try:
            engine_kwargs = dict(
                url=db_url,
                echo=settings.debug,
                pool_pre_ping=True,
                pool_recycle=1800,
            )
            if connect_args:
                engine_kwargs["connect_args"] = connect_args
            logger.info(
                "db_connect_attempt url=%s",
                _mask_url_password(str(engine_kwargs["url"])),
            )
            _engine = create_async_engine(**engine_kwargs)
            async_session_maker = async_sessionmaker(
                _engine, class_=AsyncSession, expire_on_commit=False
            )
            async with _engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("db_connection_ok url=%s", _mask_url_password(str(_engine.url)))
        except Exception as exc:
            logger.warning("db_reconnect_failed: %s", exc)
            await _dispose_engine()
            raise


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
                    Application.status.in_(
                        [
                            "rejected",
                            "screening_failed",
                            "withdrawn",
                        ]
                    ),
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
    session_maker = async_session_maker
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
