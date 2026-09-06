import redis
import json
import hashlib


r = redis.Redis(host='localhost',port=6379,decode_responses=True)

class SimpleBloomFilter:
    def __init__(self,size=100):
        self.size = size
        self.bit_array = [0] * size
    def _hashes(self,key):
        h1 = int(hashlib.md5(key.encode()).hexdigest(),16) % self.size
        h2 = int(hashlib.sha1(key.encode()).hexdigest(),16) % self.size
        return h1,h2
    def add(self,key):
        for pos in self._hashes(key):
            self.bit_array[pos] = 1
    def might_contain(self,key):
        for pos in self._hashes(key):
            if self.bit_array[pos] == 0:
                return False
        return True
bloom = SimpleBloomFilter()


fake_db = {"1":"Alice","2":"Bob"}

for k in fake_db:
    bloom.add(f"{k}")

def get_user(user_id):
    key = f"user:{user_id}"

    cached = r.get(key)
    if cached:
        print(f"[缓存命中] {cached}")
        return cached
    if not bloom.might_contain(key):
        print(f"[布隆过滤器] {key} 不存在，直接返回 None")
        return None

    print("[缓存未命中] 查询数据库...")
    if user_id in fake_db:
        result = fake_db[user_id]
        r.setex(key,60,result)
        return result
    print(f"[穿透!] user:{user_id} 不存在")
    return None
get_user("1")   # 第一次 miss，之后命中
get_user("2")   # 第一次 miss，之后命中
get_user("999")   
get_user("999") # 再来一次，还是穿透