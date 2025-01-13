import streamlit as st
from pub_med_script import search_pubmed
from ai_summary import summarize_content
import pandas as pd
import feedparser
from pytrials.client import ClinicalTrials
from rss import fetch_rss_feed
from trials import fetch_clinical_trials
from datetime import datetime
import os
from supabase import create_client, Client
from datetime import datetime
from database import sign_in, sign_up, get_saved_articles, save_article, store_user_inputs, init_supabase_client
import asyncio
from touch_up import HTMLStripper,strip_html, case_insensitive_match
import re

# Configure page settings
st.set_page_config(page_title="Med Sync", layout="wide")

# Initialize the Supabase client
# URL = "https://liteepuobwwnfggrujwy.supabase.co"
# KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxpdGVlcHVvYnd3bmZnZ3J1and5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMxOTU5MjQsImV4cCI6MjA0ODc3MTkyNH0.AF_oj_BOaMuxINCKv-EhtMUAcqpUO_KI51NI6CfPzA4"

if "supabase_client" not in st.session_state:
    try:
        st.session_state.supabase_client = init_supabase_client()
        print("Supabase client initialized successfully.")
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")

# Access the Supabase client when needed
supabase = st.session_state.supabase_client

if "auth_session" not in st.session_state:
    st.session_state.auth_session = None  # or set it to some default value



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

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "Sign in"  # Start at the Sign-In/Sign-Up page

if "user_id" not in st.session_state:
    st.session_state.user_id = None  # Track authenticated user ID
    
    
# At the start of your app, add this to handle URL parameters (for password reset)
try:
    # Get all URL parameters
    if "access_token" in st.query_params and "refresh_token" in st.query_params and "type" in st.query_params:
        # This means we're coming from a password reset email
        access_token = st.query_params["access_token"]
        refresh_token = st.query_params["refresh_token"]
        
        # Set the session to use these tokens
        supabase.auth.set_session(access_token, refresh_token)
        
        # Switch to reset password page
        st.session_state.current_page = "Reset Password"
        st.rerun()
except Exception as e:
    print(f"Error in recovery flow: {e}")


