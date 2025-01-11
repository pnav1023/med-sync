import os
from datetime import datetime, timezone
from supabase import create_client, Client
import json
import asyncio
import streamlit
import uuid



#this is purely for display already implemented correct functionality in ui.py
# Initialize the Supabase client
URL = "https://liteepuobwwnfggrujwy.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxpdGVlcHVvYnd3bmZnZ3J1and5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMxOTU5MjQsImV4cCI6MjA0ODc3MTkyNH0.AF_oj_BOaMuxINCKv-EhtMUAcqpUO_KI51NI6CfPzA4"

# Initialize Supabase Client
try:
    supabase = create_client(URL, KEY)
    print("Supabase client initialized successfully.")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase = None





# Sign-Up Function
def sign_up(email: str, password: str):
    try:
        # Call the sign-up method
        response = supabase.auth.sign_up({"email": email, "password": password})
        print("Sign-up response:", response)  # Debugging line

        if response.user:
            # Log the user in automatically after sign-up
            user, access_token = sign_in(email, password)
            if user and access_token:
                return True, "Account created successfully! You are now logged in."
            else:
                return False, "Error logging in after account creation: " + str(access_token)
        
        elif response.error:
            if "already been taken" in response.error.message.lower():
                return False, "Email already exists. Please log in or reset your password."
            return False, response.error.message
        
        return False, "Unknown error during sign-up."
    except Exception as e:
        return False, str(e)



def sign_in(email: str, password: str):
    try:
        # Sign in with Supabase
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print("Sign-in response:", response)  # Debugging line
        
        # Check if session exists
        if response.session:
            user = response.user
            access_token = response.session.access_token
            
            
            return user, access_token
        else:
            return None, "No session returned during sign-in."
    except Exception as e:
        return None, f"Error during sign-in: {str(e)}"




def get_current_user():
    try:
        user_response = supabase.auth.get_user()
        if user_response.user:
            print(f"Current user ID: {user_response.user.id}")
            return user_response.user.id
        print("No user currently signed in.")
    except Exception as e:
        print(f"Error fetching current user: {e}")
    return None

def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False




def store_user_inputs(session_state):
    try:
        # Retrieve Supabase client from session state
        supabase = session_state.get("supabase_client")
        if not supabase:
            print("Supabase client not initialized.")
            return False

        # Debugging: Confirm Supabase client
        print("Supabase client retrieved successfully.")

        # Try to refresh the session and check if a valid session exists
        try:
            supabase.auth.refresh_session()  # Refresh the session
            session = supabase.auth.get_session()  # Get the refreshed session
            print("Session after refresh:", session)
        except Exception as e:
            print(f"Error refreshing session: {str(e)}")
            return False

        if session and session.get("user"):
            print("User is authenticated:", session["user"])
        else:
            print("Session is invalid or missing user data.")
            return False

        # Proceed with saving the user data if session is valid
        user = session["user"]
        user_id = user["id"]
        print(f"User ID: {user_id}")

        # Prepare data to be inserted into the 'user_inputs' table
        data = {
            "user_id": user_id,
            "role": session_state.role or "",
            "specialty": session_state.specialty or "",
            "patients": session_state.patient_demographics.strip() if session_state.patient_demographics else "",
            "frequency": session_state.update_frequency or "Weekly",
            "geography": session_state.geography.strip() if session_state.geography else "",
            "diseases": session_state.diseases_of_interest or [],
            "drugs": session_state.drugs_of_interest or [],
            "keywords": session_state.keywords.strip() if session_state.keywords else "",
            "created_at": datetime.now().isoformat(),
        }

        # Debugging: Log the prepared data
        print("Data to be inserted into 'user_inputs':", data)

        # Insert data into the 'user_inputs' table
        response = supabase.table("user_inputs").insert(data).execute()

        # Debugging: Check response details
        print("Insert response:", response)

        # Verify insertion status
        if response.status_code == 201:  # Status code 201 indicates success
            print("Data inserted successfully into 'user_inputs'.")
            return True
        else:
            print(f"Error inserting data. Status code: {response.status_code}, Response: {response.text}")
            return False

    except Exception as e:
        # Catch and log any unexpected errors
        print(f"Error connecting to Supabase: {str(e)}")
        return False


    
    
def save_article(user_id: str, article_id: str, title: str, notes: str, source: str) -> bool:
    try:
        data = {
            "user_id": user_id,
            "article_id": article_id,
            "title": title,
            "notes": notes,
            "source": source,  
            
            # Add datetime.utcnow().isoformat() if needed
            "created_at": datetime.now().isoformat(),
        }
        response = supabase.table("saved_articles").insert(data).execute()
        return response.status_code == 201
    except Exception as e:
        print(f"Error saving article: {e}")
        return False





def get_saved_articles(user_id: str):
    if not is_valid_uuid(user_id):
        print(f"Invalid user_id detected: {user_id}")
        return []  # Return an empty list if the user_id is not valid.
    
    try:
        print(f"Fetching saved articles for user_id: {user_id}")
        
        # Explicitly filtering by `user_id`
        response = supabase.table("saved_articles").select("*").filter("user_id", "eq", str(user_id)).execute()
        
        # Check for any errors in the response
        if response.error:
            print(f"Supabase error: {response.error}")
            return []
        
        # Return the fetched data if no errors
        return response.data
    
    except Exception as e:
        # Log the exact error for debugging
        print(f"Error fetching saved articles: {e}")
        return []











# Get the currently authenticated user
#user = supabase.auth.get_user()

# Check if the user is authenticated
##if user is not None:
    ##user_id = user['id']  # Extract the user ID from the authenticated user
    ##print(f"User ID: {user_id}")

    # Call the save_article function to save articles to the database:
    ##response = save_article(
        ##supabase,
        ##user_id=user_id,  # Pass the actual dynamic user ID (which is a valid UUID)
        ##article_id="article-123",  # Replace with actual article ID (can be a UUID or string)
        ##title="Sample Article",
        ##notes="This is a sample article content."
    ##)

    # Query User-Specific Articles: Fetch articles belonging to the logged-in user:
    ##response = supabase.table("saved_articles").select("*").eq("user_id", user_id).execute()
    ##user_articles = response.data

    # Optionally, print the user articles for review:
    ##print("User's Saved Articles:", user_articles)

##else:
    ##print("No user is authenticated. Please log in.")
