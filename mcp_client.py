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
            result = await session.call_tool("execute_select_only", {"sql": "SELECT * FROM users LIMIT 3"})
            print("调用工具结果:", result)

asyncio.run(main())



