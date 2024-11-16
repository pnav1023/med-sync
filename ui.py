import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content

# Configure page settings
st.set_page_config(page_title="Med Sync", layout="wide")

# Initialize session state for navigation and inputs
if "current_page" not in st.session_state:
    st.session_state.current_page = "Welcome"
if "user_salutation" not in st.session_state:
    st.session_state.user_salutation = ""
if "user_firstname" not in st.session_state:
    st.session_state.user_firstname = ""
if "user_lastname" not in st.session_state:
    st.session_state.user_lastname = ""
if "diseases_of_interest" not in st.session_state:
    st.session_state.diseases_of_interest = ""
if "drugs_of_interest" not in st.session_state:
    st.session_state.drugs_of_interest = ""
if "additional_keywords" not in st.session_state:
    st.session_state.additional_keywords = ""
if "provider_role" not in st.session_state:
    st.session_state.provider_role = "Clinician"
if "specialty" not in st.session_state:
    st.session_state.specialty = ""
if "patient_age_group" not in st.session_state:
    st.session_state.patient_age_group = "0-18"
if "res" not in st.session_state:
    st.session_state.res = []
if "filtered_res" not in st.session_state:
    st.session_state.filtered_res = []

try:
    # Navigation Logic
    if st.session_state.current_page == "Welcome":
        st.title("Welcome to Med Sync!")
        st.write("""
            Med Sync is designed to keep you up-to-date on the latest in healthcare, tailored specifically to your specialty and interests.
            With Med Sync, you’ll receive real-time updates on everything from new clinical guidelines and research to clinical trial results and industry news.

            You can personalize what you see based on the diseases, drugs, or fields you’re most interested in, making it easier to stay informed on what matters to you. 
            Plus, Med Sync lets you save articles, add personal notes, and quickly filter by specialty or topic so that you’re always on top of the latest developments in your field.
        """)

        if st.button("Get Started"):
            st.session_state.current_page = "Input Page 1"

    elif st.session_state.current_page == "Input Page 1":
        st.title("Personal Input Page")
        st.write("Provide inputs below:")

        # Input fields with session state
        st.session_state.user_salutation = st.text_input(
            "Enter your salutation", value=st.session_state.user_salutation
        )
        st.session_state.user_firstname = st.text_input(
            "Enter your first name", value=st.session_state.user_firstname
        )
        st.session_state.user_lastname = st.text_input(
            "Enter your last name", value=st.session_state.user_lastname
        )

        if st.session_state.user_salutation and st.session_state.user_firstname and st.session_state.user_lastname:
            st.write(f"Welcome {st.session_state.user_salutation} {st.session_state.user_firstname} {st.session_state.user_lastname}!")

        if st.button("Next Page"):
            st.session_state.current_page = "Input Page 2"

    elif st.session_state.current_page == "Input Page 2":
        st.title("Information Input Page")
        st.write("Provide your information below:")

        # Input fields with session state
        st.session_state.provider_role = st.selectbox(
            "Select your role",
            ["Clinician", "Researcher", "Healthcare Administrator", "Student", "Other Professional"],
            index=["Clinician", "Researcher", "Healthcare Administrator", "Student", "Other Professional"].index(
                st.session_state.provider_role
            )
        )
        st.session_state.specialty = st.text_input(
            "Enter your specialty", value=st.session_state.specialty
        )
        st.session_state.patient_age_group = st.selectbox(
            "Select patient's age group",
            ["0-18", "19-35", "36-50", "51-70", "71+"],
            index=["0-18", "19-35", "36-50", "51-70", "71+"].index(st.session_state.patient_age_group)
        )
        st.session_state.diseases_of_interest = st.text_input(
            "Enter diseases of interest (separate by commas if multiple)", value=st.session_state.diseases_of_interest
        )
        st.session_state.drugs_of_interest = st.text_input(
            "Enter drugs of interest (separate by commas if multiple)", value=st.session_state.drugs_of_interest
        )
        st.session_state.additional_keywords = st.text_area(
            "Enter additional keywords (separate by commas if multiple)",
            value=st.session_state.additional_keywords,
            help="Provide any additional keywords relevant to your research."
        )

        if st.button("Next Page"):
            st.session_state.current_page = "Home Page"

    elif st.session_state.current_page == "Home Page":
        st.title("Med Sync")
        st.write("Search for the latest articles below:")

        # Combine user inputs into a tailored search query
        user_inputs = []
        if st.session_state.diseases_of_interest:
            user_inputs.append(st.session_state.diseases_of_interest)
        if st.session_state.drugs_of_interest:
            user_inputs.append(st.session_state.drugs_of_interest)

        # Create a search string
        search_string = ", ".join(filter(None, user_inputs))

        # Prepopulate results if not already done
        if not st.session_state.res:
            st.session_state.res = search_pubmed(search_string or "latest healthcare updates", 10)

        # Filter results based on user search query
        search_query = st.text_input("Search articles", value=search_string)
        st.session_state.filtered_res = [
            article for article in st.session_state.res if search_query.lower() in article["Title"].lower()
        ]

        for i, article in enumerate(st.session_state.filtered_res):
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
                            provider_role=st.session_state.provider_role,
                            specialty=st.session_state.specialty,
                            age_group=st.session_state.patient_age_group,
                            disease_interest=st.session_state.diseases_of_interest,
                            drug_interest=st.session_state.drugs_of_interest,
                            additional_keywords=st.session_state.additional_keywords
                        )
                    )
                with col6:
                    for j, pubtype in enumerate(article["PubType"]):
                        st.button(f"{pubtype}", key=f"{i}-{j}", disabled=True)

    else:
        st.error("Page not found. Returning to Welcome page.")
        st.session_state.current_page = "Welcome"

except Exception as e:
    st.error(f"An error occurred: {e}")
