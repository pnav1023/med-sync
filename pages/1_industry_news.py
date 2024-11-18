import streamlit as st

def industry_news():
    st.title("Industry News feed")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("News 1")
    with col2:
        st.write("News 2")

st.set_page_config(page_title="Industry News", layout="wide")
st.sidebar.title("Med Sync")

industry_news()