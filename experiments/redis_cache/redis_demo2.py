import redis
import time
import threading

r = redis.Redis(host='localhost',port=6379,decode_responses=True)

fake_db = {"hot" : "这是一个热点数据"}
def get_hot_data():
    key = "hot_data"

    cached = r.get(key)
    if cached:
        return f"[缓存命中] {cached}"
    lock_key = f"{key}:lock"
    got_lock = r.set(lock_key,"1",nx=True,ex=5)
    if got_lock:
        print(f"[{threading.current_thread().name}] 获取到锁，查询数据库...")
        time.sleep(1)
        result = fake_db["hot"]
        r.setex(key,30,result)
        r.delete(lock_key)
        return f"[重建成功] {result}"

    else:
        print(f"[{threading.current_thread().name}] 没有获取到锁，等待...")
        time.sleep(0.5)
        cached = r.get(key)
        return f"[等到了] {cached}"

threads = []
for i in range(5):
    t = threading.Thread(target=get_hot_data,name=f"请求{i}")
    threads.append(t)
    t.start()

for t in threads:
    t.join()