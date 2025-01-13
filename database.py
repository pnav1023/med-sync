import os
from datetime import datetime, timezone
from supabase import create_client, Client
import json
import asyncio
import streamlit
import uuid




def init_supabase_client() -> Client:

    # Initialize the Supabase client
    URL = "https://liteepuobwwnfggrujwy.supabase.co"
    KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxpdGVlcHVvYnd3bmZnZ3J1and5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzMxOTU5MjQsImV4cCI6MjA0ODc3MTkyNH0.AF_oj_BOaMuxINCKv-EhtMUAcqpUO_KI51NI6CfPzA4"

    # Initialize Supabase Client
    try:
        client = create_client(URL, KEY)
        print("Supabase client initialized successfully.")
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        client = None
    return client




# Sign-Up Function
def sign_up(supabase: Client, email: str, password: str):
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



def sign_in(supabase: Client, email: str, password: str):
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




def get_current_user(supabase: Client):
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
        # Get Supabase client
        supabase = session_state.get("supabase_client")
        if not supabase:
            print("Error: Supabase client not found in session state")
            return False

        # Get session
        try:
            session = supabase.auth.get_session()
            print("Initial session:", session)
            
            if not session:
                print("No session found, attempting refresh...")
                session = supabase.auth.refresh_session()
                print("Refreshed session:", session)
            
            # Handle Session object structure
            if hasattr(session, 'user'):
                user = session.user
            elif isinstance(session, dict) and 'user' in session:
                user = session['user']
            else:
                print("Error: Invalid session structure")
                return False
                
        except Exception as e:
            print(f"Session error: {str(e)}")
            return False

        # Get user ID - handle both object and dict patterns
        if hasattr(user, 'id'):
            user_id = user.id
        elif isinstance(user, dict) and 'id' in user:
            user_id = user['id']
        else:
            print("Error: Could not get user ID")
            return False

        # Prepare data
        data = {
            "user_id": user_id,
            "role": getattr(session_state, 'role', ''),
            "specialty": getattr(session_state, 'specialty', ''),
            "patients": getattr(session_state, 'patient_demographics', '').strip(),
            "frequency": getattr(session_state, 'update_frequency', 'Weekly'),
            "geography": getattr(session_state, 'geography', '').strip(),
            "diseases": getattr(session_state, 'diseases_of_interest', []),
            "drugs": getattr(session_state, 'drugs_of_interest', []),
            "keywords": getattr(session_state, 'keywords', '').strip(),
            "created_at": datetime.now().isoformat(),
        }

        print("Attempting to insert data:", data)

        # Insert data
        try:
            response = supabase.table("user_inputs").insert(data).execute()
            print("Insert response:", response)
            return True
        except Exception as e:
            print(f"Insert error: {str(e)}")
            return False

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False
    
    
def save_article(supabase: Client, user_id: str, article_id: str, title: str, notes: str, source: str, article_url: str) -> bool:
    try:
        data = {
            "user_id": user_id,
            "article_id": article_id,
            "title": title,
            "notes": notes,
            "source": source,  
            "article_url": article_url,
            
            # Add datetime.utcnow().isoformat() if needed
            "created_at": datetime.now().isoformat(),
        }
        response = supabase.table("saved_articles").insert(data).execute()
        print(response)

    except Exception as e:
        print(f"Error saving article: {e}")
        





def get_saved_articles(supabase: Client, user_id: uuid.UUID):
    # if not is_valid_uuid(user_id):
    #     print(f"Invalid user_id detected: {user_id}")
    #     return []  # Return an empty list if the user_id is not valid.
    
    try:
        print(f"Fetching saved articles for user_id: {user_id}")
        
        # Explicitly filtering by `user_id`
        response = supabase.table("saved_articles").select("*").eq("user_id", user_id).execute()
        #print("response: "+response)
        print(response.data)
        # Return the fetched data if no errors
        return response.data
    
    except Exception as e:
        # Log the exact error for debugging
        print(f"Error fetching saved articles: {e}")
        return []



if __name__ == "__main__":
    
    client = init_supabase_client()
    
    
    
    
    
    ##client = init_supabase_client()
    ##user_id = uuid.UUID("8da178bf-fc0b-43bc-b2ad-3811202dfe7f")
    ##articles = get_saved_articles(supabase=client, user_id=user_id)
    ##print(articles)



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
