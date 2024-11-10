import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content


st.title('Med Sync')
res = search_pubmed('cancer treatment', 10)

for i, article in enumerate(res):
    with st.expander(f"{article['Title']}"):
        st.write(f"[Read full article]({article['URL']})")
        if st.button(f"Get AI summary", key=i):
            st.write(summarize_content(article['URL']))

