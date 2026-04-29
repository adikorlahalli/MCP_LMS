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
    with open("../data/data.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"].lower() == name.lower():
                return f"{name}'s GPA is {row['GPA']}"
    return f"No record found for {name}."

@mcp.tool()
def analyze_student_progress(name: str) -> str:
    with open("../data/data.csv", newline="") as f:
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
    schema = """
    Tables:
    - students (ID, Name, Age, Grade, Email, GPA)
    - courses (CourseID, CourseName, Instructor)
    - enrollments (StudentID, CourseID, Status)
    """
    prompt = f"Given this schema: {schema}\nGenerate only the SQL query for: {p}\nDo not include backticks or markdown."
    
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

@mcp.tool()
def run_sql_on_csv(query: str) -> str:
    query = query.text if isinstance(query, TextContent) else str(query)
    
    try:
        conn = sqlite3.connect(":memory:")
        pd.read_csv("../data/data.csv").to_sql("students", conn, index=False, if_exists="replace")
        pd.read_csv("../data/courses.csv").to_sql("courses", conn, index=False, if_exists="replace")
        pd.read_csv("../data/enrollments.csv").to_sql("enrollments", conn, index=False, if_exists="replace")

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            return "No results found."

        columns = [desc[0] for desc in cursor.description]
        result = [", ".join(columns)]
        for row in rows:
            result.append(", ".join(str(cell) for cell in row))

        conn.close()
        return "\n".join(result)

    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def ai_response(question: str, result: str) -> str:
    prompt = f"""
    Question: {question}
    Extracted Data: {result}
    Rewrite the extracted data as a single complete sentence that answers the question.
    """
    try:
        response = client.models.generate_content(model=MODEL_ID, contents=prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()