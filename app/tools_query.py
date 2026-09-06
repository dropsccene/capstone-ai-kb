from mcp.server.mcpserver import MCPServer
from vector_store import VectorStore
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的环境变量
import pymysql


server = MCPServer("my-tools")

@server.tool("rag_search")
async def rag_search(query:str,top_k:int=3):
    """RAG 检索工具：返回 top_k 个 chunk 原文。"""
    return await VectorStore("kb_1").hybrid_query(query, top_k)



@server.tool("execute_select_only")
async def execute_select_only(sql:str):
    """查询数据库，输入SQL语句返回查询结果"""
    if not sql.strip().lower().startswith("select"):
        return "只允许执行 select 语句"
    conn = None
    try:
        conn = pymysql.connect(
            host="localhost",
            port=3307,
            user="root",
            password="learn123",
            database="lab",
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        return str(result)
    except pymysql.MySQLError as e:
        return f"SQL 执行出错: {e}"
    finally:
        if conn:
            conn.close()

server.run()