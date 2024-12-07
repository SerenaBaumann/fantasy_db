#prova per tirare fuori il file salvato di goodreads

import csv
import pandas as pd 
import sqlite3



books = pd.read_csv(("Goodreads_books_with_genres.csv"))


#Start cleaning the whole dataframe of the main points:
#getting the information about the data type in the dataframe
#dropping the NaN
#dropping the duplicates

#books.fillna('')

books.info()

books.drop_duplicates()

books.dropna(inplace=True)

books.select_dtypes(include='object')

#standardizing the strings 
# looking in the dataframe e seeing where problems may arise: genres and possibly authors. 
# 1. putting spaces in between words
# 2. separating the genres with a comma instead of a semicolon 

books['genres'] = books['genres'].str.split(";")#.str.join(", ").str.replace(" ' ", "")
books['genres']

#converting the 'objects' into either str

strings = ['Title', 'Author', 'isbn', 'language_code', 'publisher']
for n in strings:
    books[n] = books[n].fillna('').astype(str).str.strip()




#making a list of the columns i want to drop and dropping them
col_drop = ["ratings_count", "text_reviews_count"]
books = books.drop(columns=col_drop, axis=1)



#books.loc[books['publisher'] == 'Bantam Books']

#converting the date format into a standard one --> then making the object into a datatime

books['publication_date'] = books['publication_date'].astype(str)
books['publication_date'] = books['publication_date'].str.strip().str.replace('/', '-')

invalid_Dates = books[books['publication_date'].isna()] #trying to find the dates that raise errors
print(invalid_Dates) #printing them out and then modifying them manually 

books['publication_date'] = books['publication_date'].replace('11-31-2000', '11-30-2000')
books['publication_date'] = books['publication_date'].replace('6-31-1982', '6-30-1982')



#converting all the dates to the type datetime


books['publication_date'] = pd.to_datetime(books['publication_date'])
#books['publication_date'] = pd.to_datetime(books['publication_date'], format='%m-%d-%Y')

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
#ran = False


for genre in fantasy_books['genres']: 
    if 'Fantasy' in genre: #and not ran:
        genres.append('Fantasy')
        subgenres.append([x for x in genre if x != 'Fantasy'])
        #break 
        #ran = True
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

#print(fantasy_books[fantasy_books['Author'] == 'Stephanie Garber']) 
#print(fant)



#ALTERNATIVE TO THE LOOP (doesn't really work)

#def genres_subgenres(row): 

 #   for genre in fantasy_books['genres']:
  #      if 'Fantasy' in genre: 
   #         row['sub_genres'] = [x for x in row['genres'] if x != 'Fantasy']
    #        row['genres'] = 'Fantasy' 
           
     #   return row 



#fantasy_books = fantasy_books.apply(genres_subgenres, axis = 1) 




#starting the database with sqlite --> FIRST TRY, STILL NEED TO TEST IT
#ALSO MISSING: PERSON TABLE, PUBLISHING HOUSE TABLE, AUTHOR TABLE (linked to the person table), 
#evtl. a Saga table (if it makes sense to do one?)



fant = pd.read_csv(("fantasybooks.csv"))
print(fant)
#fantasy_db = squlite3.connect('fantasy_database.db')


#fantasy_db.execute('''
#CREATE TABLE IF NOT EXISTS books (
 #  Id INTEGER PRIMARY KEY AUTOINCREMENT,
  # BookID INT NOT NULL,
   #ISBN INT NOT NULL,
   #ISBN13 INT NOT NULL,
   #Title TEXT,
   #Author TEXT,
   #Language TEXT,
   #PublicationDate DATE,
   #Publisher TEXT, 
   #Genre TEXT, 
   #Subgenres TEXT
#);
#''')


#for book in fant:
 #   fantID = fant["Book Id"] 
  #  fantisbn = fant["isbn"]
   # fantisbn13 = fant["isbn13"]
    #fant_title = fant["Title"]
    #fantAuthor = fant["Author"]
    #fantlangu = fant["language_code"]
    #fantpubldate = fant["publication_date"]
    #fantpubl = fant["publisher"]
    #fantgenres = fant["genres"]
    #fantsubgenres = fant["sub_genres"]
#fantasy_db.execute('INSERT INTO books (fantID,fantisbn, fantisbn13, fan_title, fantAuthor,
#  fantlangu, fantpubldate, fantpubl, fantgenres, fantsubgenres) VALUES (?,?,?,?,?,?,?,?,?,?)',
 #          (fantID,fantisbn, fantisbn13, fan_title, fantAuthor, fantlangu, fantpubldate, fantpubl, fantgenres, fantsubgenres))

#fantasy_db.commit()