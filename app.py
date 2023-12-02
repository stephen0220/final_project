import os
import sqlite3
import re

from flask import Flask, render_template, flash, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)
app.secret_key = 'a;sldkfjghtyrueiwoqp1029384756' 

# Create database file

conn = sqlite3.connect('eschedule.db')

c = conn.cursor()

# PLEASE LEAVE THIS COMMENTED UNTIL I AM FINISHED WITH EDITING THE TABLES!

# Create Tables (Leave as commented once eschedule.db has been created after first run)

# tables = [ """CREATE TABLE members (
#        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
#        first_name TEXT NOT NULL,
#        last_name TEXT NOT NULL,
#        company_name TEXT NOT NULL,
#        email TEXT NOT NULL,
#        phone_number TEXT NOT NULL,
#        username TEXT NOT NULL,
#        password TEXT NOT NULL,
#        hash TEXT NOT NULL
#     );""",
#     """CREATE TABLE contacts (
#        contacts_id INTEGER PRIMARY KEY,
#        first_name TEXT NOT NULL,
#        last_name TEXT NOT NULL,
#        phone_number TEXT NOT NULL,
#        email TEXT NOT NULL,
#        address TEXT NOT NULL,
#        work_type TEXT NOT NULL,
#        member_id INTEGER,
#        FOREIGN KEY (member_id) REFERENCES members(member_id)
#     );""",

#     """CREATE TABLE schedule (
#         month INTEGER NOT NULL,
#         day INTEGER NOT NULL,
#         year INTEGER NOT NULL,
#         hour INTEGER CHECK (hour >= 1 AND hour < 24),
#         minute INTEGER CHECK (minute >= 1 AND minute < 60),
#         contacts_id INTEGER,
#         FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
#     );""",

#     """CREATE TABLE proposals (
#         price INTEGER,
#         description TEXT,
#         contacts_id INTEGER,
#         draft TEXT CHECK (draft IN ('draft','sent')),
#         FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
#     );"""

# ]

# for table in tables:
#     c.execute(table)



# c.execute(eschedule_tables)
""" To ensure no stored caches """
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#THESE LINES ARE COMMENTED OUT TO PREVENT SYSTEM ERRORS UNTIL WE HAVE A LOGIN PAGE SET
#Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#Session(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/draft')
def draft():
     return render_template('draft.html')

@app.route('/proposals')
def proposals():
     return render_template('proposals.html')

@app.route('/schedule')
def schedule():
     return render_template('schedule.html')

@app.route('/clients')
def clients():
     return render_template('clients.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        

        # Query database for username
        rows = c.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """Register user"""
    # Remove any user ID
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure first name was submitted

        phone_number = request.form.get("phone_number")
        email = request.form.get("email")
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not request.form.get("first_name"):
            return apology("must provide first and last name", 400)
        

        elif not request.form.get("last_name"):
            return apology("must provide first and last name", 403)
        

        elif not request.form.get("company_name"):
            return apology("must provide company name", 403)
        

        elif not phone_number or len(phone_number) != 10 or not phone_number.isdigit():
            return apology("must provide a valid phone number", 403)
        

        elif not email or not re.match(email_pattern,email):
            return apology("must provide a valid email", 403)
        

        elif not request.form.get("username"):
            return apology("must provide username", 403)
       
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Query database for username
        rows = c.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 0:
            return apology("username already exists", 400)

        # Insert username into database
        c.execute(
            "INSERT INTO members (username, hash) VALUES(?,?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        # Query database for newly inserted user
        rows = c.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("create_account.html")
