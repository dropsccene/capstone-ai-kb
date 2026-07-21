from app.rate_limit import check_rate_limit
import redis
import os
r = redis.Redis(
    host=os.getenv("REDIS_HOST","localhost"),
    port = int(os.getenv("REDIS_PORT","6379")),
    decode_responses = True
)


def test_rate_limit_allows_up_to_max():
    r.delete(f"rate:127.0.0.1")
    for _ in range(4):
        assert check_rate_limit("127.0.0.1", max_req=5, window_sec=60) is True
    assert check_rate_limit("127.0.0.1", max_req=5, window_sec=60) is True
def test_rate_limit_blocks_over_max():
    r.delete(f"rate:127.0.0.1")
    for _ in range(5):
        assert check_rate_limit("127.0.0.1", max_req=5, window_sec=60) is True
    assert check_rate_limit("127.0.0.1", max_req=5, window_sec=60) is False