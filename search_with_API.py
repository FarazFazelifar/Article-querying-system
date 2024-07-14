"pip install requests pandas"

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import pandas as pd

SCOPUS_API_KEY = '0d5fe34056347acc56defa90da7e246a'

def search_arxiv(query, max_results=10):
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=all:{quote(query)}&start=0&max_results={max_results}"
    response = requests.get(base_url + search_query)
    root = ET.fromstring(response.content)

    results = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text
        doi = entry.find('{http://arxiv.org/schemas/atom}doi')
        doi = doi.text if doi is not None else "N/A"
        results.append({"title": title, "doi": doi, "abstract": abstract})

    return results


def search_pubmed(query, max_results=10):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={quote(query)}&retmax={max_results}&usehistory=y"
    search_response = requests.get(search_url)
    search_root = ET.fromstring(search_response.content)

    id_list = [id_elem.text for id_elem in search_root.findall('.//Id')]

    results = []
    for pmid in id_list:
        fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={pmid}&rettype=abstract"
        fetch_response = requests.get(fetch_url)
        fetch_root = ET.fromstring(fetch_response.content)

        title = fetch_root.find('.//ArticleTitle').text
        abstract_elem = fetch_root.find('.//AbstractText')
        abstract = abstract_elem.text if abstract_elem is not None else "N/A"
        doi_elem = fetch_root.find('.//ArticleId[@IdType="doi"]')
        doi = doi_elem.text if doi_elem is not None else "N/A"

        results.append({"title": title, "doi": doi, "abstract": abstract})

    return results


def search_scopus(query, api_key, max_results=10):
    base_url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    params = {
        "query": query,
        "count": max_results,
        "field": "title,doi,description"
    }

    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()

    results = []
    for entry in data.get("search-results", {}).get("entry", []):
        title = entry.get("dc:title", "N/A")
        doi = entry.get("prism:doi", "N/A")
        abstract = entry.get("dc:description", "N/A")
        results.append({"title": title, "doi": doi, "abstract": abstract})

    return results


def search_all(query, scopus_api_key, max_results=10):
    arxiv_results = search_arxiv(query, max_results)
    pubmed_results = search_pubmed(query, max_results)
    scopus_results = search_scopus(query, scopus_api_key, max_results)

    return scopus_results + arxiv_results + pubmed_results


if __name__ == "__main__":
    query = input("Enter your search query: ")
    scopus_api_key = SCOPUS_API_KEY

    results = search_all(query, scopus_api_key)

    df = pd.DataFrame.from_dict(results)

    print(df)