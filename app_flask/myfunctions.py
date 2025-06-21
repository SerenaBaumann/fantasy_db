import requests 
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()
direct = os.path.join('')

#functions to retrieve the data from the API

API_KEY = os.getenv("API_KEY")



def get_api_books(): 

    NG_API_URL_Books = os.getenv("NG_API_URL_Books")
    #try: 

    request1 = requests.get(NG_API_URL_Books, headers = {"Content-Type": "application/json", 
                                                             "Authorization": f'Bearer {API_KEY}'})
       # request1.raise_for_status()        
    json_data_books = request1.json()

      #  data = json_data_books["data"]

     #   return data, None
    #except requests.exceptions.HTTPError as http_error: 
     #   return None, f"HTTP error occured: {http_error}"
    
    #except KeyError:
      #  return None, f"API limit reached. Please try again in 15 minutes. Sorry for the inconvenience!"
    
    #except Exception as e: 
     #   return None, f"An unexpected error has occurred: {str(e)}"



    return json_data_books



def get_api_authors():

    NG_API_URL_Authors = os.getenv("NG_API_URL_Authors")
    request2 = requests.get(NG_API_URL_Authors, headers = {"Content-Type": "application/json", "Authorization": f'Bearer {API_KEY}'})
    json_data_authors = request2.json()

    return json_data_authors


def get_api_ph():
    
    NG_API_URL_Pubhouse = os.getenv("NG_API_URL_Pubhouse")

    request3 = requests.get(NG_API_URL_Pubhouse, headers = {"Content-Type": "application/json", "Authorization": f'Bearer {API_KEY}'})
    json_data_ph = request3.json()

    return json_data_ph

#since the API response is in raw JSON format, we're creating a hashmap to facilitate the extraction of the needed data 

b_hashmap = {"Book_id": "34154", 
                "Book_title": "34155",
                "Book_author": "34156",
                "Publication_date": "34157",
                "Publishing_house": "34158",
                "isbn": "34159",
                "language": "34161",
                "genre": "34162",
                "subgenre": "34163"}
            

#creating the classes for Person, Book, and Publishing House

class Person: 
    """This is a class for the auhtors"""
    
    


    def __init__(self, Author_name, Author_dob, Author_country, Author_uri): 
        self.Author_name = Author_name
        self.Author_dob = Author_dob
        self.Author_country = Author_country
        self.Author_uri = Author_uri
        


class PH: 
    """This class stands for the publishing houses"""

    

    def __init__(self, PH_name, ph_url):
        self.PH_name = PH_name
        self.ph_url = ph_url
        
#the book class will have an inbuilt class method to clean the subgenres strings

class Book: 
    """This class stands for the book information gathered from the ng database"""
    
    

    def __init__(self, bookid, booktitle, bookauthor: Person, pubdate, pubhouse: PH, isbn, language, genre, subgenre):
        self.bookid = bookid
        self.booktitle = booktitle
        self.bookauthor = bookauthor
        self.pubdate = pubdate
        self.pubhouse = pubhouse
        self.isbn = isbn
        self.language = language
        self.genre = genre
        self.subgenre = subgenre
        
        

    @staticmethod
    def cleaning_subgenres(books_dict):
        for b in books_dict.values():
            if isinstance(b.subgenre, str):

                b.subgenre = b.subgenre.strip("'\" ")
                #b.subgenre = []
                if b.subgenre.startswith("[") and b.subgenre.endswith("]"):
                    b.subgenre = b.subgenre[1:-1]
                    sg_it = b.subgenre.split(",") 
                    b.subgenre = [sg.strip(" '\" ") for sg in sg_it if sg.strip()]

                else: 
                    b.subgenre = [sg.strip("'\" ") for sg in b.subgenre.split(",") if sg.strip()]

#functions to retrieve the book data from the API response

def get_book_values(bookdata, ng_id):
    ng_id_values = b_hashmap.get(ng_id)
    values = bookdata["object_definitions"].get(ng_id_values, {}).get("object_definition_value", "Unknown")
    return values 

#function to populate the book class

def get_book():    
    books = {}

    ng_json_data = get_api_books()

    #iterating through key-value pairs (in this case the key is book_id and the values are the bookdata)
    for book_id, bookdata in ng_json_data["data"]["objects"].items():
        
        book_id = bookdata["object"].get("nodegoat_id")
         
        book_obj = Book(
            bookid=book_id,
            booktitle=get_book_values(bookdata, "Book_title"),
            bookauthor=get_book_values(bookdata, "Book_author"),
            pubdate=get_book_values(bookdata, "Publication_date"),
            pubhouse=get_book_values(bookdata, "Publishing_house"),
            isbn=get_book_values(bookdata, "isbn"),
            language=get_book_values(bookdata, "language"),
            genre=get_book_values(bookdata, "genre"),
            subgenre=get_book_values(bookdata, "subgenre")
        )

        books[book_id] = book_obj
     

    return books




all_books_class = get_book()


Book.cleaning_subgenres(all_books_class)

#a function to extract all the subgenres present in the database, with attached the relative book title

def get_sgenre(books):
    sub_genre_dict = {"fantasy": {}}
    for b in books.values():
        if b.genre.lower() == 'fantasy': 
            for sg in b.subgenre:
                if sg not in sub_genre_dict["fantasy"]:
                    sub_genre_dict["fantasy"][sg] = []  

                sub_genre_dict["fantasy"][sg].append(b.booktitle)  

    return sub_genre_dict


subgen = get_sgenre(all_books_class)


