import redis
import time
import random
from cachetools import TTLCache

r = redis.Redis(host='localhost',port=6379,decode_responses=True)

local_cache = TTLCache(maxsize=100,ttl=10)

fake_db = {f"item:{i}":f"数据{i}" for i in range(10)}

def get_item(item_id):
    key = f"item:{item_id}"

    if key in local_cache:
        print(f"[L1本地命中] {key}")
        return local_cache[key]
    cached = r.get(key)
    if cached:
        print(f"[L3 redis命中] {key}")
        local_cache[key] = cached
        return cached
    print(f"[L3 查数据库] {key}")
    if item_id in fake_db:
        result = fake_db[item_id]
        ttl = 30 + random.randint(0,10)
        r.set(key,result,ex=ttl)
        local_cache[key] = result
        return result
    print(f"[L3 穿透] {key} 不存在")
    return None


get_item("item:1")   # 第一次 miss，之后命中
get_item("item:1")   # 第二次命中本地缓存
get_item("item:5")
get_item("item:5")