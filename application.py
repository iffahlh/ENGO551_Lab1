import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

@app.route("/")
def index():
    session['logged_in'] = session.get('logged_in', 'False')
    if session['logged_in']==True:
        return render_template("search.html", search=True)
    else:
        return render_template("search.html", search=False)

@app.route("/register", methods=["GET", "POST"])
def register():
    with engine.connect() as db:
        if request.method == "POST":
            name = request.form.get('name')
            user = request.form.get('username')
            pwd = request.form.get('password')
            if name is None or user is None or pwd is None:
                message="Missing field(s)"  
                return render_template("register.html", message=message) 
            if db.execute("SELECT * FROM users WHERE username = %(username)s", {"username": user}).rowcount != 0:
                message="Error: Username already exists."  
                return render_template("register.html", message=message) 
            elif name and user and pwd:
                db.execute("INSERT INTO users (name, username, password) VALUES (%(name)s, %(username)s, %(password)s)", {"name": name, "username": user, "password": pwd })   
                session['logged_in'] = True
                session['username'] = user 
                return render_template("register_success.html")                  
        else:
            return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    with engine.connect() as db:
        if request.method == "POST":
            user = request.form.get('username')
            pwd = request.form.get('password')
            query_user = db.execute("SELECT * FROM users WHERE username = %(username)s AND password = %(password)s", {"username": user, "password": pwd }).fetchone()       
            if query_user[1] == user and query_user[2] == pwd:
                session['logged_in'] = True
                session['username'] = user       
                return redirect(url_for("search"))
            else:
                message="Incorrect username or password"
                return render_template("login.html", message=message)   
            
        else:
            return render_template("login.html")

@app.route("/logout")
def logout():
    session['logged_in']= False
    session['username']=None
    message="You've been logged out"
    return render_template("login.html", message=message, search=False)
        
@app.route("/search", methods=['GET', 'POST'])
def search():
    with engine.connect() as db:
        session['logged_in'] = session.get('logged_in', 'False')
        if session['logged_in'] == True:
            if request.method == "POST":
                query = "%{}%".format(request.form.get('query'))
                results = db.execute("SELECT * FROM books WHERE isbn LIKE %(isbn)s OR UPPER(title) LIKE UPPER(%(title)s) OR UPPER(author) LIKE UPPER(%(author)s) LIMIT 20", {"isbn": query, "title": query, "author": query }).fetchall()
                return render_template("search.html", search=True, results=results, query=query[1:-1])
            else:
                return render_template("search.html", search=True)
        else:
            return render_template("search.html", search=False)

@app.route("/result/<isbn>", methods=["GET", "POST"])
def result(isbn):
    with engine.connect() as db:
        book_result = db.execute("SELECT * FROM books WHERE isbn = %(isbn)s", {"isbn": isbn}).fetchall()
        book_reviews = db.execute("SELECT username, rating, comment FROM review WHERE isbn = %(isbn)s", {"isbn": isbn}).fetchall()
        
        if request.method == "GET":
            if session['logged_in'] == True:
                if db.execute("SELECT * FROM books WHERE isbn = %(isbn)s", {"isbn": isbn}).rowcount != 0:
                    message=isbn
                    if book_reviews == []:
                        reviews = "There are no reviews yet."
                        value=0
                    else:
                        reviews = ""
                        avg=dict(db.execute("SELECT AVG(rating) FROM review WHERE isbn = %(isbn)s", {"isbn": isbn}).fetchone())['avg']
                        value=round(avg,1)
                    return render_template("result.html", search=True, message=message, book_result=book_result, reviews=reviews, book_reviews=book_reviews, value=value)
                else:
                    return render_template('404.html'), 404
            else:
                message = "Unauthorized!"
                return render_template("result.html", search=False, message=message)
    
@app.errorhandler(404)
def page_not_found(e):
   return render_template('404.html'), 404

