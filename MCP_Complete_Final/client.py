import asyncio
import sys
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """Connect to the MCP server script via stdio"""
        if not server_script_path.endswith(".py"):
            raise ValueError("Server script must be a .py file")

        server_params = StdioServerParameters(
            command=sys.executable,         
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        tools = (await self.session.list_tools()).tools
        print("\nConnected to server. Available tools:")
        for tool in tools:
            print(f" - {tool.name}: {tool.description}")
        self.tool_names = [tool.name for tool in tools]

    async def call_tool(self, tool_name: str, tool_args: dict):
        if self.session is None:
            raise RuntimeError("Not connected to session")
        result = await self.session.call_tool(tool_name, tool_args)
        return result.content

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    server_script = sys.argv[1]
    client = MCPClient()
    try:
        # Connect to the server
        await client.connect_to_server(server_script)

        while True:
            # name = input("\nEnter student name (or 'quit'): ")
            # if name.lower() == "quit":
            #     break

            # gpa_result = await client.call_tool("get_student_gpa", {"name": name})
            # analysis_result = await client.call_tool("analyze_student_progress", {"name": name})

            # sql_query = "INSERT INTO students VALUES (5, 'Aditya Korlahalli', 21, 'senior', 'ark11@illinois.edu', 3.7)"
            # sql_run = await client.call_tool("run_sql_on_csv", {"query": sql_query})

            prompt = "Who has the highest gpa and what is their gpa"
            sql_command = await client.call_tool("get_sql_from_prompt",  {"p": prompt})
            sql_text = sql_command[0].text.strip()

            sql_text = sql_text.replace("```sql", "")
            sql_text = sql_text.replace("```", "")
            sql_text = sql_text.strip()

            print(sql_text)



            sql_run3 = await client.call_tool("run_sql_on_csv", {"query": sql_text})



            # sql_query2 = "SELECT Name FROM students"
            # sql_run2 = await client.call_tool("run_sql_on_csv", {"query": sql_query2})

            # print("\nRaw GPA lookup:", gpa_result)
            # print("AI Analysis:", analysis_result)

            print(sql_run3)

            rest = await client.call_tool("ai_response", {"question" : prompt, "result": sql_run3})
            print(rest)
            break

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())



