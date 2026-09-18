"""Rate limiting middleware using Redis"""
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        exempt_paths: Optional[list] = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.exempt_paths = exempt_paths or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next):
        if not REDIS_AVAILABLE:
            return await call_next(request)

        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        current_time = int(time.time())

        minute_key = f"ratelimit:{client_ip}:{current_time // 60}"
        hour_key = f"ratelimit:{client_ip}:{current_time // 3600}"

        try:
            pipe = redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 120)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 7200)
            results = pipe.execute()

            minute_count = results[0]
            hour_count = results[2]

            if minute_count > self.requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute",
                    headers={"Retry-After": "60"},
                )

            if hour_count > self.requests_per_hour:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour",
                    headers={"Retry-After": "3600"},
                )

            response = await call_next(request)
            response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, self.requests_per_minute - minute_count))
            response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
            response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, self.requests_per_hour - hour_count))

            return response

        except HTTPException:
            raise
        except Exception:
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class SlidingWindowRateLimiter:
    def __init__(self, redis_client, key_prefix: str = "ratelimit:sw"):
        self.redis = redis_client
        self.key_prefix = key_prefix

    async def is_allowed(self, identifier: str, limit: int, window_seconds: int) -> tuple[bool, dict]:
        current_time = time.time()
        key = f"{self.key_prefix}:{identifier}"

        try:
            pipe = self.redis.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - window_seconds)
            pipe.zcard(key)
            pipe.zadd(key, {str(current_time): current_time})
            pipe.expire(key, window_seconds + 1)
            results = pipe.execute()

            current_count = results[1]
            allowed = current_count < limit

            return allowed, {
                "limit": limit,
                "remaining": max(0, limit - current_count - 1),
                "reset": int(current_time + window_seconds),
            }
        except Exception:
            return True, {"limit": limit, "remaining": limit, "reset": int(current_time + window_seconds)}