import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content
import pandas as pd
import feedparser
from pytrials.client import ClinicalTrials
from html.parser import HTMLParser
from rss import fetch_rss_feed
from trials import fetch_clinical_trials
from datetime import datetime
from spellchecker import SpellChecker
from fetch_tweets import display_tweets_dashboard




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
if 'saved_articles' not in st.session_state:
    st.session_state.saved_articles = []  # Initialize as an empty list if not already initialized


##pages###############################################################
try:
    if st.session_state.current_page == "Welcome":
        st.title("Welcome to Med Sync!")
        st.write("""
            Med Sync is designed to keep you up-to-date on the latest in healthcare, tailored specifically to your specialty and interests.
            With Med Sync, you’ll receive real-time updates on everything from new clinical guidelines and research to clinical trial results
            to industry and regulatory news.

            You can personalize what you see based on the diseases, drugs, or fields you’re most interested in, making it easier to stay informed on what matters to you. 
            Plus, Med Sync lets you save articles, add personal notes, and quickly filter by specialty or topic so that you’re always on top of the latest developments in your field.
        """)

        if st.button("Get Started"):
            st.session_state.current_page = "Input Page"

    elif st.session_state.current_page == "Input Page":
        st.title("Personal Input Page")

        # Initialize spell checker
        spell = SpellChecker()

        # Function to check for spelling errors
        def check_spelling(text):
            words = text.split()  # Split input into words
            misspelled = spell.unknown(words)  # Find unknown words (misspelled)
            
            suggestions = {}
            for word in misspelled:
                suggestions[word] = spell.correction(word)  # Suggest a correction
            
            return suggestions
        
        
        
        st.session_state.role = st.selectbox(
            "Select your Role (Required):",
            [
                "Physician",
                "Nurse Practitioner",
                "Physician Assistant",
                "Specialist (e.g., Cardiologist, Oncologist)",
                "Resident/Fellow",
                "Medical Student",
                "Other (Specify)"
            ]
        )
        
        # Required Inputs
        # Required Input: Specialty
        st.session_state.specialty = st.selectbox(
            "Select your Specialty (Required):",
            [
                "General Practitioner",
                "Internal Medicine",
                "Cardiology",
                "Oncology",
                "Pediatrics",
                "Neurology",
                "Orthopedics",
                "Surgery - General",
                "Surgery - Cardiothoracic",
                "Surgery - Neurosurgery",
                "Dermatology",
                "Endocrinology",
                "Gastroenterology",
                "Hematology",
                "Infectious Disease",
                "Nephrology",
                "Obstetrics and Gynecology",
                "Ophthalmology",
                "Otolaryngology (ENT)",
                "Pathology",
                "Psychiatry",
                "Pulmonology",
                "Radiology",
                "Immunology",
                "Urology",
                "Anesthesiology",
                "Emergency Medicine",
                "Other"
            ]
        )
        # If "Other" is selected, prompt the user for additional input
        if st.session_state.specialty == "Other (Specify)":
            specialty_other = st.text_input("Please specify your specialty:")
            if specialty_other.strip():  # Ensure it's not empty
                st.session_state.specialty = specialty_other

        # Optional Inputs
        st.session_state.patient_demographics = st.text_area(
            "Enter Patient Demographics (Optional):",
            "Age group, conditions, urban/rural, socioeconomic factors, etc."
        )

        # Initialize session state variable if not already set
        if "update_frequency" not in st.session_state:
            st.session_state.update_frequency = "Weekly"  # Default value

        # Create a radio button with a default selection
        st.session_state.update_frequency = st.radio(
            "Preferred Update Frequency (Required):",
            ["Daily", "Weekly", "Monthly"],
            index=["Daily", "Weekly", "Monthly"].index(st.session_state.update_frequency)
        )

        st.session_state.geography = st.text_input(
            "Enter your Geography (Optional):",
            "Country, State, City, or Region"
        )
        
        # Existing Inputs
        st.session_state.diseases_of_interest = st.text_input("Enter diseases of interest:")
        st.session_state.drugs_of_interest = st.text_input("Enter drugs of interest (include all relevant names if possible):")
        st.session_state.keywords = st.text_input("Enter keywords of interest (optional):")
        
        # Perform spell check on all input text
        disease_suggestions = check_spelling(st.session_state.diseases_of_interest)
        drug_suggestions = check_spelling(st.session_state.drugs_of_interest)
        keyword_suggestions = check_spelling(st.session_state.keywords)

        # Check if all required inputs are filled out
        if not all([st.session_state.role, st.session_state.specialty, st.session_state.update_frequency, 
                    st.session_state.diseases_of_interest, st.session_state.drugs_of_interest]):
            st.error("Please fill out all required fields.")
        else:
            # Proceed with the application logic
            st.write("All required fields are filled out.")
            
            # Show spell-check suggestions if any
            if disease_suggestions:
                st.write(f"Spelling suggestions for Diseases of Interest: {disease_suggestions}")
            if drug_suggestions:
                st.write(f"Spelling suggestions for Drugs of Interest: {drug_suggestions}")
            if keyword_suggestions:
                st.write(f"Spelling suggestions for Keywords: {keyword_suggestions}")
                
        
        ## content retrieval ###################################################################################################################################################
        
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
                
                rss_url5 = "https://edhub.ama-assn.org/rss/site_9/0_5614.xml"
                st.session_state.rss5_entries = fetch_rss_feed(rss_url5)
                
                rss_url6 = "https://www.biopharmadive.com/feeds/news/" 
                st.session_state.rss6_entries = fetch_rss_feed(rss_url6)
                
                rss_url4 = "https://www.statnews.com/category/pharma/feed/"
                st.session_state.rss4_entries = fetch_rss_feed(rss_url4)
                
                
                ##fetch regulatory news
                rss_url2 = "https://thehill.com/policy/healthcare/feed/"
                st.session_state.rss2_entries = fetch_rss_feed(rss_url2) 
                
                rss_url7 = "https://edhub.ama-assn.org/rss/site_9/0_44020.xml"
                st.session_state.rss7_entries = fetch_rss_feed(rss_url7)
                
                rss_url8 = "https://www.statnews.com/category/politics/feed/"
                st.session_state.rss8_entries = fetch_rss_feed(rss_url8)
                
                
                ##fetch provider news
                
                rss_url10 = "https://edhub.ama-assn.org/rss/site_9/0_5672.xml"
                st.session_state.rss10_entries = fetch_rss_feed(rss_url10)
                
                rss_url12 = "https://edhub.ama-assn.org/rss/site_9/0_46328.xml"
                st.session_state.rss12_entries = fetch_rss_feed(rss_url12)
                
                rss_url13 = "https://edhub.ama-assn.org/rss/site_9/0_44067.xml"
                st.session_state.rss13_entries = fetch_rss_feed(rss_url13)
                
                rss_url14 = "https://edhub.ama-assn.org/rss/site_9/0_45309.xml"
                st.session_state.rss14_entries = fetch_rss_feed(rss_url14)
                
                rss_url15 = "https://jamaclinicalreviews.libsyn.com/rss"
                st.session_state.rss15_entries = fetch_rss_feed(rss_url15)
                
                rss_url16 = "https://edhub.ama-assn.org/rss/site_9/0_45306.xml"
                st.session_state.rss16_entries = fetch_rss_feed(rss_url16)
                
                
                
                ##fetch drug news
                rss_url9 = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch/rss.xml"
                st.session_state.rss9_entries = fetch_rss_feed(rss_url9)
                
                rss_url17 = "https://jamanetwork.com/rss/site_9/0_42095.xml"
                st.session_state.rss17_entries = fetch_rss_feed(rss_url17)
                
                

            st.session_state.current_page = "Results Page"
            
            

