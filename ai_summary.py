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
def summarize_content(url, provider_role, specialty, age_group, disease_interest, drug_interest, additional_keywords=None):
    try:
        # Fetch and extract content from URL
        content = extract_main_content(fetch_url_content(url)) 
        
        if not content:
            return "Error: No content found at the provided URL."
        
        # Ensure API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OpenAI API key not found."
        
        client = OpenAI(api_key=api_key)

        # Build user-specific context for summarization
        user_context = (
            f"You are summarizing this for a {provider_role}. "
            f"The specialty of interest is {specialty}. "
            f"Focus on patients in the {age_group} age group. "
            f"Highlight key findings about the disease of interest: {disease_interest}. "
            f"Discuss findings related to drug interest: {drug_interest}. "
        )
        
        # Append additional context keywords if provided
        if additional_keywords:
            keywords_str = ", ".join(additional_keywords)
            user_context += f" Additional context keywords: {keywords_str}."
        
        # Create the OpenAI completion request
        completion = client.chat.completions.create(
            model="gpt-4",  # Use the correct model name
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes research papers efficiently."},
                {"role": "user", "content": f"{user_context} Here is the content of a research paper that I would like summarized: {content}"}
            ]
        )
        
        # Return the summary content from the API response
        return completion.choices[0].message.content
    
    except Exception as e:
        return f"An error occurred while summarizing the content: {str(e)}"
