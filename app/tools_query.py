from mcp.server.mcpserver import MCPServer
from vector_store import VectorStore
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件中的环境变量

server = MCPServer("my-tools")

@server.tool("rag_search")
async def rag_search(query:str,top_k:int=3):
    """RAG 检索工具：返回 top_k 个 chunk 原文。"""
    return await VectorStore("kb_1").hybrid_query(query, top_k)

server.run()

