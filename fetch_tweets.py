import requests
import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import time


load_dotenv()  # Load environment variables from .env file

@st.cache_data
def fetch_tweets_from_accounts(accounts, max_results=10):
    """
    Fetch recent tweets from specified Twitter accounts.
    
    Args:
        accounts (list): Twitter handles to fetch tweets from (without the @ symbol).
        max_results (int): The maximum number of tweets to return per account.
    
    Returns:
        list: A list of tweets with metadata.
    """
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        st.error("Twitter Bearer Token is not set. Please configure it in your .env file.")
        raise ValueError("Twitter Bearer Token is not set.")

    headers = {"Authorization": f"Bearer {bearer_token}"}
    base_url = "https://api.twitter.com/2/tweets/search/recent"
    all_tweets = []

    for account in accounts:
        query = f"from:{account} lang:en"
        params = {"query": query, "tweet.fields": "created_at,text,public_metrics", "max_results": max_results}

        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                response = requests.get(base_url, headers=headers, params=params)
                if response.status_code == 200:
                    tweets = response.json().get("data", [])
                    for tweet in tweets:
                        tweet_data = {
                            "text": tweet["text"],
                            "created_at": datetime.strptime(tweet["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                            "likes": tweet["public_metrics"]["like_count"],
                            "retweets": tweet["public_metrics"]["retweet_count"]
                        }
                        all_tweets.append(tweet_data)
                    break
                elif response.status_code == 429:
                    st.warning(f"Rate limit reached for @{account}, retrying in 15 minutes...")
                    time.sleep(15 * 60)  # Wait 15 minutes
                else:
                    st.error(f"Error fetching tweets for @{account}: {response.status_code}")
                    break
            except Exception as e:
                st.error(f"An error occurred while fetching tweets for @{account}: {str(e)}")
                break

    return all_tweets
