import time
from redis import Redis
from functools import wraps


redis_client = Redis("redis")


class RateLimitException(Exception):
    """Custom exception raised when rate limiter times out."""

    pass


def rate_limiter(
    identifier, max_per_second=10, max_per_minute=100, max_per_hour=1000, timeout=60
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Current timestamp in milliseconds
            start_time = int(time.time() * 1000)
            now = start_time

            # Time windows in milliseconds
            second_window = now - 1000
            minute_window = now - 60000
            hour_window = now - 3600000
            day_window = now - 86400000

            zset_key = f"rate_limiter:{identifier}"

            # Ensure old entries are cleaned up (remove entries older than 24 hours)
            redis_client.zremrangebyscore(zset_key, 0, day_window)

            while True:
                # Get counts within the relevant time windows
                requests_last_second = redis_client.zcount(zset_key, second_window, now)
                requests_last_minute = redis_client.zcount(zset_key, minute_window, now)
                requests_last_hour = redis_client.zcount(zset_key, hour_window, now)

                # Check rate limits
                if (
                    requests_last_second < max_per_second
                    and requests_last_minute < max_per_minute
                    and requests_last_hour < max_per_hour
                ):
                    # Add current timestamp to the ZSET
                    redis_client.zadd(zset_key, {now: now})
                    break  # Exit the loop if resources are available

                # Check timeout
                elapsed_time = (int(time.time() * 1000) - start_time) / 1000
                if elapsed_time > timeout:
                    return f"After waiting {timeout}s, the tool is still rate limited. Do not try again!"

                # Wait briefly before retrying
                time.sleep(0.5)
                now = int(time.time() * 1000)  # Update timestamp for next iteration

            # Proceed with the actual function
            return func(*args, **kwargs)

        return wrapper

    return decorator
