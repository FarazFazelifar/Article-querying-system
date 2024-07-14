"pip install arxiv biopython pybliometrics"

import arxiv
from Bio import Entrez
from Bio import Medline
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import ScopusQueryError
import json
import os
import pandas as pd

user_email = "example@gmail.com" #change this when using

def search_arxiv(query, max_results=10):
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    results = []
    for paper in client.results(search):
        results.append({
            "title": paper.title,
            "doi": paper.doi if paper.doi else "N/A",
            "abstract": paper.summary
        })

    return results


def search_pubmed(query, max_results=10):
    Entrez.email = user_email
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()

    id_list = record["IdList"]

    results = []
    handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
    records = Medline.parse(handle)

    for record in records:
        title = record.get("TI", "N/A")
        abstract = record.get("AB", "N/A")
        doi = next((id for id in record.get("AID", []) if id.endswith("[doi]")), "N/A")

        results.append({
            "title": title,
            "doi": doi.replace(" [doi]", "") if doi != "N/A" else doi,
            "abstract": abstract
        })

    handle.close()

    return results


def search_scopus(query, max_results=10):
    config_file = os.path.expanduser('~/.scopus/config.ini')
    if not os.path.exists(config_file):
        print("Scopus configuration not found. Please set up your config.ini file.")
        return []

    try:
        s = ScopusSearch(query, subscriber=True)

        results = []
        for i, result in enumerate(s.results):
            if i >= max_results:
                break

            results.append({
                "title": result.title,
                "doi": result.doi if result.doi else "N/A",
                "abstract": result.description if result.description else "N/A"
            })

        return results
    except ScopusQueryError as e:
        print(f"Error searching Scopus: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error occurred while searching Scopus: {e}")
        return []


def search_all(query, max_results=10):
    arxiv_results = search_arxiv(query, max_results)
    pubmed_results = search_pubmed(query, max_results)
    scopus_results = search_scopus(query, max_results)

    return arxiv_results + pubmed_results + scopus_results


if __name__ == "__main__":
    query = input("Enter your search query: ")

    results = search_all(query)

    df = pd.DataFrame.from_dict(results)

    print(df)

