
# ===============================
# GEN AI FRAUD DASHBOARD (FIXED)
# ===============================

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai

st.set_page_config(page_title="Fraud GenAI Dashboard", layout="wide")

# -----------------------
# Load Gemini API
# -----------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Gemini API key not found in .env file")
    st.stop()

genai.configure(api_key=api_key)

# -----------------------
# Load anomalies
# -----------------------
@st.cache_data
def load_data():
    return pd.read_csv("final_anomalies.csv")

df_anomalies = load_data()

st.title("🛡️ AI Fraud Detection Dashboard")
st.write("Unsupervised ML + Generative AI Fraud Analysis")

# -----------------------
# Gemini AI reasoning
# -----------------------
def generate_ai_report(row):

    prompt = f"""
    You are a senior fraud analyst in a bank.

    Analyze this suspicious transaction:

    Transaction ID: {row.get('TransactionID','')}
    Amount: {row.get('TransactionAmount','')}
    Account Balance: {row.get('AccountBalance','')}
    Login Attempts: {row.get('LoginAttempts','')}
    Duration: {row.get('TransactionDuration','')}
    Channel: {row.get('Channel','')}
    Type: {row.get('TransactionType','')}

    Explain WHY this looks suspicious in simple business terms.
    Keep answer under 40 words.
    """

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)

        # Read Gemini output: 
        if response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "No AI insight generated"

    except Exception as e:
        return f"Gemini Error: {str(e)}"



# -----------------------
# Sidebar filters
# -----------------------
st.sidebar.header("Filters")

min_amount = st.sidebar.slider("Minimum Amount", 0, 5000, 0)

search_id = st.sidebar.text_input("Search Transaction ID")

filtered_df = df_anomalies[df_anomalies["TransactionAmount"] >= min_amount]

if search_id:
    filtered_df = filtered_df[
        filtered_df["TransactionID"].astype(str).str.contains(search_id)
    ]

st.subheader(f"⚠️ Suspicious Transactions Found: {len(filtered_df)}")
st.dataframe(filtered_df, use_container_width=True)

# -----------------------
# AI GENERATE BUTTON
# -----------------------
st.divider()
st.subheader("🧠 Generate AI Fraud Reasoning")

if st.button("Generate AI Insights (Gemini)"):

    sample_df = filtered_df.head(20).copy()  # LIMIT to avoid API overload

    with st.spinner("Gemini analyzing transactions..."):
        sample_df["AI_Reasoning"] = sample_df.apply(generate_ai_report, axis=1)

    st.success("AI Insights Generated!")

    st.dataframe(sample_df, use_container_width=True)

    # download option
    csv = sample_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download AI Report",
        csv,
        "fraud_ai_report.csv",
        "text/csv"
    )
