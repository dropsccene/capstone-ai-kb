import asyncio
import json

from app.database import SessionLocal
from app.llm import client
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def query_database(sql: str):
    db = SessionLocal()
    try:
        result = db.execute(text(sql)).fetchall()
        return str(result)
    except SQLAlchemyError as e:
        # 错误作为 observation 返回而不是抛异常——两个理由：
        # 1) 不炸接口（语法错误现在会 500）
        # 2) self-correction 的地基：LLM 下一轮能看到错误信息并修正 SQL
        return f"SQL 执行出错: {e}"
    finally:
        db.close()


def execute_select_only(sql: str):
    if not sql.strip().lower().startswith("select"):
        return "只允许执行 select 语句"
    return query_database(sql)


tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "查询数据库，输入SQL语句返回查询结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string"}
                },
                "required": ["sql"]
            }
        }
    }
]


class ReActAgent:
    def __init__(self, tools, client):
        self.tools = tools
        self.client = client
        self.tool_map = {
            "query_database": execute_select_only
        }

    async def run(self, messages, user_query, max_rounds=10):
        messages.append({"role": "user", "content": user_query})
        for _ in range(max_rounds):
            response = await self.client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=messages,
                tools=self.tools
            )
            msg = response.choices[0].message
            if msg.tool_calls:
                messages.append(msg)
                for tool_call in msg.tool_calls:
                    tc = tool_call
                    body = json.loads(tc.function.arguments)
                    # query_database 是同步 SQL，直接 await 会阻塞事件循环
                    # （压测实测 ReAct P95 12s 的帮凶之一）——丢线程池执行
                    result = await asyncio.to_thread(self.tool_map[tc.function.name], **body)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
                continue
            return msg.content
        return {"error": "达到最大轮数，未能得到最终答案"}
