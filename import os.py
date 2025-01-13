import os
from datetime import datetime
from supabase import create_client, Client

# Load Supabase URL and API key from environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(url, key)

def store_user_preference(user_id, selected_accounts):
    try:
        data = {
            "user_id": user_id,
            "selected_account": selected_accounts,
            "created_at": datetime.now()
        }
        # Insert data into user_preferences table
        response = supabase.table("user_preferences").insert(data).execute()
        print("User preference stored successfully:", response.data)
    except Exception as e:
        print("Error storing user preference:", e)

def store_tweet(tweet_data):
    try:
        # Validate required keys in tweet_data
        required_keys = ["text", "created_at", "likes", "retweets", "account"]
        if not all(key in tweet_data for key in required_keys):
            raise ValueError(f"Missing keys in tweet_data. Required keys: {required_keys}")

        data = {
            "tweet_text": tweet_data["text"],
            "created_at": tweet_data["created_at"],
            "likes": tweet_data["likes"],
            "retweets": tweet_data["retweets"],
            "account": tweet_data["account"]
        }
        # Insert data into tweets table
        response = supabase.table('tweets').insert(data).execute()
        print("Tweet stored successfully:", response.data)
    except Exception as e:
        print("Error storing tweet:", e)




##implement in ui.py for user inputs 


def store_user_inputs(st_session):
    # Prepare data with null-value handling
    data = {
        "role": st_session.role or None,  # Required
        "specialty": st_session.specialty or None,  # Required
        "patient_demographics": st_session.patient_demographics.strip() if st_session.patient_demographics else None,
        "update_frequency": st_session.update_frequency or "Weekly",  # Default to Weekly if missing
        "geography": st_session.geography.strip() if st_session.geography else None,
        "diseases_of_interest": st_session.diseases_of_interest or None,  # Required
        "drugs_of_interest": st_session.drugs_of_interest or None,  # Required
        "keywords": st_session.keywords.strip() if st_session.keywords else None,
        "created_at": datetime.utcnow(),
    }
    
    # Insert data into the Supabase table
    try:
        response = supabase.table("user_inputs").insert(data).execute()
        if response.status_code == 201:
            print("Data successfully inserted into Supabase!")
        else:
            print(f"Error inserting data: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")





def save_article(supabase, user_id, article_id, title, content):
    data = {
        "user_id": user_id,
        "article_id": article_id,
        "title": title,
        "content": content,
        "created_at": datetime.utcnow(),
    }
    response = supabase.table("saved_articles").insert(data).execute()
    return response




##supabase.auth methods to authenticate and get the user_id of the current user.
user = supabase.auth.user()
user_id = user["id"]


##Call the save_article function to save articles to the database:

response = save_article(
    supabase,
    user_id=user_id,
    article_id="article-123",
    title="Sample Article",
    content="This is a sample article content."
)


##Query User-Specific Articles: Fetch articles belonging to the logged-in user:
response = supabase.table("saved_articles").select("*").eq("user_id", user_id).execute()
user_articles = response.data

