
import pandas as pd 
import requests 
import csv
import time
from SPARQLWrapper import SPARQLWrapper, JSON




books = pd.read_csv(("Goodreads_books_with_genres.csv"))


#Start cleaning the whole dataframe of the main points:
#getting the information about the data type in the dataframe
#dropping the NaN
#dropping the duplicates

books.replace(['', 'None', 'N/A', 'null', ' '], pd.NA, inplace=True)
books = books.dropna()
books.info()


books.drop_duplicates()

books.select_dtypes(include='object')

#standardizing the strings 
# looking in the dataframe e seeing where problems may arise: genres and possibly authors. 
# 1. putting spaces in between words
# 2. separating the genres with a comma instead of a semicolon 


books['genres'] = books['genres'].str.split(";")#.str.join(", ").str.replace(" ' ", "")
books['genres']



#converting the 'objects' into either str or int,

strings = ['Title', 'Author', 'isbn', 'language_code', 'publisher']
for n in strings:
    books[n] = books[n].fillna('').astype(str).str.strip()


#making a list of the columns i want to drop and dropping them
col_drop = ["ratings_count", "text_reviews_count", "average_rating"]
books = books.drop(columns=col_drop, axis=1)

#separating the strings of the authors names to facilitate the search

books['Author'] = books['Author'].str.replace('/', ' / ')  # putting spaces around the slash
books['Author'] = books['Author'].str.replace(r'\s+', ' ', regex=True)  # replacing eventual multiple spaces with a single space
books['Author'] = books['Author'].str.strip()

#converting the date format into a standard one --> then making the object into a datatime

books['publication_date'] = books['publication_date'].astype(str)
books['publication_date'] = books['publication_date'].str.strip().str.replace('/', '-')

invalid_Dates = books[books['publication_date'].isna()] #trying to find the dates that raise errors
print(invalid_Dates) #printing them out and then modifying them manually 

books['publication_date'] = books['publication_date'].replace('11-31-2000', '11-30-2000')
books['publication_date'] = books['publication_date'].replace('6-31-1982', '6-30-1982')



#converting all the dates to the type datetime


books['publication_date'] = pd.to_datetime(books['publication_date'])

print(books['publication_date'].dtype)


#checking for residual duplicates, especially in the title column and dropping them 

books['Title'] = books['Title'].drop_duplicates()

print(books['Title'].value_counts()) #checking if all the titles now are singular occurences

#slicing the dataframe according to the 'Fantasy' parameter by using the pandas apply method and an anonymous function
#also the genres here are kept in a list of strings
#making a copy so it doesn't raise the Copy error since i'm trying to modify only a slice of the database


fantasy_books = books[books['genres'].apply(lambda x: 'Fantasy' in x)].copy()


# looping through the dataframe in order to separate the genres from the subgenres
# if the conditions of the loop are already met (if 'Fantasy' in genre) the else statement should avoid 
# looping twice through the dataframe (it does not)

genres = []
subgenres = []



for genre in fantasy_books['genres']: 
    if 'Fantasy' in genre: 
        genres.append('Fantasy')
        subgenres.append([x for x in genre if x != 'Fantasy'])
    else:
        genres.append(genre) #trying to stop the loop if the conditions of the first statement are already met
        subgenres.append([]) 

#adding the lists to the data frame columns 
fantasy_books['genres'] = genres 
fantasy_books['sub_genres'] = subgenres


#fantasy_books['sub_genres'].head()
print(fantasy_books)

#saving the sliced dataframe in a new csv file. 
fantasy_books.to_csv('fantasybooks.csv', index=False, encoding='utf-8')




























