from mcp.server.mcpserver import MCPServer
from vector_store import VectorStore

server = MCPServer("my-tools")

@server.tool("rag_search")
def rag_search(query:str,top_k:int=3):
    """RAG 检索工具：返回 top_k 个 chunk 原文。"""
    return VectorStore().hybrid_query(query, top_k)

server.run()