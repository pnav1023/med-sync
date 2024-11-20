from pytrials.client import ClinicalTrials
import pandas as pd 
import streamlit as st

# Helper function to fetch clinical trials
def fetch_clinical_trials(drug, disease):
    ct = ClinicalTrials()
    search_expr = f"{drug}+{disease}"
    try:
        fields = ct.get_study_fields(
            search_expr=search_expr,
            fields=["NCT Number", "Conditions", "Study Title"],
            max_studies=15,
            fmt="csv",
        )
        return pd.DataFrame.from_records(fields[1:], columns=fields[0])
    except Exception as e:
        st.error(f"An error occurred while fetching clinical trials: {e}")
        return pd.DataFrame()
