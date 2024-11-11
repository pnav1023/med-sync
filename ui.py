import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content

st.set_page_config(layout="wide")

st.title('Med Sync')
res = search_pubmed('cancer treatment', 10)

for i, article in enumerate(res):
    with st.expander(f"{article['Title']}"):
        col1, col2, col3, col4 = st.columns([2, 2, 4, 1])
        with col1:
            st.write(f"[Read full article]({article['URL']})")
        with col2:
            st.write(f"Source: {article['Source']}")
        with col3:
            authorsFormatted = []
            for author in article['Authors']:
                authorsFormatted.append(author['name'])
            st.write(f"Authors: {', '.join(authorsFormatted)}")
        with col4:
            st.write(f"{article['PubDate']}")
        
        col5, col6 = st.columns([7, 1])
        with col5:
            if st.button(f"Get AI summary", key=i):
                st.write(summarize_content(article['URL']))
        with col6:
            # st.write("tags")
            for j, pubtype in enumerate(article['PubType']):
                st.button(f"{pubtype}", key=f"{i}-{j}", disabled=True)

