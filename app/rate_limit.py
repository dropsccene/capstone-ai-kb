import time
import redis
import os
r = redis.Redis(
    host=os.getenv("REDIS_HOST","localhost"),
    port = int(os.getenv("REDIS_PORT","6379")),
    decode_responses = True
)




def check_rate_limit(ip:str,max_req:int=None,window_sec:int=None) -> bool:
    max_req = max_req or int(os.getenv("RATE_LIMIT_MAX_REQ","60"))
    window_sec = window_sec or int(os.getenv("RATE_LIMIT_WINDOW_SEC","60"))
    key = f"rate:{ip}"
    now = time.time()
    r.zremrangebyscore(key,0,now-window_sec)
    if r.zcard(key)>= max_req:
        return False
    r.zadd(key,{str(now):now})
    r.expire(key,window_sec)
    return True