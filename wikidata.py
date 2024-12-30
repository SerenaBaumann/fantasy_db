import pandas as pd 
import numpy as np
import sqlite3
import requests 
import csv
import time
from SPARQLWrapper import SPARQLWrapper, JSON

# #opening the fantasy csv file 

fant = pd.read_csv(("fantasybooks.csv"))


#slicing the dataframe into the column i need

authors = fant["Author"]


#saving it to a new csv file 

authors.to_csv('authors_fantasy.csv', index = False, encoding = 'utf-8')

authors_fant = pd.read_csv('authors_fantasy.csv')
#authors_fant


#splitting the authors into single strings 

#authors_fant['Author'] = authors_fant['Author'].str.split(" /  ")#.str.join(", ").str.replace(" ' ", "")
authors_fant['Author'] = authors_fant['Author'].str.replace('/', ' / ')  # Ensure spaces around the slash
authors_fant['Author'] = authors_fant['Author'].str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with a single space
authors_fant['Author'] = authors_fant['Author'].str.strip()
authors_fant['Author'] = authors_fant['Author'].str.split(" / ")


authors_fant



#creating a series 

authors_fantas = authors_fant["Author"]
print(authors_fantas)



#since my series contains single strings with many authors in it
#i am opening the dataframe series as a list, looping throuhg it
#splitting the strings through the / marker, so that in the list i have only single strings per author
#since in the dataframe its not possible to keep different values inside the same column that aren't inside a list
#i could split the lists of authors into multiple columns but that looks messy for now


#preparing an emoty set
#since sets don't have duplicates 
final_authors = set()


#nested loop since we have lists with multiple authors
# looping through each list of authors in authors_fantas
for author_list in authors_fantas:
    # looping through each individual author in the list
    for author_name in author_list:
       #looping through eachh string in the list and split authors by '/'
        individual_authors = [author.strip() for author in author_name.split(' / ')]
        # putting the authors into a set so i remove duplicayes
        final_authors.update(individual_authors)

# converting the set back to a list
final_authors = list(final_authors)

print(final_authors)


#link for the query 

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")



#function to query through all the authors names in my list

def query_wikidata(name):
    url = 'https://query.wikidata.org/sparql'
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
    
    r = requests.get(url, params={'format': 'json', 'query': sparql_query})
    
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error for {name}: {r.status_code}")
        return None

# Loop through each row in your DataFrame (assuming 'Author(s)' is the column with lists of auth
for name in final_authors:  # Iterate over each author in the list
        
        # Execute query with retry logic
        result = None
        attempts = 0
        while result is None and attempts < 2:
            result = query_wikidata(name)
            
            if result is None:
                attempts += 1
                wait_time = 2 ** attempts  # Exponential backoff
                print(f"Retrying in {wait_time} seconds for {name}...")
                time.sleep(wait_time)
        
        if result:
            # Process the result (example: print or store)
            print(f"Result for {name}: {result}")
        
        time.sleep(2)





#next step would be to save this results into either a json file or a csv
#the csv then needs to be flattened --> since the query result is full of nested dictionaries
#TRY to merge the two csv files so that i don't lose the correspondence between authors
#the main csv file is still clean, the authors aren't split neither in lists nor in single strings --> could try to 
#split the authors into several columns, in that case the query can iterate through several columns 




