from redis import StrictRedis
from src.conf.config import settings

redis = StrictRedis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_blacklist_db,
    decode_responses=True,
)
