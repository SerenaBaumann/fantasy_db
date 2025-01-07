import pandas as pd 
import requests 
import csv
import time
from SPARQLWrapper import SPARQLWrapper, JSON






 #opening the fantasy csv file 
fantasy = pd.read_csv('fantasybooks.csv')


#cleaning the strings and putting the authors into lists

fantasy['Author'] = fantasy['Author'].str.replace(r'(\w)\.(?=\w)', r'\1. ', regex=True) #splitting the characters that are separated by a period and have no space in between (ex. J.K. Rowling)  
fantasy['Author'] = fantasy['Author'].str.replace('/', ' / ')
fantasy['Author'] = fantasy['Author'].str.replace(r'\s+', ' ', regex=True)
fantasy['Author'] = fantasy['Author'].str.strip()
fantasy['Author'] = fantasy['Author'].str.split(" / ") #so that the authors are in a list and not a single string

#exploding the authors column so that each string has a row for itself

fantasy_ex = fantasy.explode("Author")

print(fantasy_ex)





#creating a function to query the wikidata needed so that i can loop through the authors column

def querying_wikidata(name):
    
    url = 'https://query.wikidata.org/sparql' #giving the sparql url for wikidata 
    
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
    time.sleep(1)




#organize the dictionary into a clean dataframe 

#preparing an empty list
cleaned_dict = []

#looping trough the author and the results that are contained into the wikidata dictionary
for author, result in author_results.items(): 
    try: #since its a nested dictionary, with 'binding' as the key, trying to get the info from the results and then from the bindings inside. 
        bindings = result['results']['bindings']
        if bindings: #organizing the structure that i would like to unpack from the dictionary
            binding = bindings[0] #first element of the dict
            person_label = binding.get('personLabel', {}).get('value', None) #setting the label for the person, through the values scraped
            person_uri = binding.get('person', {}).get('value', None) #doing the same thing with the person's link, date of birth and nationality 
            dob = binding.get('dob', {}).get('value', None)
            nationality = binding.get('nationalityLabel', {}).get('value', None)
            
            #adding the data into the empty list already prepared, making each value correspond with the results gotten from the wikidata scraping
            cleaned_dict.append({
                'Name': person_label,
                'Person URI': person_uri,
                'Label': person_label,
                'DOB': dob,
                'Nationality': nationality
            })
    except Exception as e: #rising an Error message if some problems occur
        print(f"Error processing data for {author}: {e}")


#now converting the data into a dataframe, it will make the merging with the main dataframe easier.
final_author_info = pd.DataFrame(cleaned_dict)
final_author_info

#saving it to a separate dataframe just in case 
#final_author_info.to_csv('Author_info_final.csv',encoding='utf-8', index=False)


#merging the two dataframes 
#taking the exploded dataframe as primary df, then giving the parameters for the second df i would like to merge
merged_final_f = fantasy_ex.merge(
    final_author_info,
    left_on='Author',
    right_on= 'Name',
    how='inner'
)

print(merged_final_f)



#saving the merged and final dataframe into a csv file 


merged_final_f.to_csv('Final_fantasy_dataframe.csv', encoding=' utf-8')

#final_fant = pd.read_csv(('Final_fantasy_dataframe.csv'))














       


