from __future__ import annotations

import asyncio
import logging
import time

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import settings

logger = logging.getLogger(__name__)

_redis: Redis | None = None
_redis_available: bool = False
_last_check: float = 0.0
_CHECK_INTERVAL: int = 60
_lock = asyncio.Lock()


async def get_redis() -> Redis | None:
    if not _redis_available and time.time() - _last_check >= _CHECK_INTERVAL:
        await _ensure_redis_connection()
    return _redis


async def is_redis_available() -> bool:
    return _redis_available


async def _ensure_redis_connection() -> None:
    global _redis, _redis_available, _last_check
    async with _lock:
        if _redis_available:
            return
        try:
            if _redis is None:
                _redis = Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                )
            await _redis.ping()
            _redis_available = True
            _last_check = time.time()
            logger.info("redis_connection_ok url=%s", settings.redis_url)
        except Exception as exc:
            logger.warning("redis_connection_failed: %s", exc)
            _redis_available = False
            _last_check = time.time()
            if _redis is not None:
                try:
                    await _redis.aclose()
                except Exception:
                    pass
                _redis = None


async def _dispose_redis() -> None:
    global _redis, _redis_available
    if _redis is not None:
        try:
            await _redis.aclose()
        except Exception as exc:
            logger.warning("redis_dispose_failed: %s", exc)
        finally:
            _redis = None
            _redis_available = False


async def redis_reconnect_loop(stop_event: asyncio.Event) -> None:
    while not stop_event.is_set():
        try:
            await _ensure_redis_connection()
        except Exception as exc:
            logger.warning("redis_reconnect_loop_error: %s", exc)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=_CHECK_INTERVAL)
        except asyncio.TimeoutError:
            pass