##main app UI#########################################################################################


    elif st.session_state.current_page == "Results Page":
        st.title("Med Sync")
        st.write("View the latest updates tailored to your interests.")

        tabs = st.tabs(["Home Page", "Clinical Research and Trials", "Industry News", "Regulatory News", 
                        "Provider News & Education"
                        , "Critical Alerts", "Settings", "Saved Articles", "Help & Info"])

        with tabs[0]:
                # Sample quick overview/dashboard for Home Page
            st.title("Dashboard Overview")
            
            # Display some basic stats or quick data
            st.subheader(f"Quick View of Your Feed (Updated {st.session_state.update_frequency}) ")
            
            # Example: Display the number of articles or updates in different categories
            new_articles = len(st.session_state.rss_entries)  # Placeholder for RSS articles count
            clinical_trials = len(st.session_state.rss4_entries)  # Placeholder for clinical trials count
            industry_news = len(st.session_state.rss5_entries)  # Placeholder for industry news count
            regulatory_news = len(st.session_state.rss6_entries)  # Placeholder for regulatory news count
            
            # Display quick stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("New Articles", new_articles)
            
            with col2:
                st.metric("Clinical Trials", clinical_trials)
            
            with col3:
                st.metric("Industry News", industry_news)
            
            with col4:
                st.metric("Regulatory News", regulatory_news)
            
            # Display recently saved articles or other relevant info
            st.subheader("Recent Activity")
            if len(st.session_state.saved_articles) > 0:
                st.write("You have recent saved articles:")
                for article in st.session_state.saved_articles[-5:]:  # Show last 5 saved articles
                    st.write(f"- {article['title']} (Saved on {article['saved_on']})")
            else:
                st.write("No recent saved articles.")
            
            
            ##exception handling 
            
            # Display a list of quick links to other important sections
            st.subheader("Twitter Updates")
            # Retrieve session state values
            # Retrieve session state values
            
            
            # Convert session state values to strings (if not already)
            """ user_specialty = str(st.session_state.specialty)  # User's medical specialty

            # Convert diseases_of_interest, drugs_of_interest, and additional_keywords into lists of strings
            # Ensure that the input is cleaned up (strip spaces) before splitting by commas
            diseases_of_interest = str(st.session_state.diseases_of_interest).split(",")  # Splitting by commas for multiple entries
            drugs_of_interest = str(st.session_state.drugs_of_interest).split(",")  # Splitting by commas for multiple entries
            additional_keywords = str(st.session_state.keywords).split(",")  # Splitting by commas for multiple entries

            # Strip any extra whitespace from each keyword
            diseases_of_interest = [disease.strip() for disease in diseases_of_interest if disease.strip()]
            drugs_of_interest = [drug.strip() for drug in drugs_of_interest if drug.strip()]
            additional_keywords = [keyword.strip() for keyword in additional_keywords if keyword.strip()]

            # Combine all keywords (disease, drugs, specialty, custom keywords) into a single list
            keywords = diseases_of_interest + drugs_of_interest + [user_specialty] + additional_keywords

            # Ensure all elements in the list are strings (in case any elements are non-strings)
            keywords = [str(keyword) for keyword in keywords]

            # Join the list of keywords into a single string for the API query, separating by "OR"
            keywords_str = " OR ".join(keywords)

            # Display the generated string of keywords for debugging purposes
            st.write(f"Generated keywords string: {keywords_str}")

            # Call the function to display tweets, passing the keywords string and specialty
            display_tweets_dashboard(keywords_str)"""



            ##exception handling 
            
            
            
            
            # Optionally display a system status or recent alerts
            st.subheader("System Status")
            st.write("All systems are operational. No critical issues detected.")
        
        with tabs[1]:  # Main Tab 1 for Academic Research
            sub_tabs = st.tabs(["Academic Research", "Clinical Trials"])  # Sub-tabs under Tab 1

            # Sub-Tab 1: Academic Research
            with sub_tabs[0]:
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

                            # Buttons inside the dropdown
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

            # Sub-Tab 2: Clinical Trials
            with sub_tabs[1]:
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
            specialty = st.session_state.specialty.lower()  # Removed parentheses
            keywords = st.session_state.keywords.lower() 



                        # Display a legend above the results
            st.markdown(
                """
                <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                    <strong>Legend:</strong>
                    <ul style="list-style-type: none; padding: 0;">
                        <li style="margin-bottom: 5px;">
                            <div style="display: inline-block; width: 15px; height: 15px; 
                                        background-color: green; border-radius: 50%; margin-right: 10px;"></div>
                            <span>3-4 matches: Highly relevant</span>
                        </li>
                        <li>
                            <div style="display: inline-block; width: 15px; height: 15px; 
                                        background-color: yellow; border-radius: 50%; margin-right: 10px;"></div>
                            <span>1-2 matches: Moderately relevant</span>
                        </li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Combine entries
            combined_entries = (
                st.session_state.rss_entries +
                st.session_state.rss4_entries +
                st.session_state.rss5_entries +
                st.session_state.rss6_entries
            )

            # Initialize an empty list to store tagged entries
            tagged_entries = []

            # Helper function to calculate matches and assign colors
            def tag_entry(entry, diseases_of_interest, drugs_of_interest, specialty, keywords):
                match_count = 0
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()

                # Check for matches in each category
                if diseases_of_interest in title or diseases_of_interest in summary:
                    match_count += 1
                if drugs_of_interest in title or drugs_of_interest in summary:
                    match_count += 1
                if specialty in title or specialty in summary:
                    match_count += 1
                if keywords in title or keywords in summary:
                    match_count += 1

                # Assign color based on match count
                if match_count >= 3:
                    color = "green"
                elif 1 <= match_count <= 2:
                    color = "yellow"
                else:
                    color = "gray"  # Default for no match

                return {"entry": entry, "match_count": match_count, "color": color}

            # Iterate through combined entries and calculate matches
            for entry in combined_entries:
                tagged_entries.append(
                    tag_entry(entry, diseases_of_interest, drugs_of_interest, specialty, keywords)
                )
            
            # Add a filter for sorting results
            filter_option = st.selectbox(
                "Sort results by:",
                options=["Most Recent", "Relevancy (Number of Matches)"],
                index=0  # Default to "Most Recent"
            )

            # Helper function to parse dates
            def parse_date(entry):
                date_str = entry.get("published", "")  # Replace 'published' with the correct key for your date field
                try:
                    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")  # Adjust format to match your date strings
                except ValueError:
                    return datetime.min  # Fallback for invalid or missing dates
            
            
            # Sort tagged entries based on the selected filter
            if filter_option == "Most Recent":
                tagged_entries.sort(key=lambda x: x["entry"].get("published", ""), reverse=True)  # Assuming 'published' field exists
            elif filter_option == "Relevancy (Number of Matches)":
                tagged_entries.sort(key=lambda x: x["match_count"], reverse=True)
            
            # Display results
            if tagged_entries:
                for tagged_entry in tagged_entries:
                    entry = tagged_entry["entry"]
                    color = tagged_entry["color"]
                    match_count = tagged_entry["match_count"]

                    # Use Streamlit components to display the entry
                    with st.expander(f"{entry.get('title', 'No Title')} ({match_count} matches)"):
                        # HTML for a colored circle in the top-right corner
                        st.markdown(
                            f"""
                            <div style="position: relative; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                                <div style="position: absolute; top: 5px; right: 5px; width: 15px; height: 15px; 
                                            background-color: {color}; border-radius: 50%;"></div>
                                <div style="margin-top: 10px;">
                                    <p>{strip_html(entry.get('summary', 'No Summary'))}</p>
                                    <a href="{entry.get('link', '#')}" target="_blank">Read More</a>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.write("No relevant news articles found based on your input.")


        
        # Regulatory News Tab
        with tabs[3]:
            
            # Get user inputs for filtering
            diseases_of_interest = st.session_state.diseases_of_interest.lower()
            drugs_of_interest = st.session_state.drugs_of_interest.lower()
            specialty = st.session_state.specialty.lower()  # Removed parentheses
            keywords = st.session_state.keywords.lower() 
            
            # Combine entries
            combined_entries = st.session_state.rss2_entries + st.session_state.rss7_entries + st.session_state.rss8_entries

            # Filter RSS entries based on diseases and drugs
            filtered_rss2_entries = [
                entry for entry in combined_entries
                if (diseases_of_interest in entry.get('title', '').lower() or
                        diseases_of_interest in entry.get('summary', '').lower() or
                        drugs_of_interest in entry.get('title', '').lower() or
                        drugs_of_interest in entry.get('summary', '').lower()) and
                    (specialty in entry.get('title', '').lower() or
                    specialty in entry.get('summary', '').lower()) and
                    (keywords in entry.get('title', '').lower() or
                    keywords in entry.get('summary', '').lower())
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
        
        
        
        # Provider News and Education
        with tabs[4]:
            
            # Get user inputs for filtering
            diseases_of_interest = st.session_state.diseases_of_interest.lower()
            drugs_of_interest = st.session_state.drugs_of_interest.lower()
            specialty = st.session_state.specialty.lower()  # Removed parentheses
            keywords = st.session_state.keywords.lower() 

            # Combine entries
            combined_entries = st.session_state.rss10_entries + st.session_state.rss12_entries + st.session_state.rss13_entries + st.session_state.rss14_entries + st.session_state.rss15_entries + st.session_state.rss16_entries
            
            # Filter RSS entries based on diseases and drugs
            filtered_rss3_entries = [
                entry for entry in combined_entries
                if (diseases_of_interest in entry.get('title', '').lower() or
                            diseases_of_interest in entry.get('summary', '').lower() or
                            drugs_of_interest in entry.get('title', '').lower() or
                            drugs_of_interest in entry.get('summary', '').lower()) and
                        (specialty in entry.get('title', '').lower() or
                        specialty in entry.get('summary', '').lower()) and
                        (keywords in entry.get('title', '').lower() or
                        keywords in entry.get('summary', '').lower())
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
        
        # critical alerts
        with tabs[5]:
            
            # Get user inputs for filtering
            diseases_of_interest = st.session_state.diseases_of_interest.lower()
            drugs_of_interest = st.session_state.drugs_of_interest.lower()
            specialty = st.session_state.specialty.lower()  # Removed parentheses
            keywords = st.session_state.keywords.lower() 
            
            # Combine entries
            combined_entries = st.session_state.rss9_entries + st.session_state.rss17_entries
            
            
            # Filter RSS entries based on diseases and drugs
            filtered_rss4_entries = [
                entry for entry in combined_entries
                if (diseases_of_interest in entry.get('title', '').lower() or
                            diseases_of_interest in entry.get('summary', '').lower() or
                            drugs_of_interest in entry.get('title', '').lower() or
                            drugs_of_interest in entry.get('summary', '').lower()) and
                        (specialty in entry.get('title', '').lower() or
                        specialty in entry.get('summary', '').lower()) and
                        (keywords in entry.get('title', '').lower() or
                        keywords in entry.get('summary', '').lower())
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

        # critical alerts
        with tabs[6]:
            
            st.write("Work in progress")
            
        with tabs[7]:
            st.title("Saved Articles")

            # Check if there are any saved articles
            if st.session_state.saved_articles:
                st.subheader("Your Saved Articles")
                
                # Display saved articles
                for article in st.session_state.saved_articles:
                    with st.expander(article['title']):
                        st.write(f"**Summary**: {article.get('summary', 'No summary available.')}")
                        st.write(f"[Read more]({article.get('link', '#')})")
                        st.write(f"Saved on: {article.get('saved_on', 'Unknown')}")
                        
                        # Optionally add an option to remove or unsave an article
                        if st.button(f"Remove {article['title']}"):
                            st.session_state.saved_articles.remove(article)
                            st.success(f"Article '{article['title']}' has been removed from saved articles.")
                            st.experimental_rerun()  # Re-run to reflect the updated list

            else:
                st.write("You don't have any saved articles yet.")
                    
                    
        with tabs[8]:
            
            st.write("Work in progress")

except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
