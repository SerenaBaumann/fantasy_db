import pandas as pd 
import numpy as np
import requests 
import csv
import time
from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.parse





 #opening the fantasy csv file 
fantasy = pd.read_csv('fantasybooks.csv')


#cleaning the strings and putting the authors into lists

fantasy['Author'] = fantasy['Author'].str.replace(r'(\w)\.(?=\w)', r'\1. ', regex=True) #with this in particular, i'm  basically splitting the letters that are separated by a period and have no space in between 
fantasy['Author'] = fantasy['Author'].str.replace('/', ' / ')
fantasy['Author'] = fantasy['Author'].str.replace(r'\s+', ' ', regex=True)
fantasy['Author'] = fantasy['Author'].str.strip()
fantasy['Author'] = fantasy['Author'].str.split(" / ")

#splitting the authors in the lists so that each string has a row for itself

fantasy_ex = fantasy.explode("Author")

print(fantasy_ex)





#creating a function to query the wikidata needed so that i can loop through the authors column

def querying_wikidata(name):
    
    url = 'https://query.wikidata.org/sparql' #giving the sparql url for wikidata 
    name_econding = urllib.parse.quote(name)
    #writing the sparql query, where i chose the information i would like to extract, alongside with the prefixes 
    #that can be found in the wikiinfo page
    sparql_query = f"""
    prefix schema: <http://schema.org/>
    SELECT ?person ?personLabel ?dob ?nationalityLabel
    WHERE {{
        ?person wdt:P31 wd:Q5;
                rdfs:label "{name}"@en;
                wdt:P569 ?dob;
                wdt:P27 ?nationality.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    LIMIT 1
    """
    #requesting permission to get the data, based on the parameters given, and the url 
    req = requests.get(url, params ={'format': 'json', 'query': sparql_query})  
    #if the request status is approved then getting the information 
    #otherwise, printing an error with the code, as to see where the error lies
    if req.status_code == 200:
    
        return req.json()
    else: 
        print(f'Error for {name}: {req.status_code} - {req.text}')
    return None

#dropping the duplicates of authors
unique_authors = fantasy_ex['Author'].drop_duplicates()
#creating and empty dictionary 
author_results = {}
#looping through the unique authors and calling the function 
for author in unique_authors: 
    result = querying_wikidata(author)
    if result: 
        author_results[author] = result
        print(f"Result for {author}: {result}")
    time.sleep(2)



#finally converting the dictionary into a new dataframe which will then be merged. 

final_author_info_df = pd.DataFrame.from_dict(author_results, orient='index')












       


