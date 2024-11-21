import openai
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

# Load environment variables
load_dotenv()

def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.text  # Returns the raw HTML or text content
    except requests.RequestException as e:
        print(f"Error fetching URL content: {e}")
        return None

def extract_main_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()  # Extract text from the entire HTML document

def summarize_content(url, disease_interest, drug_interest):
    # Fetch content from URL
    content = fetch_url_content(url)
    if not content:
        return "Failed to fetch content from the URL."
    
    content = extract_main_content(fetch_url_content(url))

    # Set OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        raise ValueError("OpenAI API key is not set. Check your .env file.")

    # Build user-specific context for summarization
    user_context = (
        f"Highlight key findings about the disease of interest: {disease_interest}. "
        f"Discuss findings related to drug interest: {drug_interest}."
    )

    try:
        # Generate completion
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes research papers efficiently for clinicians."},
                {
                    "role": "user",
                    "content": f"{user_context} Here is the content of a research paper that I would like summarized: {content}."
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:  # Catch all exceptions
        print(f"OpenAI API error: {e}")
        return f"An error occurred: {e}"


