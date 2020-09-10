from flask import Flask, render_template, request, redirect,session
from flask_session import Session
import sqlite3
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mydb = SQL("sqlite:///main.db")


# print("books", len(books_rows))

@app.route("/")
@login_required
def index():
    rows = mydb.execute("SELECT name FROM users WHERE id=:id;", id = session["user_id"])
    name = rows[0]["name"]
    books_rows = mydb.execute("SELECT * FROM books;")
    return render_template("index.html", rows = books_rows, name = name)

@app.route("/register", methods=['GET', 'POST'])
def register():

    session.clear()

    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        password_hash = generate_password_hash(request.form.get('password'))
        # confirm_password_hash = generate_password_hash(request.form.get('confirm_password'))

        if request.form.get('password') != request.form.get('confirm_password'):
            return render_template("apology.html", msg="Password not matched!", back="/register")

        rows = mydb.execute("SELECT * FROM users WHERE email=:email;", email=email)
        
        if len(rows) != 0:
            return render_template("apology.html", msg="Email address already registered!", back="/register")

        # with sqlite3.connect("main.db") as mydb:
        mydb.execute("INSERT INTO users (name, email, password_hash) VALUES(?, ?, ?);", (name, email, password_hash)) 
        # mydb.commit()
        return redirect("/")

@app.route("/login", methods = ["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        rows = mydb.execute("SELECT * FROM users WHERE email=:email", email = email)
        if len(rows) == 0:
            return render_template("apology.html", msg="You are not registered!", back="/login")
        
        print(check_password_hash(rows[0]["password_hash"], password))

        if check_password_hash(rows[0]["password_hash"], password) == False:
            return render_template("apology.html", msg="Incorrect password! Try again.", back="/login")

        session["user_id"] = rows[0]["id"]
        
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/book", methods=['POST'])
@login_required
def book():

    if request.method == "POST":
        book_id = request.form.get('bookid')

        table = mydb.execute("SELECT * FROM books WHERE id=:book_id;", book_id = book_id)

        return render_template("book.html", title = table[0]['title'], author = table[0]['author'], img = table[0]['img'], download = table[0]['download'])

@app.route("/logout")
def logout():
    
    session.clear()

    return redirect("/")

@app.route("/category", methods=["post"])
def category():

    category = request.form.get("category")
    rows = mydb.execute("SELECT * FROM books WHERE language=:category;", category = category)
    return render_template("category.html",category = category, rows = rows)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/search", methods=["post"])
def search():
    query = request.form.get('search_query')

    search_query_sql = "SELECT * FROM books WHERE LOWER(title) LIKE :query OR LOWER(author) LIKE :query;"

    rows = mydb.execute(search_query_sql, query='%' + query.lower() + '%')
    if len(rows) == 0:
        return render_template("apology.html", msg="No books found!", back="/")

    return render_template("category.html", category="Found", rows=rows)


