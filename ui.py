import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content

st.title('Pulse')
res = search_pubmed('cancer treatment', 3)
# st.write(res)

st.subheader('Search Results')
for i, article in enumerate(res):
    st.write(f"{i+1}. {article['Title']}")
    # st.write(article['abstract'])
    st.write(f"Link: {article['URL']}")
    if st.button(f"Get AI summary {i+1}"):
        st.write(summarize_content(article['URL']))
    st.write("---")

