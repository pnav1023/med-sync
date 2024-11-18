import streamlit as st
from scripts.pub_med_script import search_pubmed
from scripts.ai_summary import summarize_content

def academic_research():
    if "res" not in st.session_state:
        st.session_state.res = []
    if "filtered_res" not in st.session_state:
        st.session_state.filtered_res = []
    if "selected_article" not in st.session_state:
        st.session_state.selected_article = {}
    
    with st.spinner("Fetching articles..."):
        try:
            if not st.session_state.res:
        # Attempt to fetch articles from PubMed
                st.session_state.res = search_pubmed("latest healthcare updates", 10)
        except Exception as e:
                st.error(f"An error occurred while fetching articles: {str(e)}. Please try again later.")
                st.session_state.res = []

    search_query = st.text_input("Search articles")
    st.write("**News feed**")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.res:
            st.session_state.filtered_res = [
                article for article in st.session_state.res if search_query.lower() in article["Title"].lower()
            ]
        else:
            st.warning("No articles found. Please refine your search.")
        
        for i, article in enumerate(st.session_state.filtered_res):
            
            if isinstance(article, dict):
                with st.container(border=True):
                    col5, col6 = st.columns([7, 1])
                    with col5:
                        st.write(f"{article['PubDate']}")
                    with col6:
                        st.button("🔖", key=f"bookmark_{i}")
                    st.write(f"**[{article['Title']}]({article['URL']})**")
                    col3, col4 = st.columns([2, 1])
                    with col3:
                        st.write(f"Source: {article['Source']}")
                    with col4:
                        if st.button("Get AI summary", key=i):
                            st.session_state.selected_article = article
    with col2:
        if st.session_state.selected_article:
            with st.container(border=True):
                article = st.session_state.selected_article
                st.write(f"**{article['Title']}**")
                st.write(f"[Read full article]({article['URL']})")
                st.write(f"Source: {article['Source']}")
                authors_formatted = [author["name"] for author in article["Authors"]]
                st.write(f"Authors: {', '.join(authors_formatted)}")
                with st.spinner("Generating AI summary..."):
                    try:
                        st.write(
                            summarize_content(
                                article["URL"]
                                # provider_role=st.session_state.provider_role,
                                # specialty=st.session_state.specialty,
                                # age_group=st.session_state.patient_age_group,
                                # disease_interest=st.session_state.diseases_of_interest,
                                # drug_interest=st.session_state.drugs_of_interest,
                                # additional_keywords=st.session_state.additional_keywords
                            )
                        )
                    except Exception as e:
                        st.error(F"An error occurred while fetching AI summary: {str(e)}")

st.set_page_config(page_title="Academic Research", layout="wide")
st.sidebar.title("Med Sync")

academic_research()