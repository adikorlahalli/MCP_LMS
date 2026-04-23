# 🎓 Headless LMS Dashboard

An AI-powered Learning Management System (LMS) dashboard that allows users to query academic data using natural language. This project leverages the **Model Context Protocol (MCP)** to bridge a Streamlit frontend with a backend server that utilizes **Google Gemini** for SQL generation and data analysis.

## 🌟 Features
- **Natural Language Querying**: Ask questions like "Who is teaching Alice Johnson?" and get direct answers.
- **Automated SQL Generation**: Translates user prompts into complex SQL joins across multiple tables.
- **In-Memory SQL Execution**: Processes queries safely in an isolated SQLite environment using Pandas.
- **Headless Architecture**: Decouples data logic (Server) from the presentation layer (Client/Dashboard).

## 🏗️ Architecture
The system follows a Client-Server model over MCP:
1.  **Frontend (Streamlit)**: Captures user input and displays results.
2.  **MCP Client**: Manages the connection and tool calls to the server.
3.  **MCP Server**: 
    -   **SQL Tool**: Converts text to SQL based on the database schema.
    -   **Execution Tool**: Loads CSVs into SQLite and runs the generated query.
    -   **AI Response Tool**: Refines raw data into a conversational sentence.

## 📋 Prerequisites
- Python 3.10+
- A Google Gemini API Key (Gemini 2.5 Flash-Lite or higher)

## ⚙️ Setup & Installation
1. **Install Dependencies**:
   ```bash
   conda create --name "MCP-LMS" python=3.10
   conda activate MCP-LMS
   pip install -r requirements.txt
   ```
2. **Environment Configuration**:
   Create a \`.env\` file and add your Google API key:
   \`\`\`env
   GOOGLE_API_KEY=your_actual_api_key_here
   \`\`\`

## 🚀 How to Run
Launch the Streamlit dashboard:
\`\`\`bash
streamlit run app.py
\`\`\`
EOF

# 3. Create .gitignore (to keep your repo clean)
cat << 'EOF' > .gitignore
.DS_Store
.env
__pycache__/
venv/
*.pyc
EOF

# 4. Create a .env template (reminds you to add your key)
if [ ! -f .env ]; then
  echo "GOOGLE_API_KEY=your_api_key_here" > .env
  echo "Created .env template."
fi

echo "✅ All files (requirements.txt, README.md, .gitignore, .env) have been created in one go!"