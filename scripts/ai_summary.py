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

def summarize_content(url):#, provider_role, specialty, age_group, disease_interest, drug_interest, additional_keywords):
    # Use OpenAI API to summarize
    content = extract_main_content(fetch_url_content(url)) 

    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI() #api_key=api_key

    # Build user-specific context for summarization
    # user_context = (
    #     f"You are summarizing this for a {provider_role}. "
    #     f"The specialty of interest is {specialty}. "
    #     f"Focus on patients in the {age_group} age group. "
    #     f"Highlight key findings about the disease of interest: {disease_interest}. "
    #     f"Discuss findings related to drug interest: {drug_interest}. "
    # )
    
    # if additional_keywords:
    #     keywords_str = ", ".join(additional_keywords)
    #     user_context += f"Additional context keywords: {keywords_str}."

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes research papers efficiently."},
            {
                "role": "user",
                "content": f"Here is the content of a research paper that I would like summarized: {content}." # add user context later
            }
        ]
    )

    return completion.choices[0].message.content
