
##different than mac code that was working, made to be general 
##https://support.medpagetoday.com/hc/en-us/articles/206269823-RSS-Feeds

##needs to be adapted for user input and cleaned up a bit
## query limits and boundaries 
## other clean up
## potential to match specialty to specific url to query as well
## 

import feedparser
import requests
import streamlit as st

# Helper function to fetch and parse RSS feeds
def fetch_rss_feed(rss_url):
    headers = {

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml;q=0.9, */*;q=0.8',
    }
    try:
        return _fetch_and_parse_feed(rss_url, headers)
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the RSS feed: {e}")
        st.write(rss_url)
        return []


# Function to fetch and parse the RSS feed
def _fetch_and_parse_feed(rss_url, headers):
    # Use requests to fetch the RSS feed
    response = requests.get(rss_url, headers=headers, timeout=10)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
    
    
    # Parse the RSS feed using feedparser
    rss_data = response.content
    feed = feedparser.parse(rss_data)

    if feed.bozo:
        st.error("Error parsing the RSS feed.")
        return []
    return feed.entries


