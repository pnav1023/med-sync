import streamlit as st

def clinical_trials():
    st.button("get clinical trials")

st.set_page_config(page_title="Clinical Trials")
st.title("Clinical Trials")
st.sidebar.title("Med Sync")

clinical_trials()