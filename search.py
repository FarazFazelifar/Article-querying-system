import arxiv
from Bio import Entrez
from Bio import Medline
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import ScopusQueryError
import json
import os
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
import threading

import search_with_library
import search_with_API

max_results = 10
dataframes = []

def wrapper1(query: str):
    results = search_with_API.search_all(query=query, scopus_api_key="0d5fe34056347acc56defa90da7e246a", max_results=max_results)
    df = pd.DataFrame.from_dict(results)
    df = df.sort_values(by=['title'], ascending=True)
    dataframes.append(df)

def wrapper2(query: str):
    results = search_with_library.search_all(query=query, max_results=max_results)
    df = pd.DataFrame.from_dict(results)
    df = df.sort_values(by=['title'], ascending=True)
    dataframes.append(df)

def combine_columns(col1, col2):
    return col1.combine_first(col2)

query = input("Please write your query: ")

thread1 = threading.Thread(target=wrapper1(query=query))
thread2 = threading.Thread(target=wrapper2(query=query))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print(dataframes[0].shape, dataframes[1].shape)

merged_df = pd.merge(dataframes[0], dataframes[1], on=['title', 'source'], how='outer', suffixes=('_1', '_2'))

merged_df['doi'] = combine_columns(merged_df['doi_1'], merged_df['doi_2'])

merged_df['abstract'] = combine_columns(merged_df['abstract_1'], merged_df['abstract_2'])

merged_df = merged_df.drop(columns=['doi_1', 'doi_2', 'abstract_1', 'abstract_2'])

merged_df = merged_df.fillna('N/A')

merged_df = merged_df.reset_index(drop=True)

merged_df.to_csv("out.csv")

print(merged_df.shape)
