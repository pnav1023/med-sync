import streamlit as st

# Set the title of the app
st.title("My Multipage Streamlit App")

# Navigation menu
st.sidebar.title("Med Sync")
page = st.sidebar.radio(["All", "Academic Research", "Clinical Trials", "Industry News"])

# Routing to different pages
if page == "All":
    import pages.all as all
    all.app()
elif page == "Academic Research":
    import pages.academic_research as academic_research
    academic_research.app()
elif page == "Clinical Trials":
    import pages.clinical_trials as clinical_trials
    clinical_trials.app()
elif page == "Industry News":
    import pages.industry_news as industry_news
    industry_news.app()