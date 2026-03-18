import redis
from redis.exceptions import RedisError
from app.config import settings
from typing import Optional, Any
import json
import pickle


class RedisClient:
    def __init__(self):
        self._client = None

    def init(self):
        self._client = redis.from_url(settings.REDIS_URL, decode_responses=False)

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self._client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except (RedisError, pickle.PickleError):
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            serialized = pickle.dumps(value)
            if ttl:
                return self._client.setex(key, ttl, serialized) == 1
            return self._client.set(key, serialized) == 1
        except (RedisError, pickle.PickleError):
            return False

    def delete(self, key: str) -> bool:
        try:
            return self._client.delete(key) > 0
        except RedisError:
            return False

    def exists(self, key: str) -> bool:
        try:
            return self._client.exists(key) > 0
        except RedisError:
            return False

    def clear_pattern(self, pattern: str) -> int:
        try:
            keys = self._client.keys(pattern)
            if keys:
                return self._client.delete(*keys)
            return 0
        except RedisError:
            return 0


redis_client = RedisClient()