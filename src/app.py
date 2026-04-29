import streamlit as st
import asyncio
import pandas as pd
from client import MCPClient

st.set_page_config(page_title="Personal AI-LMS", layout="wide")
st.title("🎓 Headless LMS Dashboard")

async def run_lms_interaction(user_query):
    """Handles the full connection lifecycle in a single, safe event loop."""
    client = MCPClient()
    try:
        await client.connect_to_server("src/server.py")
        
        sql_resp = await client.call_tool("get_sql_from_prompt", {"p": user_query})
        query = sql_resp[0].text.strip().replace("```sql", "").replace("```", "").strip()
        
        db_resp = await client.call_tool("run_sql_on_csv", {"query": query})
        raw_data = db_resp[0].text
        

        ai_resp = await client.call_tool("ai_response", {"question": user_query, "result": raw_data})
        
 
        final_answer = ai_resp[0].text if isinstance(ai_resp, list) else ai_resp
        
        return query, raw_data, final_answer
    finally:

        await client.exit_stack.aclose()


user_query = st.text_input("Ask your LMS", placeholder="e.g., Which instructor is teaching Alice Johnson?")

if st.button("Run Query") and user_query:
    with st.spinner("Connecting to LMS Server..."):
        try:
       
            sql, raw, final = asyncio.run(run_lms_interaction(user_query))
            
            st.code(sql, language="sql")
            st.success(final)
            with st.expander("Raw Database Result"):
                st.text(raw)
        except Exception as e:
            st.error(f"LMS Error: {e}")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Student Directory")
    st.dataframe(pd.read_csv("data/data.csv"), width='stretch')
with col2:
    st.subheader("Course Catalog")
    st.dataframe(pd.read_csv("data/courses.csv"), width='stretch')