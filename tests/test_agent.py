import json
from unittest.mock import patch, MagicMock


def fake_msg_with_answer(content="数据库中共有 3 位用户：张三、李四、王五。"):
    """模拟 LLM 直接返回答案（不调工具）"""
    mock_msg = MagicMock()
    mock_msg.tool_calls = None
    mock_msg.content = content
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message = mock_msg
    return mock_resp


def fake_msg_with_tool_call(sql, call_id="call_1"):
    """模拟 LLM 决定调用 query_database 工具（返回 tool_calls）"""
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = "query_database"
    tc.function.arguments = json.dumps({"sql": sql})
    mock_msg = MagicMock()
    mock_msg.tool_calls = [tc]
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message = mock_msg
    return mock_resp


async def fake_create(*args, **kwargs):
    """异步版本的 create mock"""
    return fake_msg_with_answer()


@patch("app.agent.client.chat.completions.create", side_effect=fake_create)
def test_ask_database(mock_create, client):
    response = client.post(
        "/api/agent/ask-database",
        json={"question": "数据库中有哪些用户？"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "3 位用户" in response.json()["answer"]


@patch("app.agent.client.chat.completions.create", side_effect=fake_create)
def test_ask_database_no_question(mock_create, client):
    response = client.post(
        "/api/agent/ask-database",
        json={}
    )
    assert response.status_code == 422


@patch("app.agent.query_database", return_value="[(1, '张三')]")
def test_tool_call_flow(mock_db, client):
    """核心缺口：LLM 走工具调用路径时，observation 要正确回灌对话历史"""
    seen = []

    async def fake_create(*args, **kwargs):
        seen.append(kwargs["messages"])
        if len(seen) == 1:
            return fake_msg_with_tool_call("SELECT * FROM users")
        return fake_msg_with_answer("查询到 1 位用户：张三")

    with patch("app.agent.client.chat.completions.create", side_effect=fake_create):
        response = client.post("/api/agent/ask-database", json={"question": "有哪些用户？"})

    assert response.status_code == 200
    assert "张三" in response.json()["answer"]
    # 第二次 LLM 调用时，查询结果必须以 role=tool 的 observation 回灌
    tool_msgs = [m for m in seen[1] if m["role"] == "tool"]
    assert tool_msgs and "张三" in tool_msgs[0]["content"]
    mock_db.assert_called_once_with("SELECT * FROM users")


def test_self_correct_on_error(client):
    """self-correction：第一次 SQL 写错 → 错误以 observation 回灌 → 修正后重试成功。

    注意这里不能把 query_database mock 掉——捕获 SQL 错误的代码就在它体内，
    mock 一抛异常真实 catch 就没机会执行。用 wraps 包住真实函数，只加调用计数。
    """
    from app.agent import query_database as real_query_database

    seen = []

    async def fake_create(*args, **kwargs):
        seen.append(kwargs["messages"])
        n = len(seen)
        if n == 1:
            return fake_msg_with_tool_call("SELECT * FROM nope", "call_1")
        if n == 2:
            return fake_msg_with_tool_call("SELECT * FROM users", "call_2")
        return fake_msg_with_answer("修正成功，查到 1 位用户")

    with patch("app.agent.query_database", wraps=real_query_database) as mock_db, \
         patch("app.agent.client.chat.completions.create", side_effect=fake_create):
        response = client.post("/api/agent/ask-database", json={"question": "有哪些用户？"})

    assert response.status_code == 200
    assert "修正成功" in response.json()["answer"]
    # 第二次 LLM 调用必须能看到第一次的错误信息（这是它修正的依据）
    obs = [m["content"] for m in seen[1] if m["role"] == "tool"]
    assert any("SQL 执行出错" in o and "no such table" in o for o in obs)
    # 真实执行了两次 SQL：第一次失败，第二次修正后成功
    assert mock_db.call_count == 2


@patch("app.agent.query_database", return_value="[(1, '张三')]")
def test_non_select_rejected_then_corrected(mock_db, client):
    """DELETE 被拦截 → observation 提示只允许 select → LLM 修正为 SELECT"""
    seen = []

    async def fake_create(*args, **kwargs):
        seen.append(kwargs["messages"])
        n = len(seen)
        if n == 1:
            return fake_msg_with_tool_call("DELETE FROM users", "call_1")
        if n == 2:
            return fake_msg_with_tool_call("SELECT * FROM users", "call_2")
        return fake_msg_with_answer("安全执行")

    with patch("app.agent.client.chat.completions.create", side_effect=fake_create):
        response = client.post("/api/agent/ask-database", json={"question": "有哪些用户？"})

    assert response.status_code == 200
    obs = [m["content"] for m in seen[1] if m["role"] == "tool"]
    assert any("只允许执行 select" in o for o in obs)
    # 数据库只被 SELECT 调用过——拦截是真实的，不是嘴上说说
    mock_db.assert_called_once_with("SELECT * FROM users")


def test_max_rounds_exhausted(client):
    """LLM 每轮都调工具（陷入死循环）→ 到 max_rounds 返回 error 而不是抛异常"""
    async def fake_create(*args, **kwargs):
        return fake_msg_with_tool_call("SELECT 1", "call_x")

    with patch("app.agent.client.chat.completions.create", side_effect=fake_create), \
         patch("app.agent.query_database", return_value="[1]"):
        response = client.post("/api/agent/ask-database", json={"question": "循环测试"})

    assert response.status_code == 200
    answer = response.json()["answer"]
    assert isinstance(answer, dict) and "error" in answer


def test_query_database_catches_sql_error():
    """语法错误不再抛异常炸接口——返回错误文本，供 LLM 自纠正"""
    from app.agent import query_database
    result = query_database("SELECT * FROM 不存在的表")
    assert isinstance(result, str)
    assert "SQL 执行出错" in result
