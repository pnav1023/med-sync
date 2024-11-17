
##different than mac code that was working, made to be general 
##https://support.medpagetoday.com/hc/en-us/articles/206269823-RSS-Feeds

##needs to be adapted for user input and cleaned up a bit
## query limits and boundaries 
## other clean up
## potential to match specialty to specific url to query as well
## 

import feedparser
import urllib.request

# URL for MedPage Today RSS Feed
RSS_URL = "https://www.medpagetoday.com/rss/headlines.xml"

def fetch_rss_feed():
    """
    Fetch and parse the RSS feed using custom headers to avoid 403 errors.
    """
    try:
        # Set up custom headers to simulate a browser request (generic user-agent)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Create a request with the headers
        request = urllib.request.Request(RSS_URL, headers=headers)

        # Fetch the RSS feed using urllib and the custom headers
        with urllib.request.urlopen(request) as response:
            rss_data = response.read()

        # Parse the RSS data using feedparser
        feed = feedparser.parse(rss_data)

        # Check for errors in feed parsing
        if feed.bozo:
            print("Error fetching the RSS feed.")
            print(f"Error details: {feed.bozo_exception}")
            return None

        return feed.entries

    except Exception as e:
        print(f"An unexpected error occurred while fetching the RSS feed: {e}")
        return None

def filter_articles(entries, keyword):
    """
    Filter feed entries for articles that contain the keyword.

    Args:
        entries: List of feedparser entries.
        keyword: The keyword to filter articles by.

    Returns:
        List of filtered articles.
    """
    filtered = []
    for entry in entries:
        title = entry.get("title", "").lower()
        summary = entry.get("summary", "").lower()
        if keyword.lower() in title or keyword.lower() in summary:
            filtered.append(entry)
    return filtered

def display_articles(articles):
    """
    Display the filtered articles to the user.
    """
    if not articles:
        print("\nNo articles found for your search.")
        return

    print("\nFiltered Articles:")
    for idx, article in enumerate(articles, start=1):
        print(f"{idx}. {article.get('title', 'No Title')}")
        print(f"   Link: {article.get('link', 'No Link')}")
        print(f"   Published: {article.get('published', 'No Date')}\n")

def main_ui():
    """
    Main UI function to fetch, filter, and display RSS feed articles.
    """
    print("Fetching articles from MedPage Today...")
    entries = fetch_rss_feed()
    if not entries:
        return

    keyword = input("Enter a keyword to search for articles: ").strip()
    if not keyword:
        print("Keyword cannot be empty. Please try again.")
        return

    filtered_articles = filter_articles(entries, keyword)
    display_articles(filtered_articles)

if __name__ == "__main__":
    main_ui()
