from unittest.mock import patch, AsyncMock
import redis
import os

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


@patch("app.routers.asks.call_llm", new_callable=AsyncMock)
@patch("app.routers.asks.VectorStore")
def test_ask(mock_vectorstore, mock_call_llm, client):
    r.delete("ask:1:答案是啥")
    mock_vectorstore.return_value.query = AsyncMock(return_value=["资料片段1", "资料片段2"])
    mock_call_llm.return_value = "根据资料，答案是42"
    response = client.post("/knowledge-bases/1/ask", json={"question": "答案是啥"})
    assert response.status_code == 200
    assert response.json()["answer"] == "根据资料，答案是42"
    assert response.json()["sources"] == ["资料片段1", "资料片段2"]


@patch("app.routers.asks.call_llm", new_callable=AsyncMock)
@patch("app.routers.asks.VectorStore")
def test_ask_cache_hit(mock_vectorstore, mock_call_llm, client):
    r.delete("ask:1:答案是啥")
    r.set("ask:1:吃了吗", "吃饱了", ex=60)
    response = client.post("/knowledge-bases/1/ask", json={"question": "吃了吗"})
    assert response.json()["answer"] == "吃饱了"
    assert response.json()["sources"] == []


@patch("app.routers.asks.VectorStore")
def test_ask_rate_limited(mock_vectorstore, client, monkeypatch):
    # 钉住限流值：asks.py 现在读 RATE_LIMIT_MAX_REQ（.env 里配的是 60），
    # 测试要固定语义，不能跟着 .env 走
    monkeypatch.setenv("RATE_LIMIT_MAX_REQ", "5")
    mock_vectorstore.return_value.query = AsyncMock(return_value=["片段"])
    r.delete("rate:testclient")
    for _ in range(5):
        client.post("/knowledge-bases/1/ask", json={"question": "刷子测试"})
    response = client.post("/knowledge-bases/1/ask", json={"question": "刷子测试"})
    assert response.status_code == 429
