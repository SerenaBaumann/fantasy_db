from flask import render_template, request
from app_flask.myfunctions import  get_author, get_book, get_ph, get_sgenre, timeline_authors, bookxauthor, plot_sgxauthor, get_auth_sg
from app_flask.myfunctions import Book
from app_flask import app
from plotly.utils import PlotlyJSONEncoder
import plotly.graph_objs as go
#from top import top10, sorted_POP
from matplotlib import pyplot as plt
import json
from json import dumps



all_books_class = get_book()
Book.cleaning_subgenres(all_books_class)
all_authors_class = get_author()
all_ph_class = get_ph()

subgen = get_sgenre(all_books_class)









@app.route("/")
def home():


    all_authors = set()
    all_ph= set()

    for book_id, book in all_books_class.items():
        if book.bookauthor:
            all_authors.add(book.bookauthor)
        if book.pubhouse:
            all_ph.add(book.pubhouse)        


    all_authors = sorted(all_authors)
    all_ph = sorted(all_ph)
    all_sg = sorted(subgen['fantasy'].keys())


    return render_template("home.html", title= "Homepage", all_sg=all_sg, all_authors=all_authors, all_ph=all_ph)



@app.route("/search", methods =["GET", "POST"])
def search():
    query = request.args.get('q', '').strip().lower()
    results = []
    if query:
        for book_id, book in all_books_class.items(): 
            title = (book.booktitle or '').lower()
            author = (book.bookauthor or '').lower()
            publishing = (book.pubhouse or '').lower()
            if isinstance(book.subgenre, list):
                subgenre = ' '.join([sg.lower() for sg in book.subgenre if sg])
            else: 
                subgenre = (book.subgenre or '').lower()
        
            if query in title or query in author or query in publishing or query in subgenre:
                results.append((book_id, book))

                #no_results_message= "Sorry, there are no books matching your search query 🥲"
                
    return render_template("home.html", results = results, q=query)



@app.route("/advanced_search_results")
def advanced_search_results(): 

    selected_sg = request.args.getlist("subgenres")
    selected_authors = request.args.getlist("authors")
    selected_ph = request.args.getlist("publishing_houses")

    filt_books = []

    if selected_sg:
        for sg in selected_sg:

            sg_titles = subgen['fantasy'].get(sg, [])
            filt_books.extend(sg_titles)
    else: 
        for sg_titles in subgen['fantasy'].values():
            filt_books.extend(sg_titles)

    results = []

    for book_id, book in all_books_class.items():
        match_sg = not selected_sg or all(sg in book.subgenre for sg in selected_sg)
        #book.booktitle in filt_books
        match_authors = not selected_authors or book.bookauthor in selected_authors
        match_phs = not selected_ph or book.pubhouse in selected_ph

        if match_sg and match_authors and match_phs:
            results.append((book_id, book))


    all_authors = set()
    all_ph= set()

    for book_id, book in all_books_class.items():
        if book.bookauthor:
            all_authors.add(book.bookauthor)
        if book.pubhouse:
            all_ph.add(book.pubhouse)          


    all_authors = sorted(all_authors)
    all_ph = sorted(all_ph)
    all_sg = sorted(subgen['fantasy'].keys())

    no_results_message = None
    if not results: 
        no_results_message= "Sorry, there are no books matching your search query 🥲"
    


    return render_template("home.html", results= results, all_sg = all_sg, all_authors=all_authors, all_ph= all_ph,
                            no_results_message= no_results_message)





@app.route('/books')
def all_books():
    sorted_titles = sorted(all_books_class.items(), key= lambda item: item[1].booktitle.lower())
    alphabet = [chr(i) for i in range(ord('a'), ord('z')+1)]

    titles_by_letter = {l: [] for l in alphabet}
    titles_by_letter['#'] = []

    for book_id, book in sorted_titles: 

        fl = book.booktitle[0].lower()

        if fl in titles_by_letter: 
            titles_by_letter[fl].append((book_id, book))
        else:
            titles_by_letter['#'].append((book_id, book))

    return render_template("books.html", the_books= titles_by_letter, alphabet = alphabet + ['#'])


@app.route('/books/<book_id>')
def book_info(book_id):
    book = all_books_class.get(book_id)

    return render_template("book_info.html", book_inform = book)


@app.route('/authors')
def all_authors_funct():
    author_names = list(all_authors_class.keys())
    sorted_author_names = sorted(author_names)

    alphabet = [chr(i) for i in range(ord('a'),ord('z')+1)]
    authors_for_letter = {}
    for l in alphabet: 
        authors_for_letter[l] = [a for a in sorted_author_names if a.lower().startswith(l)]


    return render_template("authors.html", the_authors = authors_for_letter, alphabet = alphabet) 



@app.route('/authors/<authorname>')
def author_infor(authorname):
    
    auth = all_authors_class.get(authorname)
    author_book_titles = [(book_id, b) for book_id, b in all_books_class.items() if b.bookauthor == authorname]
   
    authtimeline = bookxauthor.get(authorname)
    
    fig1 = timeline_authors(authorname, authtimeline)
    plotJson1 = json.dumps(fig1, cls= PlotlyJSONEncoder)

    data_sgxauth = get_auth_sg(all_books_class)

    fig2 = plot_sgxauthor(authorname, data_sgxauth)
    plotJson2 = json.dumps(fig2, cls= PlotlyJSONEncoder)
    

    return render_template("authors_info.html", author_info = auth, bookstitles = author_book_titles, plotJson1 = plotJson1,
                           plotJson2 = plotJson2)



@app.route('/publishinghouses')
def all_ph_function():
    
    
    #theph_names = list(all_ph_class.keys())
    #sorted_phs = sorted(theph_names)

    #alphabet = [chr(i) for i in range(ord('a'), ord('z')+1)]

    #ph_for_letter = {}
    #for l in alphabet: 
     #    ph_for_letter[l] = [ph for ph in sorted_phs if ph.lower().startswith(l)]


    return render_template("ph.html", the_phs = sorted(all_ph_class.keys()))


@app.route('/publishinghouses/<publishinghouse>')
def pub_info(publishinghouse):
    
    ph = all_ph_class.get(publishinghouse)
    ph_book_titles = [(book_id, b) for book_id, b in all_books_class.items() if b.pubhouse == ph]

    return render_template("ph_info.html", ph_information = ph, ph_book_titles = ph_book_titles)



@app.route('/subgenres')
def subgenres():
    sorted_sg = sorted(subgen['fantasy'])
    
    alphabet = [chr(i) for i in range(ord('a'), ord('z')+1)]

    sg_for_letter = {}
    for l in alphabet: 
        if l == '#':
            sg_for_letter[l] = [sg for sg in sorted_sg if not sg[0].lower().isalpha()]
        else: 

            sg_for_letter[l] = [sg for sg in sorted_sg if sg.lower().startswith(l)]

    return render_template ("subgenre.html", the_sg = sg_for_letter, alphabet = alphabet )




@app.route('/subgenres/<sg_name>')
def subgen_books(sg_name):
    books = subgen['fantasy'].get(sg_name, [])
    book_infosss = [(book_id, b) for book_id, b in all_books_class.items() if b.booktitle in books]
    return render_template("subgenre_books.html", subgenre= sg_name, books = book_infosss)








