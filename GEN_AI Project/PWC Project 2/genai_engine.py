
# ==============================================================
# Section 3.1 – GPT-4 API Integration
# Section 3.2 – Intent Extraction from User Query
# Section 3.3 – Contextual Response Generation
# ==============================================================


import json
import re
from datetime import datetime
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




def classify_user_query(user_query):

    # ==========================================================
    # GPT-BASED INTENT EXTRACTION
    # ==========================================================
    try:
        system_prompt = """
        You are a Sales Analytics AI assistant.

        Extract structured JSON from user queries.

        Return ONLY valid JSON in this format:

        {
            "intent": "descriptive | comparison | trend | ranking",
            "metric": "sales | revenue | customers",
            "time_filter": "year if mentioned",
            "quarter": "Q1 | Q2 | Q3 | Q4 if mentioned",
            "top_n": "number if ranking"
        }

        Only return JSON. No explanation.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0
        )

        output_text = response.choices[0].message.content.strip()

        return json.loads(output_text)

    except Exception as e:
        print("⚠ GPT Failed, switching to rule-based fallback:", e)

    # ==========================================================
    # 2️⃣ RULE-BASED FALLBACK (Your Original Logic)
    # ==========================================================

    user_query = user_query.lower()
    current_year = datetime.now().year

    # Year Detection
    years = re.findall(r"\b20\d{2}\b", user_query)

    if "last year" in user_query:
        years.append(str(current_year - 1))
    if "this year" in user_query:
        years.append(str(current_year))

    # Month Detection
    months = [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december"
    ]

    month_found = None
    for month in months:
        if month in user_query:
            month_found = month
            break

    # Quarter Detection
    quarter_match = re.search(r"\bq[1-4]\b", user_query)
    quarter = quarter_match.group().upper() if quarter_match else None

    # Top N Detection
    top_match = re.search(r"top\s*(\d+)", user_query)
    top_n = int(top_match.group(1)) if top_match else None

    # Highest Product
    if "highest" in user_query and "product" in user_query:
        return {
            "intent": "ranking",
            "metric": "sales",
            "top_n": 1,
            "time_filter": years[0] if years else None
        }

    # Comparison
    if "compare" in user_query:
        return {
            "intent": "comparison",
            "metric": "sales",
            "time_filter": years if years else None,
            "month": month_found,
            "quarter": quarter
        }

    # Trend
    elif "trend" in user_query:
        return {
            "intent": "trend",
            "metric": "sales",
            "time_filter": years[0] if years else None,
            "month": month_found,
            "quarter": quarter
        }

    # Ranking
    elif top_n:
        return {
            "intent": "ranking",
            "metric": "sales",
            "top_n": top_n,
            "time_filter": years[0] if years else None
        }

    # Customers
    elif "customer" in user_query:
        return {
            "intent": "descriptive",
            "metric": "customers",
            "time_filter": years[0] if years else None
        }

    # Revenue
    elif "revenue" in user_query:
        return {
            "intent": "descriptive",
            "metric": "revenue",
            "time_filter": years[0] if years else None,
            "month": month_found,
            "quarter": quarter
        }

    # Default Sales
    else:
        return {
            "intent": "descriptive",
            "metric": "sales",
            "time_filter": years[0] if years else None,
            "month": month_found,
            "quarter": quarter
        }


