import requests
import os
import streamlit as st
from dotenv import load_dotenv
import time




load_dotenv()  # This will load the variables from your .env file

# Function to fetch tweets from specific accounts and filter by keywords

@st.cache_data
def fetch_tweets_from_accounts(keywords, accounts, max_results=10):
    """
    Fetch recent tweets from specified Twitter accounts and prioritize tweets matching user keywords.
    
    Args:
        keywords (list): A list of keywords to match in tweets.
        accounts (list): Twitter handles to fetch tweets from (without the @ symbol).
        max_results (int): The maximum number of tweets to return.
    
    Returns:
        list: A list of prioritized tweets with metadata.
    """
    # Twitter API credentials
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")  # Set this in your environment
    
    if not bearer_token:
        st.error("Twitter Bearer Token is not set in environment variables. Please configure it in your .env file.")
        raise ValueError("Twitter Bearer Token is not set in environment variables.")
    
    headers = {"Authorization": f"Bearer {bearer_token}"}
    
    base_url = "https://api.twitter.com/2/tweets/search/recent"
    matched_tweets = []
    
    for account in accounts:
            query = f"from:{account} ({keywords}) lang:en"
            params = {"query": query, "tweet.fields": "created_at,text,public_metrics", "max_results": 10}
            
            retry_attempts = 3
            for attempt in range(retry_attempts):
                try:
                    response = requests.get(base_url, headers=headers, params=params)
                    if response.status_code == 200:
                        tweets = response.json().get("data", [])
                        
                        for tweet in tweets:
                            matches = [keyword for keyword in keywords.split(" OR ") if keyword.lower() in tweet["text"].lower()]
                            if matches:
                                tweet_data = {
                                    "text": tweet["text"],
                                    "created_at": tweet["created_at"],
                                    "matches": matches,
                                    "score": len(matches),
                                    "likes": tweet["public_metrics"]["like_count"],
                                    "retweets": tweet["public_metrics"]["retweet_count"]
                                }
                                matched_tweets.append(tweet_data)
                        break
                    elif response.status_code == 429:
                        st.warning("Rate limit reached, retrying...")
                        time.sleep(15 * 60)  # Wait for 15 minutes before retrying
                    else:
                        st.error(f"Error fetching tweets for @{account}: {response.status_code}")
                        break
                except Exception as e:
                    st.error(f"An error occurred while fetching tweets: {e}")
                    break
        
        # Sort tweets by score (number of matches) and recency
    matched_tweets.sort(key=lambda x: (x["score"], x["created_at"]), reverse=True)
    return matched_tweets[:max_results]

# Function to display tweets in Streamlit
def display_tweets_dashboard(keywords):
    """
    Display a dashboard of tweets matching user keywords from specified accounts.
    
    Args:
        keywords (list): Keywords provided by the user.
        user_specialty (str): User's specialty, displayed in the header.
    """
    st.subheader("Recent Tweets of Interest")
    
    # Twitter accounts to fetch tweets from
    twitter_accounts = ["ASCO", "myESMO", "Medscape", "JAMA_current", "NIH"]
    
    # Fetch tweets
    tweets = fetch_tweets_from_accounts(keywords, twitter_accounts)
    
    if tweets:
        for tweet in tweets:
            st.write(f"**Tweet:** {tweet['text']}")
            st.write(f"**Matches:** {', '.join(tweet['matches'])}")
            st.write(f"**Created At:** {tweet['created_at']}")
            st.write(f"**Likes:** {tweet['likes']} | **Retweets:** {tweet['retweets']}")
            st.write("---")
    else:
        st.write("No tweets found matching your keywords. Try adjusting your search terms.")
