import redis
import json
import logging

logger = logging.getLogger(__name__)

_redis_pool = None


def get_redis(config) -> redis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD,
            db=config.REDIS_DB,
            decode_responses=True,
            max_connections=10,
        )
    return redis.Redis(connection_pool=_redis_pool)


def save_and_publish(r: redis.Redis, channel: str, hash_key: str,
                     symbol: str, price: str, event_time: int):
    """写入 Redis 缓存 + 发布到 Pub/Sub 频道"""
    value = json.dumps({
        "symbol": symbol,
        "price": price,
        "time": event_time,
    })
    try:
        pipe = r.pipeline()
        pipe.hset(hash_key, symbol, value)
        pipe.publish(channel, value)
        pipe.execute()
    except Exception as e:
        logger.error("Redis 写入失败 [%s %s]: %s", channel, symbol, e)
