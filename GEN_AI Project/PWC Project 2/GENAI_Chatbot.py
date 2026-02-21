
# ==============================================================
# Streamlit Chat-Based Sales Analytics UI
# ==============================================================

import streamlit as st
import time
from datetime import datetime
import pandas as pd

from genai_engine import classify_user_query
from query_engine import execute_query

# --------------------------------------------------------------
# Page Config
# --------------------------------------------------------------
st.set_page_config(
    page_title="GenAI Sales Analytics Chatbot",
    page_icon="💬",
    layout="wide"
)

st.title("GenAI-Powered Sales Analytics Chatbot")

# --------------------------------------------------------------
# Session State Initialization
# --------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --------------------------------------------------------------
# Suggested Questions Panel
# --------------------------------------------------------------
SUGGESTED_QUESTIONS = [
    "Show total sales for 2022",
    "Compare sales between 2022 and 2023",
    "Top 5 products by revenue",
    "Show monthly sales trend for 2023",
    "Total unique customers"
]

with st.sidebar:
    st.header("Suggested Queries")
    for q in SUGGESTED_QUESTIONS:
        if st.button(q):
            st.session_state.selected_query = q

# --------------------------------------------------------------
# Chat Input
# --------------------------------------------------------------
user_input = st.chat_input("Ask a business question")

query_to_process = None

if user_input:
    query_to_process = user_input.strip()
elif "selected_query" in st.session_state:
    query_to_process = st.session_state.selected_query
    del st.session_state.selected_query

# --------------------------------------------------------------
# Process Query
# --------------------------------------------------------------
if query_to_process:

    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        intent_data = classify_user_query(query_to_process)
        result = execute_query(intent_data)
    except Exception as e:
        result = f"Database Error: {e}"
        intent_data = {}

    processing_time = round(time.time() - start_time, 2)

    # ✅ FIX 1: store intent
    st.session_state.chat_history.append({
        "timestamp": timestamp,
        "query": query_to_process,
        "intent": intent_data,
        "result": result,
        "processing_time_sec": processing_time
    })

# --------------------------------------------------------------
# Display Chat History (FIXED TABLE LOGIC)
# --------------------------------------------------------------
st.subheader("Chat History")

for chat in st.session_state.chat_history:
    with st.container():

        st.markdown(f"**Query:** {chat['query']}")
        st.markdown("**Result:**")

        result = chat["result"]
        intent = chat.get("intent", {})

        # -------- TABLE HANDLING FIX --------
        if isinstance(result, list) and result:

            # Case 1: list of dicts (already good)
            if isinstance(result[0], dict):
                st.table(pd.DataFrame(result))

            # Case 2: list of tuples/lists → intent-based columns
            elif isinstance(result[0], (list, tuple)):
                df = pd.DataFrame(result)

                metric = intent.get("metric", "").lower()
                intent_type = intent.get("intent", "").lower()

                if intent_type == "ranking":
                    if metric == "sales":
                        df.columns = ["Product", "Sales"]
                    elif metric == "revenue":
                        df.columns = ["Product", "Revenue"]
                    else:
                        df.columns = ["Item", "Value"]

                elif intent_type == "trend":
                    df.columns = ["Time Period", metric.title() or "Value"]

                elif intent_type == "comparison":
                    df.columns = ["Category", metric.title() or "Value"]

                elif metric == "customers":
                    df.columns = ["Category", "Customer Count"]

                else:
                    df.columns = [f"Column {i+1}" for i in range(df.shape[1])]

                st.table(df)

            else:
                st.write(result)

        elif isinstance(result, dict):
            st.table(pd.DataFrame([result]))

        else:
            st.write(result)

        st.caption(
            f"Executed on {chat['timestamp']} | "
            f"Processing time: {chat['processing_time_sec']} seconds"
        )

        st.divider()

# --------------------------------------------------------------
# Download Conversation Report
# --------------------------------------------------------------
if st.session_state.chat_history:
    st.subheader("Download Report")

    report_df = pd.DataFrame(st.session_state.chat_history)
    csv = report_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Chat & Analytics Report",
        data=csv,
        file_name="sales_analytics_chat_report.csv",
        mime="text/csv"
    )
