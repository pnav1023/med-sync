import streamlit as st

def run():
    st.set_page_config(
        page_title="All", 
        page_icon="☁️"
    )
    st.title("My Multipage Streamlit App")
    st.sidebar.title("Med Sync")

def get_all():
    st.button("get all news")

if __name__ == "__main__":
    run()

    get_all()