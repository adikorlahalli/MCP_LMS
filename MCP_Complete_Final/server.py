import csv
import os
import sqlite3
import pandas as pd
from pathlib import Path
from typing import List
from dotenv import load_dotenv


from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent


from google import genai


os.chdir(Path(__file__).parent)
load_dotenv()


mcp = FastMCP("student-server")


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)


MODEL_ID = "gemini-2.5-flash-lite"

@mcp.tool()
def get_student_gpa(name: str) -> str:
    with open("data.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"].lower() == name.lower():
                return f"{name}'s GPA is {row['GPA']}"
    return f"No record found for {name}."

@mcp.tool()
def analyze_student_progress(name: str) -> str:
    with open("data.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"].lower() == name.lower():
                gpa = row["GPA"]
                prompt = (
                    f"The student {name} has a GPA of {gpa}. "
                    f"Say in one sentence whether the student is doing great, average, or needs improvement."
                )
                response = client.models.generate_content(model=MODEL_ID, contents=prompt)
                return response.text.strip()
    return f"No record found for {name}."

@mcp.tool()
def get_sql_from_prompt(p: str) -> str:
    if not GOOGLE_API_KEY:
        return "GOOGLE_API_KEY not found. Please check your .env file."

    df = pd.read_csv("data.csv")
    schema_str = "\n".join([f"- {col} ({df[col].dtype})" for col in df.columns])
    preview_str = df.head().to_string(index=False)

    prompt = f"""
    You are an expert SQL generator.
    THE TABLE NAME IS 'students'.
    Columns:
    {schema_str}

    First rows:
    {preview_str}

    Generate EXACTLY ONE SQL SELECT statement (no explanation, no markdown, no backticks).
    Request: "{p}"
    """
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

@mcp.tool()
def run_sql_on_csv(query: str) -> str:

    query = query.text if isinstance(query, TextContent) else str(query)
    print(query)

    try:
        df = pd.read_csv("data.csv")

        conn = sqlite3.connect(":memory:")
        df.to_sql("students", conn, index=False, if_exists="replace")


        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        if not rows:
            return "No results found."

        result = [", ".join(columns)]
        for row in rows:
            result.append(", ".join(str(cell) for cell in row))

        conn.close()
        return "\n".join(result)

    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def ai_response(question: str, result: List[TextContent]) -> str:
    text = "\n".join([r.text for r in result])

    prompt = f"""
    Question: {question}
    Extracted Text: {text}
    Rewrite the extracted text as a single complete sentence.
    """


    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")