##pages###############################################################
try:
    if st.session_state.current_page == "Welcome":
        st.title("Welcome to Kairos!")
        st.write("""
            
            In ancient Greek, "Kairos" symbolizes the perfect, opportune moment—a concept that embodies the mission of this app.
            
            Kairos keeps you ahead with real-time updates tailored to your specialty and interests. From clinical guidelines and research to trial results, industry trends, and regulatory news, you’ll have everything you need at your fingertips.

            Personalize your feed, save articles, add notes, and filter by topic to stay on top of what truly matters. Stay informed, stay ready—welcome to Kairos.
        """)

        if st.button("Proceed to Sign in"):
            st.session_state.current_page = "Sign in"
            st.rerun()
            
            
    elif st.session_state.current_page == "Sign in":
        st.title("Sign in to your account")
        st.write("Please sign in or create your account below:")
        
        # Authentication Section
        auth_option = st.radio("Select an option:", ("Sign In", "Sign Up", "Forgot Password"))
        
        if auth_option in ["Sign In", "Sign Up"]:
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

    
        
        if auth_option == "Sign Up":
                if st.button("Create Account"):
                    if email and password:
                        try:
                            # Directly call the sign-up method
                            response = supabase.auth.sign_up({"email": email, "password": password})
                            print("Sign-up response:", response)  # Debugging line

                            if response.user:
                                # Log the user in automatically after sign-up
                                user, access_token = sign_in(st.session_state.supabase_client, email, password)
                                if user and access_token:
                                    st.write("Success! Press create account button again to proceed!")
                                    st.session_state.current_page = "Input Page"
                                    st.session_state.auth_session = access_token
                                    st.session_state.user_id = str(user.id)
                                    st.rerun()

                                    if "auth_session" in st.session_state and st.session_state.auth_session:
                                        print("User is logged in.")
                                        print("Session state contains:", st.session_state)  # To confirm the session values
                                        # Proceed with authenticated actions
                                    else:
                                        print("No user session found.")
                                else:
                                    st.write("Please check your email, confirm, and sign up again")
                            elif response.error:
                                if "already been taken" in response.error.message.lower():
                                    st.error("Email already exists. Please log in or reset your password.")
                                else:
                                    st.error(response.error.message)

                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                    else:
                        st.warning("Please provide both email and password.")
                    
        elif auth_option == "Forgot Password":
            reset_email = st.text_input("Email", placeholder="Enter your email")
            if st.button("Reset Password"):
                if reset_email:
                    try:
                        # Call Supabase password reset method
                        response = supabase.auth.reset_password_email(reset_email)
                        st.success("If an account exists with this email, you will receive password reset instructions.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                else:
                    st.warning("Please enter your email address.")            
        
        
        # Your existing page logic...
        elif st.session_state.current_page == "Reset Password":
            st.title("Reset Your Password")
            new_password = st.text_input("New Password", type="password", placeholder="Enter your new password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your new password")
            
            if st.button("Update Password"):
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        try:
                            # Update the user's password
                            response = supabase.auth.update_user({
                                "password": new_password
                            })
                            
                            if response.user:
                                st.success("Password successfully updated! You can now sign in with your new password.")
                                # Clear the session
                                supabase.auth.sign_out()
                                st.session_state.current_page = "Sign in"
                                st.rerun()
                            else:
                                st.error("Error updating password. Please try again or request a new reset link.")
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                            print(f"Password reset error: {e}")  # For debugging
                    else:
                        st.error("Passwords do not match!")
                else:
                    st.warning("Please fill in both password fields.")
                
        
        ##
        elif auth_option == "Sign In":
            if st.button("Log In"):
                if email and password:
                    user, access_token = sign_in(st.session_state.supabase_client, email, password)
                    if user and access_token:
                        st.session_state.user_id = str(user.id)
                        st.session_state.auth_session = access_token


                        if 'supabase_client' not in st.session_state:
                            st.session_state.supabase_client = None

                        # Initialize data variables
                        if 'role' not in st.session_state:
                            st.session_state.role = ""
                        if 'specialty' not in st.session_state:
                            st.session_state.specialty = ""
                        if 'patient_demographics' not in st.session_state:
                            st.session_state.patient_demographics = ""
                        if 'update_frequency' not in st.session_state:
                            st.session_state.update_frequency = "Weekly"
                        if 'geography' not in st.session_state:
                            st.session_state.geography = ""
                        if 'diseases_of_interest' not in st.session_state:
                            st.session_state.diseases_of_interest = ""
                        if 'drugs_of_interest' not in st.session_state:
                            st.session_state.drugs_of_interest = ""
                        if 'keywords' not in st.session_state:
                            st.session_state.keywords = ""

                        # Initialize Industry News
                        if "i_news1_entries" not in st.session_state:
                            st.session_state.i_news1_entries = []

                        if "i_news2_entries" not in st.session_state:
                            st.session_state.i_news2_entries = []

                        if "i_news3_entries" not in st.session_state:
                            st.session_state.i_news3_entries = []

                        if "i_news4_entries" not in st.session_state:
                            st.session_state.i_news4_entries = []

                        # Initialize Regulatory News
                        if "r_news1_entries" not in st.session_state:
                            st.session_state.r_news1_entries = []

                        if "r_news2_entries" not in st.session_state:
                            st.session_state.r_news2_entries = []

                        if "r_news3_entries" not in st.session_state:
                            st.session_state.r_news3_entries = []

                        # Initialize Provider News
                        if "p_news1_entries" not in st.session_state:
                            st.session_state.p_news1_entries = []

                        if "p_news2_entries" not in st.session_state:
                            st.session_state.p_news2_entries = []

                        if "p_news3_entries" not in st.session_state:
                            st.session_state.p_news3_entries = []

                        # Initialize Drug News
                        if "d_news1_entries" not in st.session_state:
                            st.session_state.d_news1_entries = []

                        if "d_news2_entries" not in st.session_state:
                            st.session_state.d_news2_entries = []

                        if "d_news3_entries" not in st.session_state:
                            st.session_state.d_news3_entries = []


                        # Fetch stored user inputs after successful login
                        try:
                            # Query the user_inputs table for this user's data
                            response = st.session_state.supabase_client.table("user_inputs")\
                                .select("*")\
                                .eq("user_id", st.session_state.user_id)\
                                .execute()

                            if hasattr(response, 'data') and response.data:
                                # Get the most recent entry (if there are multiple)
                                user_data = response.data[-1]
                                
                                # Assign values to session state
                                st.session_state.role = user_data.get('role', '')
                                st.session_state.specialty = user_data.get('specialty', '')
                                st.session_state.patient_demographics = user_data.get('patients', '')
                                st.session_state.update_frequency = user_data.get('frequency', 'Weekly')
                                st.session_state.geography = user_data.get('geography', '')
                                # Assuming user_data.get('diseases', []) returns a list like: [",\"obesity,\""]

                                st.session_state.diseases_of_interest = user_data.get('diseases')
                                st.session_state.drugs_of_interest = user_data.get('drugs')
                            



                                st.session_state.keywords = user_data.get('keywords', '')
                                
                                print("User preferences loaded successfully")

                                # If you need a search string, create it using session state variables
                                search_string = f"{st.session_state.diseases_of_interest}, {st.session_state.drugs_of_interest}" 

                                st.session_state.academic_research = search_pubmed(search_string, 20)
                                st.session_state.clinical_trials = fetch_clinical_trials(st.session_state.diseases_of_interest, st.session_state.drugs_of_interest)


                                # Fetch Industry News
                                i_news1 = "https://www.pharmaceutical-business-review.com/drug-discovery/rss"
                                st.session_state.i_news1_entries = fetch_rss_feed(i_news1)

                                i_news2 = "https://www.biopharmadive.com/feeds/news/"
                                st.session_state.i_news2_entries = fetch_rss_feed(i_news2)

                                i_news3 = "https://www.statnews.com/category/pharma/feed/"
                                st.session_state.i_news3_entries = fetch_rss_feed(i_news3)

                                i_news4 = "https://www.medpagetoday.com/rss/headlines.xml"
                                st.session_state.i_news4_entries = fetch_rss_feed(i_news4)

                                # Fetch Regulatory News
                                r_news1 = "https://thehill.com/policy/healthcare/feed/"
                                st.session_state.r_news1_entries = fetch_rss_feed(r_news1)

                                r_news2 = "https://edhub.ama-assn.org/rss/site_9/0_44020.xml"
                                st.session_state.r_news2_entries = fetch_rss_feed(r_news2)

                                r_news3 = "https://www.statnews.com/category/politics/feed/"
                                st.session_state.r_news3_entries = fetch_rss_feed(r_news3)

                                # Fetch Provider News
                                p_news1 = "https://www.medpagetoday.com/rss/headlines.xml"
                                st.session_state.p_news1_entries = fetch_rss_feed(p_news1)

                                p_news2 = "https://edhub.ama-assn.org/rss/site_9/0_5672.xml"
                                st.session_state.p_news2_entries = fetch_rss_feed(p_news2)

                                p_news3 = "https://edhub.ama-assn.org/rss/site_9/0_44067.xml"
                                st.session_state.p_news3_entries = fetch_rss_feed(p_news3)

                                # Fetch Drug News
                                d_news1 = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch/rss.xml"
                                st.session_state.d_news1_entries = fetch_rss_feed(d_news1)

                                d_news2 = "https://jamanetwork.com/rss/site_9/0_42095.xml"
                                st.session_state.d_news2_entries = fetch_rss_feed(d_news2)

                                d_news3 = "https://www.biospace.com/FDA.rss"
                                st.session_state.d_news3_entries = fetch_rss_feed(d_news3)


                            else:
                                # If no data found, initialize with empty values
                                st.session_state.role = ""
                                st.session_state.specialty = ""
                                st.session_state.patient_demographics = ""
                                st.session_state.update_frequency = "Weekly"
                                st.session_state.geography = ""
                                st.session_state.diseases_of_interest = ""
                                st.session_state.drugs_of_interest = ""
                                st.session_state.keywords = ""
                                print("No stored preferences found for user")

                        except Exception as e:
                            print(f"Error loading user preferences: {str(e)}")
                            st.error("There was an error loading your preferences")

                        # After loading preferences, redirect to results page
                        st.session_state.current_page = "Results Page"
                        
                        if "auth_session" in st.session_state and st.session_state.auth_session:
                            print("User is logged in.")
                            st.rerun()
                        else:
                            print("No user session found.")
                    else:
                        st.error("Login failed. Please check your credentials.")
                else:
                    st.warning("Please provide both email and password.")

    

    elif st.session_state.current_page == "Input Page":
        st.title("Personal Input Page")
        
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
        
        st.session_state.update_frequency = st.radio(
                "Preferred Update Frequency (Required):",
                ["Daily", "Weekly", "Monthly"],
                index=1
            )

        st.session_state.geography = st.text_input(
            "Enter your Geography (Optional):",
            "Country, State, City, or Region"
        )
        
        # Existing Inputs
        st.session_state.diseases_of_interest = st.text_input("Enter disease (only enter one) of interest:")
        st.session_state.drugs_of_interest = st.text_input("Enter drug of interest (only enter one):")
        st.session_state.keywords = st.text_input("Enter keywords of interest (optional):")
        
        # Perform spell check on all input text
        disease_suggestions = st.session_state.diseases_of_interest
        drug_suggestions = st.session_state.drugs_of_interest
        keyword_suggestions = st.session_state.keywords

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
        
        # Check if the user is already logged in before proceeding with any action
        if "auth_session" not in st.session_state or st.session_state.auth_session is None:
            st.error("No user session found. Ensure the user is logged in.")
            st.session_state.current_page = "Sign in"  # Redirect to Sign-in page



        else:
            # Proceed with the submit action only if the user is logged in
            if st.button("Submit"):
                try:
                    # Ensure user session is intact before proceeding
                    if st.session_state.auth_session:
                        print("User is logged in with session:", st.session_state.auth_session)

                        # Call the store_user_inputs function to save the user inputs
                        
                        success = store_user_inputs(st.session_state)
                        if success:
                            st.success("Your inputs have been saved successfully!")
                            st.session_state.current_page = "Results Page"
                        else:
                            st.error("Failed to save your inputs. Please try again.")
                    
                    # If no valid session is found, we request the user to log in
                    else:
                        st.error("No valid session found. Please log in again.")
                        st.session_state.current_page = "Sign in"  # Redirect to Sign-in page

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            
            
                with st.spinner("Fetching updates..."):
                    # Fetch Academic Research
                    search_string = f"{st.session_state.diseases_of_interest}, {st.session_state.drugs_of_interest}"
                    st.session_state.academic_research = search_pubmed(search_string, 20)

                    # Fetch Clinical Trials
                    drug = st.session_state.drugs_of_interest.split(",")[0] if st.session_state.drugs_of_interest else ""
                    disease = st.session_state.diseases_of_interest.split(",")[0] if st.session_state.diseases_of_interest else ""
                    st.session_state.clinical_trials = fetch_clinical_trials(drug, disease)

                    # Fetch Industry News
                    i_news1 = "https://www.pharmaceutical-business-review.com/drug-discovery/rss"
                    st.session_state.i_news1_entries = fetch_rss_feed(i_news1)

                    i_news2 = "https://www.biopharmadive.com/feeds/news/"
                    st.session_state.i_news2_entries = fetch_rss_feed(i_news2)

                    i_news3 = "https://www.statnews.com/category/pharma/feed/"
                    st.session_state.i_news3_entries = fetch_rss_feed(i_news3)

                    i_news4 = "https://www.medpagetoday.com/rss/headlines.xml"
                    st.session_state.i_news4_entries = fetch_rss_feed(i_news4)

                    # Fetch Regulatory News
                    r_news1 = "https://thehill.com/policy/healthcare/feed/"
                    st.session_state.r_news1_entries = fetch_rss_feed(r_news1)

                    r_news2 = "https://edhub.ama-assn.org/rss/site_9/0_44020.xml"
                    st.session_state.r_news2_entries = fetch_rss_feed(r_news2)

                    r_news3 = "https://www.statnews.com/category/politics/feed/"
                    st.session_state.r_news3_entries = fetch_rss_feed(r_news3)

                    # Fetch Provider News
                    p_news1 = "https://www.medpagetoday.com/rss/headlines.xml"
                    st.session_state.p_news1_entries = fetch_rss_feed(p_news1)

                    p_news2 = "https://edhub.ama-assn.org/rss/site_9/0_5672.xml"
                    st.session_state.p_news2_entries = fetch_rss_feed(p_news2)

                    p_news3 = "https://edhub.ama-assn.org/rss/site_9/0_44067.xml"
                    st.session_state.p_news3_entries = fetch_rss_feed(p_news3)

                    # Fetch Drug News
                    d_news1 = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch/rss.xml"
                    st.session_state.d_news1_entries = fetch_rss_feed(d_news1)

                    d_news2 = "https://jamanetwork.com/rss/site_9/0_42095.xml"
                    st.session_state.d_news2_entries = fetch_rss_feed(d_news2)

                    d_news3 = "https://www.biospace.com/FDA.rss"
                    st.session_state.d_news3_entries = fetch_rss_feed(d_news3)

                st.session_state.current_page = "Results Page"
                st.rerun()
            
            

##main app UI#########################################################################################


    elif st.session_state.current_page == "Results Page":
        st.title("Kairos")
        st.write("View the latest and most comprehensive medical updates tailored to your interests.")

        tabs = st.tabs(["Home Page", "Clinical Research and Trials", "Industry News", "Regulatory News", 
                        "Provider News & Education"
                        , "Critical Alerts", "Settings", "Saved Articles", "Help & Info", "Survey"])

        with tabs[0]:
            # Sample quick overview/dashboard for Home Page
            st.title("Dashboard Overview")

            # Display some basic stats or quick data
            st.subheader(f"Quick View of Your Feed (Updated {st.session_state.update_frequency}) ")

            st.subheader("Content Updates")
            

            # Aggregating the counts for each section
            industry_news_count = 20

            regulatory_news_count = len([
                len(st.session_state.r_news1_entries),  # Regulatory News 1
                len(st.session_state.r_news2_entries),  # Regulatory News 2
                len(st.session_state.r_news3_entries),  # Regulatory News 3
            ])

            provider_news_count = sum([
                len(st.session_state.p_news1_entries),  # Provider News 1
                len(st.session_state.p_news2_entries),  # Provider News 2
                len(st.session_state.p_news3_entries),  # Provider News 3
            ])

            drug_news_count = sum([
                len(st.session_state.d_news1_entries),  # Drug News 1
                len(st.session_state.d_news2_entries),  # Drug News 2
                len(st.session_state.d_news3_entries),  # Drug News 3
            ])

            # Displaying the metrics in expandable sections
            with st.expander("Clinical Research"):
                st.metric("Total Articles", f"{industry_news_count} Articles")
                
            with st.expander("Regulatory News"):
                ##st.metric("Total Articles", f"{regulatory_news_count} Articles")
                st.write("Please view tab for articles")
            
            with st.expander("Provider News"):
                ##st.metric("Total Articles", f"{provider_news_count} Articles")
                st.write("Please view tab for articles")
                
            with st.expander("Drug Alerts"):
                ##st.metric("Total Articles", f"{drug_news_count} Articles")
                st.write("Please view tab for articles")
    
            # Display recently saved articles or other relevant info
            st.subheader("Recent Activity")
            
            def is_valid_uuid(uuid_str):
                regex = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', re.I)
                return bool(regex.match(uuid_str))
            
            
            

            if "user_id" in st.session_state:
                user_id = st.session_state["user_id"]
                if is_valid_uuid(user_id):
                    try:
                        print(f"Retrieved user_id: {user_id}")  # Debug log
                        st.session_state.saved_articles = get_saved_articles(st.session_state.supabase_client, user_id)
                        # Remaining code unchanged
                    except Exception as e:
                        st.write("An error occurred while fetching saved articles. Please try again later.")
                        print(f"Error fetching saved articles: {e}")
                else:
                    st.write("Invalid user ID. Please log in again.")
                    print(f"Invalid user_id format: {user_id}")
            else:
                st.write("You are not logged in. Please log in to view saved articles.")
                st.session_state["saved_articles"] = []

            # Display saved articles or an appropriate message
            if len(st.session_state["saved_articles"]) > 0:
                st.write("You have recent saved articles:")

                # Sort articles by 'saved_on' (descending) and display the last 5
                try:
                    sorted_articles = sorted(
                        st.session_state["saved_articles"], 
                        key=lambda x: x.get('saved_on', ''), 
                        reverse=True
                    )
                    for article in sorted_articles[:5]:  # Show last 5 saved articles
                        st.write(f"- {article.get('title', 'Untitled')}")
                except Exception as e:
                    st.write("An error occurred while displaying saved articles.")
                    print(f"Error displaying saved articles: {e}")
            else:
                st.write("No recent saved articles.")
                

            # Optionally display a system status or recent alerts
            st.subheader("System Status")
            st.write("All systems are operational. No critical issues detected.")

        
        with tabs[1]:  # Main Tab 1 for Academic Research
            sub_tabs = st.tabs(["Academic Research", "Clinical Trials"])  # Sub-tabs under Tab 1

            # Sub-Tab 1: Academic Research
            with sub_tabs[0]:
                
                
                st.subheader("Sort Articles by Publication Date")
    
                # Sorting options
                sort_option = st.radio(
                    "Sort by:",
                    options=["Most Recent", "Least Recent"],
                    horizontal=True
                )
                
                # Function to safely parse PubDate
                def parse_pubdate(pubdate):
                    try:
                        # Attempt to parse with complete date format
                        return datetime.strptime(pubdate, "%Y %b %d")
                    except ValueError:
                        try:
                            # If the day is missing, attempt to parse with only year and month
                            return datetime.strptime(pubdate, "%Y %b")
                        except ValueError:
                            # If it still doesn't work, return a very early date (datetime.min)
                            return datetime.min

                # Sort articles based on PubDate
                sorted_articles = sorted(
                    st.session_state.academic_research,
                    key=lambda article: parse_pubdate(article.get("PubDate", None) if isinstance(article, dict) else ""),
                    reverse=(sort_option == "Most Recent")  # Reverse for most recent
                )
                
                st.write(f"Showing articles sorted by **{sort_option}**.")

                # Display sorted articles
                for i, article in enumerate(sorted_articles):
                    if isinstance(article, dict):
                        with st.expander(article['Title']):
                            # Adjusted column ratios for better spacing
                            col1, col2, col3 = st.columns([2, 2, 1])

                            with col1:
                                st.write(f"**Source:** {article['Source']}")

                            with col2:
                                st.write(f"**Published:** {article['PubDate']}")

                            with col3:
                                st.write(f"[Read More]({article['URL']})")  # Displaying the URL link

                            st.write("---")  # Adding a separator for better visual organization

                            # Buttons inside the dropdown
                            col5, col6 = st.columns([5, 1])
                            with col5:
                                if st.button(f"Get AI summary", key=f"ai_summary_{i}"):
                                    with st.spinner("Generating AI summary..."):
                                        try:
                                            st.write(
                                                summarize_content(
                                                    article["URL"],
                                                    disease_interest=st.session_state.diseases_of_interest,
                                                    drug_interest=st.session_state.drugs_of_interest,
                                                    role=st.session_state.role,
                                                    specialty=st.session_state.specialty,
                                                    patient=st.session_state.patient_demographics
                                                )
                                            )
                                        except Exception as e:
                                            st.error(f"An error occurred while fetching AI summary: {str(e)}")

                            with col6:
                                if st.button(f"Save Article", key=f"save_article_{i}"):
                                    with st.spinner("Saving article..."):
                                        try:
                                            source = article.get("Source", "Unknown Source")
                                            save_article(
                                                st.session_state.supabase_client,
                                                user_id=st.session_state.user_id,
                                                article_id=article.get("ID", f"article_{i}"),
                                                title=article.get("Title", "Untitled Article"),
                                                notes=article.get("notes"),
                                                source=article.get("Source"),
                                                article_url=article.get("URL")
                                            )

                                            st.session_state.saved_articles.append({
                                                "article_id": article.get("ID", f"article_{i}"),
                                                "title": article.get("Title", "Untitled Article"),
                                                "notes": article.get("notes"),
                                                "source": source,
                                                "article_url": article.get("URL"),
                                                "saved_on": datetime.now().isoformat(),
                                            })
                                            st.success("Article saved successfully!")

                                        except Exception as e:
                                            st.error(f"An error occurred while saving the article: {str(e)}")

                    else:
                        st.write(f"Article {i} is NOT a dictionary: {type(article)}")
                        continue  # Skip this article if it's not a dictionary



            # Sub-Tab 2: Clinical Trials
            with sub_tabs[1]:
                # Check if the clinical_trials DataFrame is not empty
                if not st.session_state.clinical_trials.empty:
                    # Use the DataFrame from session state
                    df_trials = st.session_state.clinical_trials

                    # Initialize sorted DataFrame
                    df_trials_sorted = df_trials  # Default to the original DataFrame

                    # Check for 'LastUpdatePostDate' column
                    if 'LastUpdatePostDate' in df_trials.columns:
                        # Separate trials into two groups: with and without 'LastUpdatePostDate'
                        df_with_update = df_trials[df_trials['LastUpdatePostDate'].notna()].copy()
                        df_without_update = df_trials[df_trials['LastUpdatePostDate'].isna()].copy()

                        # Sort trials with 'LastUpdatePostDate' (descending)
                        if not df_with_update.empty:
                            df_with_update['LastUpdatePostDate'] = pd.to_datetime(
                                df_with_update['LastUpdatePostDate'], errors='coerce'
                            )
                            df_with_update = df_with_update.sort_values(
                                by="LastUpdatePostDate", ascending=False
                            )

                        # Sort trials without 'LastUpdatePostDate' by 'StudyFirstPostDate' (descending)
                        if not df_without_update.empty and 'StudyFirstPostDate' in df_trials.columns:
                            df_without_update['StudyFirstPostDate'] = pd.to_datetime(
                                df_without_update['StudyFirstPostDate'], errors='coerce'
                            )
                            df_without_update = df_without_update.sort_values(
                                by="StudyFirstPostDate", ascending=False
                            )

                        # Combine sorted DataFrames
                        df_trials_sorted = pd.concat([df_with_update, df_without_update], ignore_index=True)

                    # Fallback: Sort by 'StudyFirstPostDate' if 'LastUpdatePostDate' is missing
                    elif 'StudyFirstPostDate' in df_trials.columns:
                        df_trials['StudyFirstPostDate'] = pd.to_datetime(
                            df_trials['StudyFirstPostDate'], errors='coerce'
                        )
                        df_trials_sorted = df_trials.sort_values(by="StudyFirstPostDate", ascending=False)

                    # Display the sorted DataFrame
                    st.write("### Clinical Trials")
                    st.write("Click on any column header to reorganize the results by that category:")
                    # Add a link to ClinicalTrials.gov for further details
                    st.markdown("[Click here to explore more trials on ClinicalTrials.gov](https://clinicaltrials.gov)")
                    
                    
                    st.dataframe(df_trials_sorted)

                else:
                    # Display a warning if the DataFrame is empty
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
                st.session_state.i_news1_entries +
                st.session_state.i_news2_entries +
                st.session_state.i_news3_entries +
                st.session_state.i_news4_entries
            )

            # Initialize an empty list to store tagged entries
            tagged_entries = []

            # Helper function to calculate matches and assign colors
            def contains_word(word, text):
                """Check if a word exists as a whole word in the text."""
                return bool(re.search(rf"\b{re.escape(word)}\b", text))

            def tag_entry(entry, diseases_of_interest, drugs_of_interest, specialty, keywords):
                match_count = 0
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()

                # Check for matches, ensuring no empty inputs
                if diseases_of_interest and (contains_word(diseases_of_interest, title) or contains_word(diseases_of_interest, summary)):
                    match_count += 1
                if drugs_of_interest and (contains_word(drugs_of_interest, title) or contains_word(drugs_of_interest, summary)):
                    match_count += 1
                if specialty and (contains_word(specialty, title) or contains_word(specialty, summary)):
                    match_count += 1
                if keywords and (contains_word(keywords, title) or contains_word(keywords, summary)):
                    match_count += 1

                # Assign color based on match count
                if match_count >= 3:
                    color = "green"
                elif match_count == 1 or match_count == 2:
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
                # List potential keys for date
                potential_keys = ["published", "date", "timestamp", "created_at"]
                
                # Attempt to extract a valid date
                for key in potential_keys:
                    date_str = entry.get(key, "")
                    if date_str:
                        try:
                            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")  # Adjust the format as needed
                        except ValueError:
                            continue  # Try the next key
                
                # Fallback if no valid date is found
                return datetime.min

            
            
            if filter_option == "Most Recent":
                tagged_entries.sort(
                    key=lambda x: parse_date(x["entry"]),
                    reverse=True
                )
            elif filter_option == "Relevancy (Number of Matches)":
                tagged_entries.sort(
                    key=lambda x: x["match_count"],
                    reverse=True
                )

            
            # Display results
            if tagged_entries:
                for i, tagged_entry in enumerate(tagged_entries):
                    entry = tagged_entry["entry"]
                    color = tagged_entry["color"]
                    match_count = tagged_entry["match_count"]

                    # Generate a unique key for each article
                    article_key = entry.get("id", f"article_{i}")

                    # Display the article details in an expander
                    with st.expander(f"{entry.get('title', 'No Title')} ({match_count} matches)"):
                        # Article metadata layout
                        col1, col2, col3 = st.columns([2, 3, 1])

                        with col1:
                            st.write(f"**Source:** {entry.get('source', 'Unknown Source')}")

                        with col2:
                            st.write(f"**Summary:** {strip_html(entry.get('summary', 'No Summary'))}")

                        with col3:
                            # A colored indicator for match relevance
                            st.markdown(
                                f"""
                                <div style="background-color: {color}; width: 15px; height: 15px; border-radius: 50%;"></div>
                                """,
                                unsafe_allow_html=True,
                            )

                        st.write(f"[Read Full Article]({entry.get('link', '#')})", unsafe_allow_html=True)

                        # Buttons for summarization and saving
                        col4, col5 = st.columns(2)

                        with col4:
                            if st.button("Get AI Summary", key=f"ai_summary_{article_key}"):
                                with st.spinner("Generating AI summary..."):
                                    try:
                                        summary = summarize_content(
                                            entry.get("link", ""),
                                            disease_interest=st.session_state.diseases_of_interest,
                                            drug_interest=st.session_state.drugs_of_interest,
                                            role=st.session_state.role,
                                            specialty=st.session_state.specialty,
                                            patient=st.session_state.patient_demographics,
                                        )
                                        st.write(summary)
                                    except Exception as e:
                                        st.error(f"An error occurred while fetching AI summary: {str(e)}")

                        with col5:
                            if st.button("Save Article", key=f"save_article_{article_key}"):
                                with st.spinner("Saving article..."):
                                    try:
                                        source = entry.get("source", "Unknown Source")
                                        save_article(
                                            st.session_state.supabase_client,
                                            user_id=st.session_state.user_id,
                                            article_id=entry.get("id", article_key),
                                            title=entry.get("title", "Untitled Article"),
                                            notes=entry.get("notes"),
                                            source=source,
                                            article_url=entry.get("link", "#"),
                                        )

                                        st.session_state.saved_articles.append({
                                            "article_id": entry.get("id", article_key),
                                            "title": entry.get("title", "Untitled Article"),
                                            "notes": entry.get("notes"),
                                            "source": source,
                                            "article_url": entry.get("link", "#"),
                                            "saved_on": datetime.now().isoformat(),
                                        })
                                        st.success("Article saved successfully!")
                                    except Exception as e:
                                        st.error(f"An error occurred while saving the article: {str(e)}")

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
            combined_entries = st.session_state.r_news1_entries + st.session_state.r_news2_entries + st.session_state.r_news3_entries

            
            # Filter RSS entries based on diseases, drugs, specialty, and keywords using OR logic
            filtered_rss2_entries = [
                entry for entry in combined_entries
                if (
                    case_insensitive_match(diseases_of_interest, entry.get('title', '')) or
                    case_insensitive_match(diseases_of_interest, entry.get('summary', '')) or
                    case_insensitive_match(drugs_of_interest, entry.get('title', '')) or
                    case_insensitive_match(drugs_of_interest, entry.get('summary', ''))
                ) or (
                    case_insensitive_match(specialty, entry.get('title', '')) or
                    case_insensitive_match(specialty, entry.get('summary', ''))
                ) or (
                    case_insensitive_match(keywords, entry.get('title', '')) or
                    case_insensitive_match(keywords, entry.get('summary', ''))
                )
            ]
            
            
            # Display filtered results or a message if no matches
            if filtered_rss2_entries:
                for i, entry in enumerate(filtered_rss2_entries):
                    # Generate a unique key by combining index with title or link
                    unique_key = f"entry_{i}_{entry.get('title', '')[:10]}"

                    with st.expander(f"{entry.get('title', 'No Title')}"):
                        # Article metadata layout
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            st.write(f"**Source:** {entry.get('source', 'Unknown Source')}")
                            summary_html = entry.get("summary", "No Summary")
                            plain_summary = strip_html(summary_html)
                            st.write(plain_summary)
                            st.markdown(
                                f"[Read More]({entry.get('link', '#')})", unsafe_allow_html=True
                            )

                        with col2:
                            if st.button("Get AI Summary", key=f"ai_summary_{unique_key}"):
                                with st.spinner("Generating AI summary..."):
                                    try:
                                        summary = summarize_content(
                                            entry.get("link", ""),
                                            disease_interest=st.session_state.diseases_of_interest,
                                            drug_interest=st.session_state.drugs_of_interest,
                                            role=st.session_state.role,
                                            specialty=st.session_state.specialty,
                                            patient=st.session_state.patient_demographics,
                                        )
                                        st.write(summary)
                                    except Exception as e:
                                        st.error(f"An error occurred while fetching AI summary: {str(e)}")

                            if st.button("Save Article", key=f"save_article_{unique_key}"):
                                with st.spinner("Saving article..."):
                                    try:
                                        source = entry.get("source", "Unknown Source")
                                        save_article(
                                            st.session_state.supabase_client,
                                            user_id=st.session_state.user_id,
                                            article_id=entry.get("id", unique_key),
                                            title=entry.get("title", "Untitled Article"),
                                            notes=entry.get("notes"),
                                            source=source,
                                            article_url=entry.get("link", "#"),
                                        )

                                        st.session_state.saved_articles.append({
                                            "article_id": entry.get("id", unique_key),
                                            "title": entry.get("title", "Untitled Article"),
                                            "notes": entry.get("notes"),
                                            "source": source,
                                            "article_url": entry.get("link", "#"),
                                            "saved_on": datetime.now().isoformat(),
                                        })
                                        st.success("Article saved successfully!")
                                    except Exception as e:
                                        st.error(f"An error occurred while saving the article: {str(e)}")
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
            combined_entries = st.session_state.p_news1_entries + st.session_state.p_news2_entries + st.session_state.p_news3_entries 
            
            # Filter RSS entries based on diseases, drugs, specialty, and keywords using OR logic
            filtered_rss3_entries = [
                entry for entry in combined_entries
                if (
                    case_insensitive_match(diseases_of_interest, entry.get('title', '')) or
                    case_insensitive_match(diseases_of_interest, entry.get('summary', '')) or
                    case_insensitive_match(drugs_of_interest, entry.get('title', '')) or
                    case_insensitive_match(drugs_of_interest, entry.get('summary', ''))
                ) or (
                    case_insensitive_match(specialty, entry.get('title', '')) or
                    case_insensitive_match(specialty, entry.get('summary', ''))
                ) or (
                    case_insensitive_match(keywords, entry.get('title', '')) or
                    case_insensitive_match(keywords, entry.get('summary', ''))
                )
            ]


            # Display filtered results or a message if no matches
            if filtered_rss3_entries:
                for i, entry in enumerate(filtered_rss3_entries):
                    # Generate a unique key by combining index with title or link
                    unique_key = f"entry_{i}_{entry.get('title', '')[:10]}"

                    with st.expander(entry.get("title", "No Title")):
                        # Article metadata layout
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            summary_html = entry.get("summary", "No Summary")
                            plain_summary = strip_html(summary_html)
                            st.write(plain_summary)
                            st.markdown(
                                f"[Read More]({entry.get('link', '#')})", unsafe_allow_html=True
                            )

                        with col2:
                            # Summarization button
                            if st.button("Get AI Summary", key=f"ai_summary_{unique_key}"):
                                with st.spinner("Generating AI summary..."):
                                    try:
                                        summary = summarize_content(
                                            entry.get("link", ""),
                                            disease_interest=st.session_state.diseases_of_interest,
                                            drug_interest=st.session_state.drugs_of_interest,
                                            role=st.session_state.role,
                                            specialty=st.session_state.specialty,
                                            patient=st.session_state.patient_demographics,
                                        )
                                        st.write(summary)
                                    except Exception as e:
                                        st.error(f"An error occurred while fetching AI summary: {str(e)}")

                            # Save article button
                            if st.button("Save Article", key=f"save_article_{unique_key}"):
                                with st.spinner("Saving article..."):
                                    try:
                                        source = entry.get("source", "Unknown Source")
                                        save_article(
                                            st.session_state.supabase_client,
                                            user_id=st.session_state.user_id,
                                            article_id=entry.get("id", unique_key),
                                            title=entry.get("title", "Untitled Article"),
                                            notes=entry.get("notes"),
                                            source=source,
                                            article_url=entry.get("link", "#"),
                                        )

                                        st.session_state.saved_articles.append({
                                            "article_id": entry.get("id", unique_key),
                                            "title": entry.get("title", "Untitled Article"),
                                            "notes": entry.get("notes"),
                                            "source": source,
                                            "article_url": entry.get("link", "#"),
                                            "saved_on": datetime.now().isoformat(),
                                        })
                                        st.success("Article saved successfully!")
                                    except Exception as e:
                                        st.error(f"An error occurred while saving the article: {str(e)}")
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
            combined_entries = st.session_state.d_news1_entries + st.session_state.d_news2_entries + st.session_state.d_news3_entries
            
            
            # Filter RSS entries based on diseases, drugs, specialty, and keywords using OR logic
            filtered_rss4_entries = [
                entry for entry in combined_entries
                if (
                    case_insensitive_match(diseases_of_interest, entry.get('title', '')) or
                    case_insensitive_match(diseases_of_interest, entry.get('summary', '')) or
                    case_insensitive_match(drugs_of_interest, entry.get('title', '')) or
                    case_insensitive_match(drugs_of_interest, entry.get('summary', ''))
                ) or (
                    case_insensitive_match(specialty, entry.get('title', '')) or
                    case_insensitive_match(specialty, entry.get('summary', ''))
                ) or (
                    case_insensitive_match(keywords, entry.get('title', '')) or
                    case_insensitive_match(keywords, entry.get('summary', ''))
                )
            ]


            # Display filtered results or a message if no matches
            if filtered_rss4_entries:
                for i, entry in enumerate(filtered_rss4_entries):
                    # Generate a unique key for each entry
                    unique_key = f"rss4_entry_{i}_{entry.get('title', '')[:10]}"

                    with st.expander(entry.get('title', 'No Title')):
                        # Article metadata layout
                        col1, col2 = st.columns([4, 1])

                        with col1:
                            # Display the summary and link
                            summary_html = entry.get('summary', 'No Summary')
                            plain_summary = strip_html(summary_html)
                            st.write(plain_summary)
                            st.markdown(f"[Read More]({entry.get('link', '#')})", unsafe_allow_html=True)

                        with col2:
                            # Summarization button
                            if st.button("Get AI Summary", key=f"ai_summary_{unique_key}"):
                                with st.spinner("Generating AI summary..."):
                                    try:
                                        summary = summarize_content(
                                            entry.get("link", ""),
                                            disease_interest=st.session_state.diseases_of_interest,
                                            drug_interest=st.session_state.drugs_of_interest,
                                            role=st.session_state.role,
                                            specialty=st.session_state.specialty,
                                            patient=st.session_state.patient_demographics,
                                        )
                                        st.write(summary)
                                    except Exception as e:
                                        st.error(f"An error occurred while fetching AI summary: {str(e)}")

                            # Save article button
                            if st.button("Save Article", key=f"save_article_{unique_key}"):
                                with st.spinner("Saving article..."):
                                    try:
                                        source = entry.get("source", "Unknown Source")
                                        save_article(
                                            st.session_state.supabase_client,
                                            user_id=st.session_state.user_id,
                                            article_id=entry.get("id", unique_key),
                                            title=entry.get("title", "Untitled Article"),
                                            notes=entry.get("notes"),
                                            source=source,
                                            article_url=entry.get("link", "#"),
                                        )

                                        # Add article to the saved articles list in session state
                                        st.session_state.saved_articles.append({
                                            "article_id": entry.get("id", unique_key),
                                            "title": entry.get("title", "Untitled Article"),
                                            "notes": entry.get("notes"),
                                            "source": source,
                                            "article_url": entry.get("link", "#"),
                                            "saved_on": datetime.now().isoformat(),
                                        })
                                        st.success("Article saved successfully!")
                                    except Exception as e:
                                        st.error(f"An error occurred while saving the article: {str(e)}")
            else:
                st.write("No relevant news articles found based on your input.")


        # critical alerts
        with tabs[6]:
                st.title("Settings")

                # Role Input
                role = st.selectbox(
                    "Select your Role (Required):",
                    [
                        "Physician", "Nurse Practitioner", "Physician Assistant", 
                        "Specialist (e.g., Cardiologist, Oncologist)", "Resident/Fellow", 
                        "Medical Student", "Other (Specify)"
                    ],
                    index=0 if not st.session_state.get("role") else [
                        "Physician", "Nurse Practitioner", "Physician Assistant", 
                        "Specialist (e.g., Cardiologist, Oncologist)", "Resident/Fellow", 
                        "Medical Student", "Other (Specify)"
                    ].index(st.session_state.role)
                )

                # Specialty Input
                specialty = st.selectbox(
                    "Select your Specialty (Required):",
                    [
                        "General Practitioner", "Internal Medicine", "Cardiology", "Oncology", 
                        "Pediatrics", "Neurology", "Orthopedics", "Surgery - General", 
                        "Surgery - Cardiothoracic", "Surgery - Neurosurgery", "Dermatology", 
                        "Endocrinology", "Gastroenterology", "Hematology", "Infectious Disease", 
                        "Nephrology", "Obstetrics and Gynecology", "Ophthalmology", 
                        "Otolaryngology (ENT)", "Pathology", "Psychiatry", "Pulmonology", 
                        "Radiology", "Immunology", "Urology", "Anesthesiology", "Emergency Medicine", 
                        "Other (Specify)"
                    ],
                    index=0 if not st.session_state.get("specialty") else [
                        "General Practitioner", "Internal Medicine", "Cardiology", "Oncology", 
                        "Pediatrics", "Neurology", "Orthopedics", "Surgery - General", 
                        "Surgery - Cardiothoracic", "Surgery - Neurosurgery", "Dermatology", 
                        "Endocrinology", "Gastroenterology", "Hematology", "Infectious Disease", 
                        "Nephrology", "Obstetrics and Gynecology", "Ophthalmology", 
                        "Otolaryngology (ENT)", "Pathology", "Psychiatry", "Pulmonology", 
                        "Radiology", "Immunology", "Urology", "Anesthesiology", "Emergency Medicine", 
                        "Other (Specify)"
                    ].index(st.session_state.specialty)
                )

                # Patient Demographics Input
                patient_demographics = st.text_area(
                    "Enter Patient Demographics (Optional):",
                    value=st.session_state.get("patient_demographics", "")
                )

                # Update Frequency Input
                update_frequency = st.radio(
                    "Preferred Update Frequency (Required):",
                    ["Daily", "Weekly", "Monthly"],
                    index=["Daily", "Weekly", "Monthly"].index(st.session_state.get("update_frequency", "Daily"))
                )

                # Geography Input
                geography = st.text_input(
                    "Enter your Geography (Optional):",
                    value=st.session_state.get("geography", "")
                )

                # Diseases, Drugs, and Keywords Inputs
                diseases_of_interest = st.text_input(
                    "Enter diseases of interest:",
                    value=st.session_state.get("diseases_of_interest", "")
                )
                drugs_of_interest = st.text_input(
                    "Enter drugs of interest (include all relevant names if possible):",
                    value=st.session_state.get("drugs_of_interest", "")
                )
                keywords = st.text_input(
                    "Enter keywords of interest (optional):",
                    value=st.session_state.get("keywords", "")
                )

                # Button to apply changes
                if st.button("Update Preferences"):
                    
                    # Initialize session state if not already set
                    if "role" not in st.session_state:
                        st.session_state.role = None
                    if "specialty" not in st.session_state:
                        st.session_state.specialty = None
                    if "patient_demographics" not in st.session_state:
                        st.session_state.patient_demographics = None
                    if "update_frequency" not in st.session_state:
                        st.session_state.update_frequency = None
                    if "geography" not in st.session_state:
                        st.session_state.geography = None
                    if "diseases_of_interest" not in st.session_state:
                        st.session_state.diseases_of_interest = ""
                    if "drugs_of_interest" not in st.session_state:
                        st.session_state.drugs_of_interest = ""
                    if "keywords" not in st.session_state:
                        st.session_state.keywords = None

                    # Save updated preferences in session state
                    st.session_state.role = role
                    st.session_state.specialty = specialty
                    st.session_state.patient_demographics = patient_demographics
                    st.session_state.update_frequency = update_frequency
                    st.session_state.geography = geography
                    st.session_state.diseases_of_interest = diseases_of_interest
                    st.session_state.drugs_of_interest = drugs_of_interest
                    st.session_state.keywords = keywords
                    
                    
                    
                    
                    try:
                        # Clean the input data
                        diseases_list = [d.strip() for d in diseases_of_interest.split(",") if d.strip()]
                        drugs_list = [d.strip() for d in drugs_of_interest.split(",") if d.strip()]
                        
                        # Convert lists back to comma-separated strings for storage
                        diseases_str = ", ".join(diseases_list)
                        drugs_str = ", ".join(drugs_list)
                        
                        data = {
                            "role": role.strip(),
                            "specialty": specialty.strip(),
                            "patients": patient_demographics.strip(),
                            "frequency": update_frequency.strip(),
                            "geography": geography.strip(),
                            "diseases": diseases_str,
                            "drugs": drugs_str,
                            "keywords": keywords.strip(),
                            "created_at": datetime.now().isoformat(),
                        }
                        
                        response = supabase.table("user_inputs").update(data).eq("user_id", st.session_state.user_id).execute()
                        
                        if hasattr(response, 'data') and response.data:
                            st.success("Preferences updated successfully.")
                        else:
                            st.error("Failed to update preferences. Please try again.")
                            print("Update response:", response)  # For debugging
                            
                    except Exception as e:
                        st.error(f"An error occurred while updating preferences: {e}")
                        print(f"Update error details: {str(e)}")  # For debugging


                    with st.spinner("Fetching new updates..."):
                        # Fetch Academic Research
                        search_string = f"{diseases_of_interest}, {drugs_of_interest}"
                        st.session_state.academic_research = search_pubmed(search_string, 20)

                        # Fetch Clinical Trials
                        drug = st.session_state.drugs_of_interest.split(",")[0] if st.session_state.drugs_of_interest else ""
                        disease = st.session_state.diseases_of_interest.split(",")[0] if st.session_state.diseases_of_interest else ""
                        st.session_state.clinical_trials = fetch_clinical_trials(drug, disease)

                        # Fetch Industry News
                        i_news1 = "https://www.pharmaceutical-business-review.com/drug-discovery/rss"
                        st.session_state.i_news1_entries = fetch_rss_feed(i_news1)

                        i_news2 = "https://www.biopharmadive.com/feeds/news/"
                        st.session_state.i_news2_entries = fetch_rss_feed(i_news2)

                        i_news3 = "https://www.statnews.com/category/pharma/feed/"
                        st.session_state.i_news3_entries = fetch_rss_feed(i_news3)

                        i_news4 = "https://www.medpagetoday.com/rss/headlines.xml"
                        st.session_state.i_news4_entries = fetch_rss_feed(i_news4)

                        # Fetch Regulatory News
                        r_news1 = "https://thehill.com/policy/healthcare/feed/"
                        st.session_state.r_news1_entries = fetch_rss_feed(r_news1)

                        r_news2 = "https://edhub.ama-assn.org/rss/site_9/0_44020.xml"
                        st.session_state.r_news2_entries = fetch_rss_feed(r_news2)

                        r_news3 = "https://www.statnews.com/category/politics/feed/"
                        st.session_state.r_news3_entries = fetch_rss_feed(r_news3)

                        # Fetch Provider News
                        p_news1 = "https://www.medpagetoday.com/rss/headlines.xml"
                        st.session_state.p_news1_entries = fetch_rss_feed(p_news1)

                        p_news2 = "https://edhub.ama-assn.org/rss/site_9/0_5672.xml"
                        st.session_state.p_news2_entries = fetch_rss_feed(p_news2)

                        p_news3 = "https://edhub.ama-assn.org/rss/site_9/0_44067.xml"
                        st.session_state.p_news3_entries = fetch_rss_feed(p_news3)

                        # Fetch Drug News
                        d_news1 = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/medwatch/rss.xml"
                        st.session_state.d_news1_entries = fetch_rss_feed(d_news1)

                        d_news2 = "https://jamanetwork.com/rss/site_9/0_42095.xml"
                        st.session_state.d_news2_entries = fetch_rss_feed(d_news2)

                        d_news3 = "https://www.biospace.com/FDA.rss"
                        st.session_state.d_news3_entries = fetch_rss_feed(d_news3)
                        
                        

                    st.session_state.current_page = "Results Page"
                    st.rerun()

            
        with tabs[7]:
            # Article Saving Section
            
            with st.container():
            
                st.markdown("""
                    ### Add Clinical Notes
                    Use this space to document:
                    - Key findings relevant to your practice
                    - Patient population this might benefit
                    - Treatment considerations
                    - Follow-up actions
                """)
                
                # Create a shared notes input that will be used for saving to any article
                shared_note = st.text_area(
                    label="Clinical Notes",
                    value="",
                    height=150,
                    placeholder="Enter your clinical observations, treatment implications, and follow-up plans...",
                    key=f"shared_notes_input"
                )

            # Saved Articles Display Section
            st.title("Saved Articles")

            # Check if there are any saved articles
            if st.session_state.saved_articles:
                st.subheader("Your Saved Articles")
                
                # Display saved articles
                for saved_index, article in enumerate(st.session_state.saved_articles):
                    with st.expander(article.get('title', 'Untitled Article')):
                        st.write(f"**Notes**: {article.get('notes', 'No notes added.')}")
                        st.write(f"**Source**: {article.get('source', 'Unknown Source')}")
                        
                        # Check if a valid link exists
                        link = article.get('article_url') 
                        if link:
                            st.write(f"[Read more]({link})")
                        else:
                            st.write("No link available for this article.")
                        
                        # Assuming `article.get('created_at', 'Unknown')` is an ISO 8601 string
                        created_at = article.get('created_at', 'Unknown')

                        # Check if the value is not 'Unknown' and format the timestamp
                        if created_at != 'Unknown':
                            # Convert to datetime object
                            datetime_obj = datetime.fromisoformat(created_at)
                            # Format it as "YYYY-MM-DD HH:MM AM/PM"
                            formatted_time = datetime_obj.strftime("%Y-%m-%d %I:%M %p")
                        else:
                            formatted_time = 'Unknown'

                        # Use the formatted time in your st.write statement
                        st.write(f"Saved on: {formatted_time}")
                        
                        # Add Save Note button with unique key
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            save_note_key = f"save_note_btn_saved_{saved_index}_{article.get('article_id', '')}"
                            if st.button("Save Note", key=save_note_key):
                                try:
                                    # Update note in Supabase
                                    response = st.session_state.supabase_client.table("saved_articles") \
                                        .update({"notes": shared_note}) \
                                        .eq("article_id", article.get('article_id')) \
                                        .execute()
                                    
                                    # Update note in session state
                                    for saved_article in st.session_state.saved_articles:
                                        if saved_article.get('article_id') == article.get('article_id'):
                                            saved_article['notes'] = shared_note
                                    
                                    st.success("Note saved successfully!")
                                    st.rerun()
                                
                                except Exception as e:
                                    st.error(f"Error saving note: {str(e)}")
                        
                        # Removal functionality
                        if "confirm_remove_state" not in st.session_state:
                            st.session_state.confirm_remove_state = {}

                        with col3:
                            remove_key = f"remove_btn_saved_{saved_index}_{article.get('article_id', '')}"
                            if st.button(f"Remove", key=remove_key):
                                # Set confirmation state for this article ID
                                st.session_state.confirm_remove_state[article.get('article_id')] = True

                            # Show confirmation and cancel buttons only if the state is set
                            if st.session_state.confirm_remove_state.get(article.get('article_id')):
                                st.write("")  # Add spacing for better visual alignment
                                # Create a horizontal layout for "Confirm" and "Cancel"
                                confirm_col, cancel_col = st.columns([1, 1])  # Adjust width ratios if needed
                                with confirm_col:
                                    confirm_key = f"confirm_remove_saved_{saved_index}_{article.get('article_id', '')}"
                                    if st.button("Confirm removal", key=confirm_key):
                                        try:
                                            # Remove from Supabase
                                            response = st.session_state.supabase_client.table("saved_articles") \
                                                .delete() \
                                                .eq("article_id", article.get('article_id')) \
                                                .execute()
                                            
                                            # Remove from session state
                                            st.session_state.saved_articles = [
                                                a for a in st.session_state.saved_articles 
                                                if a.get('article_id') != article.get('article_id')
                                            ]
                                            st.success("Article removed successfully!")
                                            st.session_state.confirm_remove_state.pop(article.get('article_id'), None)  # Clear state
                                            st.rerun()
                                        
                                        except Exception as e:
                                            st.error(f"Error removing article: {str(e)}")
                                with cancel_col:
                                    if st.button("Cancel", key=f"cancel_remove_{saved_index}_{article.get('article_id', '')}"):
                                        # Reset the confirmation state for this article
                                        st.session_state.confirm_remove_state.pop(article.get('article_id'), None)
                                        st.rerun()

                                            
            else:
                st.write("You don't have any saved articles yet.")
                    
                    
        with tabs[8]:
            
                # Title of the help section
                st.title("Help and Information")

                # Section for general information
                st.header("Welcome to Kairos!")
                st.write("""
                Kairos is designed to keep you up-to-date on the latest in healthcare, tailored specifically to your specialty and interests. 
                With Kairos, you’ll receive real-time updates on everything from new clinical guidelines and research to clinical trial results 
                to industry and regulatory news.

                You can personalize what you see based on the diseases, drugs, or fields you’re most interested in, making it easier to stay informed 
                on what matters to you. Plus, Kairos lets you save articles, add personal notes, and quickly filter 
                so that you’re always on top of the latest developments in your field.
                """)

                # Instructions for use
                st.header("How to Use Kairos?")
                st.write("""
                1. **Personalize Your Feed**: Set your preferences based on your specialty, diseases, or drugs of interest in the settings section.
                2. **Stay Informed**: Receive real-time updates on clinical guidelines, research, clinical trial results, and news relevant to your field.
                3. **Save Articles**: When you find articles of interest, save them for future reference by clicking the 'Save' button.
                4. **Add Personal Notes**: Add notes to saved articles to highlight important information or reminders by typing in the text box
                    and clicking the save note button 
                5. **Filter by Specialty/Topic/Time**: Quickly filter content by specialty, time or topic to ensure you're always viewing the most relevant information.
                """)

                # FAQs section
                ##st.header("Frequently Asked Questions")
                ##st.write("""
                ##**Q1: How can I personalize my feed?**  
                ##A1: In the 'Settings' section, you can choose your specialty, diseases, or drugs of interest. Your feed will update based on these preferences.

                ##**Q2: How do I save articles?**  
                ##A2: When you come across an article you find useful, click the 'Save' button to keep it in your saved articles list.

                ##**Q3: How can I add personal notes to articles?**  
                ##A3: After saving an article, you can add your personal notes by clicking on the article and entering your thoughts in the provided note section.

                ##**Q4: Can I filter content by specialty or topic?**  
                ##A4: Yes! You can filter the articles and updates based on your chosen specialty or topic to quickly find the information that’s most relevant to you.

                ##**Q5: Will I receive notifications about updates?**  
                ##A5: Yes, Med Sync sends push notifications to keep you updated on the latest research, guidelines, and news in your field.
                ##""")

                # Contact information
                st.header("Contact Us")
                st.write("""
                If you have any further questions or need assistance, feel free to reach out to us:
                - **Email**: krutinkumar@gmail.com
                """)

                # Disclaimer
                st.header("Disclaimer")
                st.write("""
                Kairos provides timely updates on healthcare topics but is not a substitute for professional medical advice. 
                """)
        
        with tabs[9]:
            st.write("Please fill this survey out every week if possible to let us know how we can make your experience better: https://forms.gle/T1nbbina5jnaMK7o7")

except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
