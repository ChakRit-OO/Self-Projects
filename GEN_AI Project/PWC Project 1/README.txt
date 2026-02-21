#######################################################################################################################################

Documentation explaining the workflow and model logic:

A fraud detection framework using Generative AI (GenAI) and unsupervised machine 
learning to identify suspicious patterns in financial transactions. 

#######################################################################################################################################
---------------------------------------------------------------------------------------------------------------------------------------

CAUTION-1:

The [ipynb] file will automatically fetch the Data from CSV and run end to end. It will generate the [GEN AI FRAUD DASHBOARD.py] file,
which is responsible for the AI Dashboard on 'Streamlit'. This process is automated end to end.  
Just keep the script and CSV data in a same folder.
---------------------------------------------------------------------------------------------------------------------------------------

#######################################################################################################################################

CAUTION-2:

For the API key:
Change the API key accordingly to run it correctly. If the API key is not used correctly then it will not give the AI-Reasoning outcome.
API provider version should be aligned with the API key.

{Here I used 'gemini/2.5-flash'}
#######################################################################################################################################



1. Project Overview
This project aims to build a real-time fraud detection system for banking transactions. Unlike traditional systems that rely on static rules (e.g., "flag all transactions over $10,000"), this solution uses Unsupervised Machine Learning to detect unknown anomaly patterns and Generative AI to provide human-readable explanations for why a transaction is suspicious.

2. Solution Workflow
The system follows a standard Data Science pipeline:

Data Ingestion: Loading raw transaction logs.

Preprocessing & Feature Engineering: transforming raw data into meaningful behavioral indicators.

Anomaly Detection: Applying the Isolation Forest algorithm to identify outliers.

GenAI Contextualization: Generating prompts for an LLM to explain the risk.

Visualization: Plotting anomalies to validate findings.

3.Machine Learning Model: Isolation Forest
We selected Isolation Forest for this task.

Why this model?
Unsupervised: We do not have a labeled dataset with "Fraud" flags. We need the model to discover the fraud on its own.

Assumption: Fraudulent data points are "few and different."

Mechanism: The algorithm randomly selects a feature and splits the data.

Normal points are clustered together and require many splits to be isolated.

Anomalies (Fraud) are far from the crowd and are isolated very quickly (few splits).