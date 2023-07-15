import redis.asyncio as redis

from settings import Settings, get_settings

_settings = get_settings(Settings)


async def get_redis_connection() -> redis.Redis:
    return redis.Redis.from_url(str(_settings.redis_url), decode_responses=True)
