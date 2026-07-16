from unittest.mock import patch

@patch("app.routers.asks.call_llm")
@patch("app.routers.asks.VectorStore")
def test_ask(mock_vectorstore,mock_call_llm,client):
    mock_vectorstore.return_value.query.return_value = ["资料片段1","资料片段2"]
    mock_call_llm.return_value = "根据资料，答案是42"
    response = client.post("/knowledge-bases/1/ask",json={"question":"答案是啥"})
    assert response.status_code == 200
    assert response.json()["answer"] == "根据资料，答案是42"
    assert response.json()["sources"] == ["资料片段1","资料片段2"]