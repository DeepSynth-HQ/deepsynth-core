from .redis import get_redis_client
from redis import RedisError
from fastapi import HTTPException
from fastapi import status
from datetime import datetime as time
from functools import wraps
from fastapi import Request


class RateLimiter:
    def is_rate_limited(self, key: str, max_requests: int, window: int) -> bool:
        """
        Check if a request should be rate limited.

        Args:
            key: The unique identifier for the rate limit bucket
            max_requests: Maximum number of requests allowed in the window
            window: Time window in seconds

        Returns:
            bool: True if request should be rate limited, False otherwise

        Raises:
            HTTPException: If Redis operations fail
        """
        current = int(time.now().timestamp())
        window_start = current - window
        redis_conn = get_redis_client()

        with redis_conn.pipeline() as pipe:
            try:
                # First pipeline: Check current state
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                results = pipe.execute()

                current_count = results[1]

                # If not rate limited, add the new request
                if current_count < max_requests:
                    pipe.zadd(key, {current: current})
                    pipe.expire(key, window)
                    pipe.execute()
                    return False

                return True

            except RedisError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Redis error: {str(e)}",
                ) from e


rate_limiter = RateLimiter()


# decorator to check if the user is rate limited
def rate_limit(max_requests: int, window: int):
    def decorator(func):
        @wraps(func)
        def wrapper(request: Request, *args, **kwargs):
            key = f"rate_limit:{request.client.host}:{request.url.path}"
            if rate_limiter.is_rate_limited(key, max_requests, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
