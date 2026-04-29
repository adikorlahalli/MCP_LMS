import asyncio
import sys
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        server_params = StdioServerParameters(
            command=sys.executable,         
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        print("--- LMS Server Connected ---")

    async def call_tool(self, tool_name: str, tool_args: dict):
        if self.session is None:
            raise RuntimeError("Not connected to session")
        result = await self.session.call_tool(tool_name, tool_args)
        return result.content

async def main():
    client = MCPClient()
    try:

        await client.connect_to_server("server.py")


        prompt = "Which instructor is teaching Alice Johnson?"
        
  
        sql_command = await client.call_tool("get_sql_from_prompt", {"p": prompt})
        sql_text = sql_command[0].text.strip().replace("```sql", "").replace("```", "").strip()
        print(f"\nPrompt: {prompt}\nSQL: {sql_text}")


        sql_run = await client.call_tool("run_sql_on_csv", {"query": sql_text})
        raw_result = sql_run[0].text
        
        final_answer = await client.call_tool("ai_response", {"question": prompt, "result": raw_result})
        print(f"Result: {final_answer}")

    finally:
        await client.exit_stack.aclose()
        print("\n--- Connection closed gracefully ---")

if __name__ == "__main__":
    asyncio.run(main())