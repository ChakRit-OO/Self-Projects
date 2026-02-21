
#==============================================================
# Section 2.1 – Backend Query Interpretation Logic
# Section 2.2 – Question Category Classification
# Section 2.3 – Dynamic Textual Insight Generation
# ==============================================================
import sqlite3

DB_PATH = "sales_data.db"

def execute_query(intent_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ----------------------------
    # Extract Intent Data
    # ----------------------------
    metric = intent_data.get("metric")
    years = intent_data.get("time_filter") or []
    quarter = intent_data.get("quarter")
    intent = intent_data.get("intent") or ""
    top_n = intent_data.get("top_n")

    # ----------------------------
    # Map Metric to Column
    # ----------------------------
    if metric == "sales":
        column = "sales_amount"
    elif metric == "customers":
        column = "customer_number"
    else:
        column = "sales_amount"

    query = ""
    params = []

    # ----------------------------
    # YEAR FILTER
    # ----------------------------
    year_condition = ""
    if years:
        if isinstance(years, list):
            placeholders = ",".join(["?"] * len(years))
            year_condition = f" AND strftime('%Y', transaction_month) IN ({placeholders})"
            params.extend(years)
        else:
            year_condition = " AND strftime('%Y', transaction_month) = ?"
            params.append(years)

    # ----------------------------
    # QUARTER FILTER
    # ----------------------------
    quarter_condition = ""
    if quarter:
        quarter_map = {
            "Q1": ("01", "02", "03"),
            "Q2": ("04", "05", "06"),
            "Q3": ("07", "08", "09"),
            "Q4": ("10", "11", "12"),
        }

        months = quarter_map.get(quarter)
        if months:
            quarter_condition = " AND strftime('%m', transaction_month) IN (?, ?, ?)"
            params.extend(months)

    # ==========================================================
    # SINGLE DECISION TREE (VERY IMPORTANT)
    # ==========================================================

    # 1️⃣ Comparison
    if intent == "comparison" and isinstance(years, list):
        query = f"""
        SELECT strftime('%Y', transaction_month) as year,
               SUM({column}) as total
        FROM sales_data
        WHERE 1=1 {year_condition}
        GROUP BY year
        ORDER BY year
        """

    # 2️⃣ Monthly Trend
    elif "trend" in intent:
        query = f"""
        SELECT strftime('%m', transaction_month) as month,
               SUM({column}) as total
        FROM sales_data
        WHERE 1=1 {year_condition}
        GROUP BY month
        ORDER BY month
        """

    # 3️⃣ Top Products
    elif intent == "ranking" and top_n:
        query = f"""
        SELECT product_name,
               SUM(sales_amount) as total
        FROM sales_data
        WHERE 1=1 {year_condition}
        GROUP BY product_name
        ORDER BY total DESC
        LIMIT ?
        """
        params.append(top_n)

    # 4️⃣ Customers
    elif metric == "customers":
        query = """
        SELECT COUNT(DISTINCT customer_number)
        FROM sales_data
        """

    # 5️⃣ Sales Total
    elif metric == "sales":
        query = f"""
        SELECT SUM({column})
        FROM sales_data
        WHERE 1=1 {year_condition} {quarter_condition}
        """

    # 6️⃣ Default
    else:
        query = f"""
        SELECT SUM({column})
        FROM sales_data
        WHERE 1=1 {year_condition} {quarter_condition}
        """

    # ----------------------------
    # Execute Query
    # ----------------------------
    cursor.execute(query, params)
    result = cursor.fetchall()

    conn.close()
    return result

#You’ve now built:

#Multi-year dynamic Sales Analytics Engine
#With NLP detection
#With quarter, trend, ranking support
#With comparison support
