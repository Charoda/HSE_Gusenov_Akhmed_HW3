from app.database import engine, Base
from app.utils.redis_client import redis_client
from app.config import settings


def init_db():
    Base.metadata.create_all(bind=engine)


def init_redis():
    redis_client.init()


def init_app():
    init_db()
    init_redis()