import time
import redis
import os

_r = None
_redis_available = None


def get_redis():
    """获取共享 Redis 连接，Redis 不可用时返回 None（不崩溃）"""
    global _r, _redis_available
    if _redis_available is None:
        try:
            _r = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                decode_responses=True,
                socket_connect_timeout=1,
            )
            _r.ping()
            _redis_available = True
        except (redis.ConnectionError, redis.TimeoutError):
            _r = None
            _redis_available = False
    return _r


def check_rate_limit(ip: str, max_req: int = None, window_sec: int = None) -> bool:
    r = get_redis()
    if r is None:
        return True  # Redis 不可用时放行，不阻塞功能
    max_req = max_req or int(os.getenv("RATE_LIMIT_MAX_REQ", "60"))
    window_sec = window_sec or int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
    key = f"rate:{ip}"
    now = time.time()
    r.zremrangebyscore(key, 0, now - window_sec)
    if r.zcard(key) >= max_req:
        return False
    r.zadd(key, {str(now): now})
    r.expire(key, window_sec)
    return True
