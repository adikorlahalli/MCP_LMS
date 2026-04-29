#  Headless LMS Dashboard

An AI-powered Learning Management System (LMS) dashboard that allows users to query academic data using natural language. This project leverages the **Model Context Protocol (MCP)** to bridge a Streamlit frontend with a backend server that utilizes **Google Gemini** for SQL generation and data analysis.

##  Features
- **Natural Language Querying**: Ask questions like "Who is teaching Alice Johnson?" and get direct answers.
- **Automated SQL Generation**: Translates user prompts into complex SQL joins across multiple tables.
- **In-Memory SQL Execution**: Processes queries safely in an isolated SQLite environment using Pandas.
- **Headless Architecture**: Decouples data logic (Server) from the presentation layer (Client/Dashboard).

##  Architecture
The system follows a Client-Server model over MCP:
1.  **Frontend (Streamlit)**: Captures user input and displays results.
2.  **MCP Client**: Manages the connection and tool calls to the server.
3.  **MCP Server**: 
    -   **SQL Tool**: Converts text to SQL based on the database schema.
    -   **Execution Tool**: Loads CSVs into SQLite and runs the generated query.
    -   **AI Response Tool**: Refines raw data into a conversational sentence.

##  Prerequisites
- Python 3.10+
- A Google Gemini API Key (Gemini 2.5 Flash-Lite or higher)

##  Setup & Installation
1. **Install Dependencies**:
   ```bash
   conda create --name "MCP-LMS" python=3.10
   conda activate MCP-LMS
   cd MCP_Complete_Final
   pip install -r requirements.txt
   ```
2. **Environment Configuration**:
   Create a `.env` file and add your Google API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
   The key can be obtained from the [Google AI Studio](https://aistudio.google.com/api-keys).
   Click "Create API Key" and copy the generated key into your `.env` file.

##  How to Run
Launch the Streamlit dashboard

In the MCP_LMS folder run the following command:
```bash
streamlit run src/app.py
```