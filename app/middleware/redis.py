import redis
from config import settings


def get_redis_client():
    redis_client = redis.Redis.from_url(settings.REDIS_URI)
    return redis_client
