import streamlit as st

def selected_article_block(article, summarize_content):
    with st.container(border=True):
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
                    )
                )
            except Exception as e:
                st.error(f"An error occurred while generating AI summary: {str(e)}. Please try again later.")