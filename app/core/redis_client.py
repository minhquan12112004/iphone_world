import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        self.redis = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.aclose()

redis_client = RedisClient()

async def get_redis() -> redis.Redis:
    if redis_client.redis is None:
        await redis_client.connect()
    return redis_client.redis
