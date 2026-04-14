# api.py
from fastapi import FastAPI
import asyncio
from client import MCPClient

app = FastAPI()

client = MCPClient()

@app.on_event("startup")
async def startup():
    await client.connect_to_server("server.py")

@app.get("/highest_gpa")
async def highest_gpa():
    prompt = "Who has the highest gpa and what is their gpa"

    sql_command = await client.call_tool(
        "get_sql_from_prompt",
        {"p": prompt}
    )

    sql_text = sql_command[0].text.strip()

    result = await client.call_tool(
        "run_sql_on_csv",
        {"query": sql_text}
    )

    final = await client.call_tool(
        "ai_response",
        {
            "question": prompt,
            "result": result
        }
    )

    return {"response": final}