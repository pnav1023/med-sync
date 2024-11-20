
##different than mac code that was working, made to be general 
##https://support.medpagetoday.com/hc/en-us/articles/206269823-RSS-Feeds

##needs to be adapted for user input and cleaned up a bit
## query limits and boundaries 
## other clean up
## potential to match specialty to specific url to query as well
## 

import feedparser
import urllib.request
import streamlit as st

# URL for MedPage Today RSS Feed
RSS_URL = "https://www.medpagetoday.com/rss/headlines.xml"

# Helper function to fetch and parse RSS feeds
def fetch_rss_feed(rss_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        request = urllib.request.Request(rss_url, headers=headers)
        with urllib.request.urlopen(request) as response:
            rss_data = response.read()
        feed = feedparser.parse(rss_data)
        if feed.bozo:
            st.error("Error fetching the RSS feed.")
            return []
        return feed.entries
    except Exception as e:
        st.error(f"An error occurred while fetching the RSS feed: {e}")
        return []
