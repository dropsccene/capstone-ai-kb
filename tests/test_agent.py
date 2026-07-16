import pytest
from unittest.mock import patch, MagicMock

# Mock OpenAI client's chat.completions.create 返回值
def fake_msg_with_answer():
    """模拟 LLM 直接返回答案（不调工具）"""
    mock_msg = MagicMock()
    mock_msg.tool_calls = None
    mock_msg.content = "数据库中共有 3 位用户：张三、李四、王五。"
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message = mock_msg
    return mock_resp

@patch("app.agent.client.chat.completions.create")
def test_ask_database(mock_create, client):
    mock_create.return_value = fake_msg_with_answer()
    
    response = client.post(
        "/api/agent/ask-database",
        json={"question": "数据库中有哪些用户？"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "3 位用户" in response.json()["answer"]

@patch("app.agent.client.chat.completions.create")
def test_ask_database_no_question(mock_create, client):
    response = client.post(
        "/api/agent/ask-database",
        json={}  # 缺 question 字段
    )
    assert response.status_code == 422
