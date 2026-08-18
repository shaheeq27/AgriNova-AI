"""
AgriNova AI — Rate Limiter.

Phase 9: Production-grade Redis-backed sliding window rate limiter,
with a fallback to in-process memory for local development.
Includes fail-closed behavior on Redis failure and a global backstop.
"""

import time
import logging
from collections import defaultdict

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.exceptions import AgriNovaException

logger = logging.getLogger(__name__)


class AIRateLimitException(AgriNovaException):
    """User has exceeded the AI chat rate limit."""
    def __init__(self, is_global: bool = False) -> None:
        if is_global:
            message = "Global AI capacity reached. Please try again in a few minutes."
        else:
            message = (
                f"Rate limit exceeded. You can send up to "
                f"{settings.AI_RATE_LIMIT_MAX_REQUESTS} messages per "
                f"{settings.AI_RATE_LIMIT_WINDOW_SECONDS} seconds. "
                f"Please wait and try again."
            )
        super().__init__(message=message, status_code=429)


class AILimiterUnavailableException(AgriNovaException):
    """Redis is unavailable; failing closed."""
    def __init__(self) -> None:
        super().__init__(
            message="AI service is temporarily unavailable. Please try again later.",
            status_code=503,
        )


class RateLimiter:
    """Production rate limiter with Redis backing and local fallback."""

    def __init__(self) -> None:
        self.max_requests = settings.AI_RATE_LIMIT_MAX_REQUESTS
        self.window_seconds = settings.AI_RATE_LIMIT_WINDOW_SECONDS
        self.global_max_requests = settings.AI_GLOBAL_RATE_LIMIT_MAX_REQUESTS
        self.global_window_seconds = settings.AI_GLOBAL_RATE_LIMIT_WINDOW_SECONDS
        
        self.use_redis = not settings.is_sqlite and settings.APP_ENV != "development"
        
        if self.use_redis:
            # We use decode_responses=True so we get strings back, though we only check counts here.
            self.redis_client: Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Initialized Redis Rate Limiter.")
        else:
            self._requests: dict[str, list[float]] = defaultdict(list)
            self._global_requests: list[float] = []
            logger.info("Initialized In-Process Rate Limiter (Local Dev).")

    async def check(self, user_id: str, ip_address: str | None = None) -> None:
        """Check both per-user and global rate limits."""
        if self.use_redis:
            await self._check_redis(user_id, ip_address)
        else:
            self._check_in_process(user_id, ip_address)

    async def _check_redis(self, user_id: str, ip_address: str | None) -> None:
        now = time.time()
        user_key = f"rate_limit:user:{user_id}"
        global_key = "rate_limit:global:ai"

        try:
            # Check global backstop first
            async with self.redis_client.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(global_key, 0, now - self.global_window_seconds)
                pipe.zadd(global_key, {str(now): now})
                pipe.zcard(global_key)
                pipe.expire(global_key, self.global_window_seconds)
                _, _, global_count, _ = await pipe.execute()
                
            if global_count > self.global_max_requests:
                logger.warning("Global AI rate limit exceeded.")
                raise AIRateLimitException(is_global=True)

            # Check per-user limit
            async with self.redis_client.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(user_key, 0, now - self.window_seconds)
                pipe.zadd(user_key, {str(now): now})
                pipe.zcard(user_key)
                pipe.expire(user_key, self.window_seconds)
                _, _, user_count, _ = await pipe.execute()

            if user_count > self.max_requests:
                logger.info("User %s exceeded AI rate limit.", user_id)
                raise AIRateLimitException(is_global=False)

        except AIRateLimitException:
            raise
        except RedisError as e:
            logger.error("Redis rate limiter failed: %s. Failing closed.", e)
            raise AILimiterUnavailableException()

    def _check_in_process(self, user_id: str, ip_address: str | None) -> None:
        now = time.time()
        global_window_start = now - self.global_window_seconds
        user_window_start = now - self.window_seconds

        # Prune and check global
        self._global_requests = [ts for ts in self._global_requests if ts > global_window_start]
        if len(self._global_requests) >= self.global_max_requests:
            raise AIRateLimitException(is_global=True)

        # Prune and check user
        self._requests[user_id] = [ts for ts in self._requests[user_id] if ts > user_window_start]
        if len(self._requests[user_id]) >= self.max_requests:
            raise AIRateLimitException(is_global=False)

        self._global_requests.append(now)
        self._requests[user_id].append(now)


# Module-level singleton
ai_rate_limiter = RateLimiter()
