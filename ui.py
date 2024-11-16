import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content

# Configure page settings
st.set_page_config(page_title="Med Sync", layout="wide")

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Welcome"

try:
    # Navigation Logic
    if st.session_state.current_page == "Welcome":
        # Title and Welcome Text
        st.title("Welcome to Med Sync!")
        st.write(
            """
            Med Sync is designed to keep you up-to-date on the latest in healthcare, tailored specifically to your specialty and interests. 
            With Med Sync, you’ll receive real-time updates on everything from new clinical guidelines and research to clinical trial results and industry news.

            You can personalize what you see based on the diseases, drugs, or fields you’re most interested in, making it easier to stay informed on what matters to you. 
            Plus, Med Sync lets you save articles, add personal notes, and quickly filter by specialty or topic so that you’re always on top of the latest developments in your field.
            """
        )
        st.image("welcome_image.png", caption="Stay in sync with Med Sync!", use_column_width=True)

        # Button to navigate to Input Page 1
        if st.button("Get Started"):
            st.session_state.current_page = "Input Page 1"

    elif st.session_state.current_page == "Input Page 1":
        # Input Page 1 Content
        st.title("Personal Input Page")
        st.write("Provide inputs below:")

        # Example input fields
        user_salutation = st.text_input("Enter your salutation")
        user_firstname = st.text_input("Enter your first name")
        user_lastname = st.text_input("Enter your last name")
        
        if user_salutation and user_firstname and user_lastname:
            st.write(f"Welcome {user_salutation} {user_firstname} {user_lastname}!")

        # Navigation to Input Page 2
        if st.button("Next Page"):
            st.session_state.current_page = "Input Page 2"

    elif st.session_state.current_page == "Input Page 2":
        # Input Page 2 Content
        st.title("Information Input Page")
        st.write("Provide your information below:")

        # Input fields for role, specialty, and interests
        provider_role = st.selectbox(
            "Select your role",
            ["Clinician", "Researcher", "Healthcare Administrator", "Student", "Other Professional"]
        )
        specialty = st.text_input("Enter your specialty")
        patient_age_group = st.selectbox(
            "Select patient's age group",
            ["0-18", "19-35", "36-50", "51-70", "71+"]
        )
        diseases_of_interest = st.text_input(
            "Enter diseases of interest (separate by commas if multiple)"
        )
        drugs_of_interest = st.text_input(
            "Enter drugs of interest (separate by commas if multiple)"
        )
        additional_keywords = st.text_area(
            "Enter additional keywords (separate by commas if multiple)",
            help="Provide any additional keywords relevant to your research."
        )

        # Navigation to Home Page
        if st.button("Next Page"):
            st.session_state.current_page = "Home Page"

    elif st.session_state.current_page == "Home Page":
        st.title("Med Sync")
        st.write("Search for the latest articles below:")

        ss = st.session_state

        if "res" not in ss:
            ss.res = []
        if "filtered_res" not in ss:
            ss.filtered_res = []

        # Combine user inputs into a tailored search query
        user_inputs = []
        if ss.get("diseases_of_interest"):
            user_inputs.append(ss.diseases_of_interest)
        if ss.get("drugs_of_interest"):
            user_inputs.append(ss.drugs_of_interest)

        # Create a search string by joining all inputs
        search_string = ", ".join(filter(None, user_inputs))

        # Prepopulate results if not already done
        if not ss.res:
            ss.res = search_pubmed(search_string or "latest healthcare updates", 10)

        # Filter results based on user search query
        search_query = st.text_input("Search articles", value=search_string)
        ss.filtered_res = [article for article in ss.res if search_query.lower() in article["Title"].lower()]

        for i, article in enumerate(ss.filtered_res):
            with st.expander(f"{article['Title']}"):
                col1, col2, col3, col4 = st.columns([1, 1, 4, 1])
                with col1:
                    st.write(f"[Read full article]({article['URL']})")
                with col2:
                    st.write(f"Source: {article['Source']}")
                with col3:
                    authors_formatted = [author["name"] for author in article["Authors"]]
                    st.write(f"Authors: {', '.join(authors_formatted)}")
                with col4:
                    st.write(f"Published: {article['PubDate']}")

                col5, col6 = st.columns([7, 1])
                with col5:
                    if st.button(f"Get AI summary", key=i):
                        st.write(
                            summarize_content(
                                article["URL"],
                                provider_role=ss.get("provider_role", "healthcare professional"),
                                specialty=ss.get("specialty", "general"),
                                age_group=ss.get("patient_age_group", "all ages"),
                                disease_interest=ss.get("diseases_of_interest", ""),
                                drug_interest=ss.get("drugs_of_interest", ""),
                                additional_keywords=ss.get("additional_keywords", [])
                            )
                        )
                with col6:
                    for j, pubtype in enumerate(article["PubType"]):
                        st.button(f"{pubtype}", key=f"{i}-{j}", disabled=True)

    else:
        # Handle unknown pages
        st.error("Page not found. Returning to Welcome page.")
        st.session_state.current_page = "Welcome"

except Exception as e:
    st.error(f"An error occurred: {e}")