auth_hasmap = {"Author_name": "34152", 
               "Author_dob": "34149",
                "Author_country": "34150",
                  "Author_uri": "34151"}


def get_author_values(author_data, ng_id):
    ng_id_values = auth_hasmap.get(ng_id)
    values = author_data["object_definitions"].get(ng_id_values, {}).get("object_definition_value", "Unknown")
    return values
    


def get_author():

    authors = {}

    ng_json_authors = get_api_authors()


    for auth_name, author_data in ng_json_authors["data"]["objects"].items():

        author_name = get_author_values(author_data, "Author_name")

        auth_obj = Person(
            Author_name = author_name,
            Author_dob = get_author_values(author_data, "Author_dob"),
            Author_country = get_author_values(author_data, "Author_country"),
            Author_uri = get_author_values(author_data, "Author_uri")
        )

        authors[author_name] = auth_obj

    return authors


all_authors = get_author()


def get_ph():

    ph = {}

    ng_json_ph = get_api_ph()

    for phname, ph_data in ng_json_ph["data"]["objects"].items():
        ph_name =  ph_data["object"]["object_name"]
        
        #ph_object = PH(
         #   ph_url = ph_data["object_definitions"].get("34466", {}).get("object_definition_value", "Unkown"),
          #  ph_name = ph_name)


        ph[ph_name] = ph_name
     
    return ph
        


all_ph = get_ph()




#creating a dictionary for each author in the database that shows their book titles and the corresponding publishing dates
#  
bookxauthor = {}

for book_id, b in all_books_class.items():

    if b.bookauthor not in bookxauthor:
        bookxauthor[b.bookauthor] = []

    bookxauthor[b.bookauthor].append({
      "Book Title": b.booktitle,
       
        "Pub Date": b.pubdate, 

        "Book_id": b.bookid  
    }) 


def correct_js(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

#function to plot the timeline of the authors's publishing history 

def timeline_authors(author_name, books):

    books.sort(key= lambda b: b["Pub Date"])

    titles = [book["Book Title"] for book in books]
    dates = [datetime.fromisoformat(book["Pub Date"]) for book in books]

    #fig = go.Figure()
    
    hovertext= [correct_js(f"<b>{title}</b><br>{date.strftime('%B %d, %Y')}") for title, date in zip(titles, dates)]


    
    fig= go.Figure(data=go.Scatter(
        x = dates,
        y =list(range(1, len(dates)+1)),  
        mode= "markers+lines",
        marker=dict(size=12, color="#62dad6"),
        text = titles,
        hovertext= hovertext,
        hoverinfo="text"
    ))

    fig.update_layout(
        title= dict(text= f"{author_name}'s Publishing Timeline", x= 0.5, font= dict(size= 22, family= "-apple-system, BlinkMacSystemFont, 'SegoeUI', Roboto, 'Helvetica Neue', Arial sans-serif")),
        xaxis = dict(title= "Publication Date", tickformat= "%Y-%m-%d", tickmode='auto',
                     dtick='M6', showgrid= False, gridcolor= "#e5ecf6", zeroline= False),
        yaxis = dict(visible= False),
        font= dict(family= "-apple-system, BlinkMacSystemFont, 'SegoeUI', Roboto, 'Helvetica Neue', Arial sans-serif", size= 14, color= "black"),
        showlegend = False,
        height = 800, 
        margin = dict(t=60, b=40),
        paper_bgcolor= "#fafafa",
        plot_bgcolor = "#ffffff")

    return fig

#function to link each author to the subgenres in which they have written

def get_auth_sg(books):
    auth_sg= {}
    for b in books.values():
        authors = [b.bookauthor] if isinstance(b.bookauthor, str) else b.bookauthor
        for a in authors:
            if a not in auth_sg:
                auth_sg[a] = {}
            for sg in b.subgenre:
                if sg not in auth_sg[a]:
                    auth_sg[a][sg] = []
                auth_sg[a][sg].append(b.booktitle)
    return auth_sg



#function to plot a chart that shows the subgenres in which the authors have written

def plot_sgxauthor(authr_nm, data): 
    genres = data[authr_nm]
    b_counts = []
    b_titles = []
    gnr_names = []

    for g, b in genres.items():
        gnr_names.append(g)
        #gnr_names = sorted(gnr_names)
        b_counts.append(len(b))
        b_titles.append("<br>".join(b))

    colors= px.colors.qualitative.Plotly
    bubble_colors = colors[:len(gnr_names)]


    fig = go.Figure(data = [
        go.Pie(
            labels = gnr_names,#[authr_nm, * gnr_names],
            #parents = ["",*[authr_nm] * len(gnr_names)], 
            values = b_counts,#[None] + b_counts,
            hovertext = b_titles,#[""] + b_titles,
            hoverinfo = "label + text",# + value",
            textinfo='label+percent',
            textposition='inside',
            insidetextorientation='radial'
        )
    ])

    fig.update_layout(width= 600, height = 800, showlegend= True, 
                      font= dict(family= "-apple-system, BlinkMacSystemFont, 'SegoeUI', Roboto, 'Helvetica Neue', Arial sans-serif",
                                  size= 14, color= "black"), 
                      title= f"Book Count per Genre for {authr_nm}")#, xaxis_title= "Genre", yaxis_title="Number of Books")

    return fig



if __name__ == "main":
    all_books_class
    all_authors
    all_ph
    subgen
    bookxauthor
    timeline_authors
    get_auth_sg
    plot_sgxauthor
    



