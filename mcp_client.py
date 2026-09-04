from mcp.client.stdio import StdioServerParameters,stdio_client
from mcp.client.session import ClientSession
import asyncio

server_parrmeters = StdioServerParameters(
    command="python",
    args=["app/tools_query.py"])
async def main():
    async with stdio_client(server_parrmeters) as streams:
        async with ClientSession(*streams) as session:
            await session.initialize()
            list_tools = await session.list_tools()
            call_tool = await session.call_tool("rag_search", {"query": "什么是向量数据库？","top_k": 2})
            print("工具列表:", list_tools)
            print("调用工具结果:", call_tool)

asyncio.run(main())



