import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content
import pandas as pd
import feedparser
from pytrials.client import ClinicalTrials
import urllib.request
from html.parser import HTMLParser
from rss import fetch_rss_feed
from trials import fetch_clinical_trials

# Configure page settings
st.set_page_config(page_title="Med Sync", layout="wide")

# Create a class to strip HTML tags
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = []

    def handle_data(self, data):
        self.data.append(data)

    def get_data(self):
        return ''.join(self.data)

def strip_html(html):
    stripper = HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()


# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Welcome"
if "rss_entries" not in st.session_state:
    st.session_state.rss_entries = []
if "clinical_trials" not in st.session_state:
    st.session_state.clinical_trials = pd.DataFrame()
if "academic_research" not in st.session_state:
    st.session_state.academic_research = []
if "rss2_entries" not in st.session_state:
    st.session_state.rss2_entries = []
if "rss3_entries" not in st.session_state:
    st.session_state.rss3_entries = []
if "rss4_entries" not in st.session_state:
    st.session_state.rss4_entries = []

try:
    if st.session_state.current_page == "Welcome":
        st.title("Welcome to Med Sync!")
        st.write("""
            Med Sync is designed to keep you up-to-date on the latest in healthcare, tailored specifically to your specialty and interests.
            With Med Sync, you’ll receive real-time updates on everything from new clinical guidelines and research to clinical trial results and industry news.

            You can personalize what you see based on the diseases, drugs, or fields you’re most interested in, making it easier to stay informed on what matters to you. 
            Plus, Med Sync lets you save articles, add personal notes, and quickly filter by specialty or topic so that you’re always on top of the latest developments in your field.
        """)

        if st.button("Get Started"):
            st.session_state.current_page = "Input Page"

    elif st.session_state.current_page == "Input Page":
        st.title("Personal Input Page")
        st.session_state.diseases_of_interest = st.text_input("Enter diseases of interest:")
        st.session_state.drugs_of_interest = st.text_input("Enter drugs of interest:")

        
        
        
        if st.button("Fetch Updates"):
            with st.spinner("Fetching updates..."):
                # Fetch Academic Research
                search_string = f"{st.session_state.diseases_of_interest}, {st.session_state.drugs_of_interest}"
                st.session_state.academic_research = search_pubmed(search_string, 10)

                # Fetch Clinical Trials
                drug = st.session_state.drugs_of_interest.split(",")[0] if st.session_state.drugs_of_interest else ""
                disease = st.session_state.diseases_of_interest.split(",")[0] if st.session_state.diseases_of_interest else ""
                st.session_state.clinical_trials = fetch_clinical_trials(drug, disease)

                # Fetch Industry News
                rss_url = "https://www.medpagetoday.com/rss/headlines.xml"
                st.session_state.rss_entries = fetch_rss_feed(rss_url)
                
                
                ##fetch regulatory news
                rss_url2 = "https://www.fiercehealthcare.com/rss/regulatory/xml"
                st.session_state.rss2_entries = fetch_rss_feed(rss_url2) 
                
                
                ##fetch provider news
                rss_url3 = "https://www.fiercehealthcare.com/rss/providers/xml"
                st.session_state.rss3_entries = fetch_rss_feed(rss_url3)
                
                ##fetch drug news
                rss_url4 = "https://www.fiercepharma.com/rss/xml"
                st.session_state.rss4_entries = fetch_rss_feed(rss_url4)

            st.session_state.current_page = "Results Page"

    elif st.session_state.current_page == "Results Page":
        st.title("Home Page")
        st.write("View the latest updates tailored to your interests.")

        tabs = st.tabs(["Academic Research", "Clinical Trials", "Clinical News", "Regulatory News", "Provider News", "Drug News"])

        with tabs[0]:
            
            for i, article in enumerate(st.session_state.academic_research):
                if isinstance(article, dict):
                    with st.expander(article['Title']):
                        # Article metadata and URL link inside the dropdown
                        col1, col2, col3, col4 = st.columns([1, 1, 4, 1])
                        
                        with col1:
                            st.write(f"Source: {article['Source']}")
                        
                        with col2:
                            authors_formatted = [author["name"] for author in article["Authors"]]
                            st.write(f"Authors: {', '.join(authors_formatted)}")
                        
                        with col3:
                            st.write(f"Published: {article['PubDate']}")
                        
                        with col4:
                            st.write(f"[Read More]({article['URL']})")  # Displaying the URL link

                        # Now, place the buttons inside the dropdown as well
                        col5, col6 = st.columns([7, 1])
                        with col5:
                            if st.button(f"Get AI summary", key=f"ai_summary_{i}"):
                                with st.spinner("Generating AI summary..."):
                                    try:
                                        # Assuming 'summarize_content' function is already defined to generate summaries
                                        st.write(
                                            summarize_content(
                                                article["URL"],
                                                disease_interest=st.session_state.diseases_of_interest,
                                                drug_interest=st.session_state.drugs_of_interest,
                                            )
                                        )
                                    except Exception as e:
                                        st.error(f"An error occurred while fetching AI summary: {str(e)}")
                        
                        with col6:
                            st.button(f"Save Article", key=f"save_article_{i}")  # Placeholder for Save Article button

                else:
                    st.write(f"Article {i} is NOT a dictionary: {type(article)}")
                    continue  # Skip this article if it's not a dictionary




        # Clinical Trials Tab
        with tabs[1]:

            # Check if the clinical_trials DataFrame is not empty
            if not st.session_state.clinical_trials.empty:
                # Use the DataFrame from session state
                df_trials = st.session_state.clinical_trials
                
                # Display the entire dataframe in a scrollable table
                st.dataframe(df_trials)  # This will render a scrollable table with all the fields
                
            else:
                st.warning("No clinical trials found for this search.")

        # Industry News Tab
        with tabs[2]:
            
            # Get user inputs for filtering
            diseases_of_interest = st.session_state.diseases_of_interest.lower()
            drugs_of_interest = st.session_state.drugs_of_interest.lower()

            # Filter RSS entries based on diseases and drugs
            filtered_rss_entries = [
                entry for entry in st.session_state.rss_entries
                if diseases_of_interest in entry.get('title', '').lower() or
                diseases_of_interest in entry.get('summary', '').lower() or
                drugs_of_interest in entry.get('title', '').lower() or
                drugs_of_interest in entry.get('summary', '').lower()
            ]

            # Display filtered results or a message if no matches
            if filtered_rss_entries:
                for entry in filtered_rss_entries:
                    with st.expander(entry.get('title', 'No Title')):
                        summary_html = entry.get('summary', 'No Summary')
                        plain_summary = strip_html(summary_html)
                        st.write(plain_summary)
                        st.write(f"[Read More]({entry.get('link', '#')})")
            else:
                st.write("No relevant news articles found based on your input.")
            
        
        
        # Industry News Tab
        with tabs[3]:
            
            # Get user inputs for filtering
            diseases_of_interest = st.session_state.diseases_of_interest.lower()
            drugs_of_interest = st.session_state.drugs_of_interest.lower()

            # Filter RSS entries based on diseases and drugs
            filtered_rss2_entries = [
                entry for entry in st.session_state.rss2_entries
                if diseases_of_interest in entry.get('title', '').lower() or
                diseases_of_interest in entry.get('summary', '').lower() or
                drugs_of_interest in entry.get('title', '').lower() or
                drugs_of_interest in entry.get('summary', '').lower()
            ]

            # Display filtered results or a message if no matches
            if filtered_rss2_entries:
                for entry in filtered_rss2_entries:
                    with st.expander(entry.get('title', 'No Title')):
                        summary_html = entry.get('summary', 'No Summary')
                        plain_summary = strip_html(summary_html)
                        st.write(plain_summary)
                        st.write(f"[Read More]({entry.get('link', '#')})")
            else:
                st.write("No relevant news articles found based on your input.")
        
        # Industry News Tab
        with tabs[4]:
            
            # Get user inputs for filtering
            diseases_of_interest = st.session_state.diseases_of_interest.lower()
            drugs_of_interest = st.session_state.drugs_of_interest.lower()

            # Filter RSS entries based on diseases and drugs
            filtered_rss3_entries = [
                entry for entry in st.session_state.rss3_entries
                if diseases_of_interest in entry.get('title', '').lower() or
                diseases_of_interest in entry.get('summary', '').lower() or
                drugs_of_interest in entry.get('title', '').lower() or
                drugs_of_interest in entry.get('summary', '').lower()
            ]

            # Display filtered results or a message if no matches
            if filtered_rss3_entries:
                for entry in filtered_rss3_entries:
                    with st.expander(entry.get('title', 'No Title')):
                        summary_html = entry.get('summary', 'No Summary')
                        plain_summary = strip_html(summary_html)
                        st.write(plain_summary)
                        st.write(f"[Read More]({entry.get('link', '#')})")
            else:
                st.write("No relevant news articles found based on your input.")
        
        # Industry News Tab
        with tabs[5]:
            
            # Get user inputs for filtering
            diseases_of_interest = st.session_state.diseases_of_interest.lower()
            drugs_of_interest = st.session_state.drugs_of_interest.lower()

            # Filter RSS entries based on diseases and drugs
            filtered_rss4_entries = [
                entry for entry in st.session_state.rss4_entries
                if diseases_of_interest in entry.get('title', '').lower() or
                diseases_of_interest in entry.get('summary', '').lower() or
                drugs_of_interest in entry.get('title', '').lower() or
                drugs_of_interest in entry.get('summary', '').lower()
            ]

            # Display filtered results or a message if no matches
            if filtered_rss4_entries:
                for entry in filtered_rss4_entries:
                    with st.expander(entry.get('title', 'No Title')):
                        summary_html = entry.get('summary', 'No Summary')
                        plain_summary = strip_html(summary_html)
                        st.write(plain_summary)
                        st.write(f"[Read More]({entry.get('link', '#')})")
            else:
                st.write("No relevant news articles found based on your input.")


except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
