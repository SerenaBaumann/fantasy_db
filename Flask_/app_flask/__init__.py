from flask import Flask
from datetime import datetime



app = Flask(__name__)

@app.context_processor
def roll_year():
    return{"current_year": datetime.now().year}


from app_flask import myroutes
