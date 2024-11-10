from openai import OpenAI
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

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
    # Example: Extract text from main article section
    content = soup.get_text()
    return content

def summarize_content(url):
    # Use OpenAI API to summarize
    content = extract_main_content(fetch_url_content(url)) 

    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistent that summarizes papers"},
            {
                "role": "user",
                "content": f"Here is a content of a research paper that I would like summarized: {content}."
            }
        ]
    )

    return completion.choices[0].message.content