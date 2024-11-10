import requests

def search_pubmed(term, max_results=5):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    details_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": max_results
    }
    
    # Perform search
    search_response = requests.get(base_url, params=params)
    search_data = search_response.json()

    if "esearchresult" in search_data:
        id_list = search_data["esearchresult"]["idlist"]
        if not id_list:
            return "No results found."

        # Fetch article details
        details_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json"
        }
        details_response = requests.get(details_url, params=details_params)
        details_data = details_response.json()
        articles = details_data["result"]
        results = []
        for article_id in id_list:
            article = articles.get(article_id)
            if article:
                results.append({
                    "Title": article.get('title', 'N/A'),
                    "Source": article.get('source', 'N/A'),
                    "PubDate": article.get('pubdate', 'N/A'),
                    "URL": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}",
                    "Authors": article.get('authors', ['N/A']),
                })
        return results
    else:
        return "Failed to retrieve data from PubMed API."

# Use the function
search_term = "cancer treatment"
search_pubmed(search_term, max_results=3)
