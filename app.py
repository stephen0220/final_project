from flask import Flask, g, flash, redirect, request, session, redirect, url_for, render_template, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import sqlite3
import re

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'a;sldkfjghtyrueiwoqp1029384756' 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# PLEASE LEAVE THIS COMMENTED UNTIL I AM FINISHED WITH EDITING THE TABLES!

# Create Tables (Leave as commented once eschedule.db has been created after first run)
conn = sqlite3.connect('eschedule.db')
c = conn.cursor()

'''tables = [ """CREATE TABLE members (
        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        company_name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        hash TEXT NOT NULL
     );""",
     """CREATE TABLE contacts (
        contacts_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        work_type TEXT NOT NULL,
        member_id INTEGER,
        FOREIGN KEY (member_id) REFERENCES members(member_id)
     );""",

     """CREATE TABLE schedule (
         month INTEGER NOT NULL,
         day INTEGER NOT NULL,
         year INTEGER NOT NULL,
         hour INTEGER CHECK (hour >= 1 AND hour < 24),
         minute INTEGER CHECK (minute >= 1 AND minute < 60),
         contacts_id INTEGER,
         FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
     );""",

     """CREATE TABLE proposals (
         price INTEGER,
         description TEXT,
         contacts_id INTEGER,
         draft TEXT CHECK (draft IN ('draft','sent')),
         FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
     );"""

 ]

for table in tables:
     c.execute(table)

conn.commit()
conn.close'''

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('eschedule.db')
        db.row_factory = sqlite3.Row  # This line sets the row_factory for better row access
    return db

# Function to close the database connection
@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Ensure no stored caches
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def home():
             # Initialize the cursor outside the try block
        c = None

        try:
            db = get_db()
            c = db.cursor()

            clients = c.execute("SELECT * FROM contacts WHERE member_id = ?", (session['user_id'],)).fetchall()

            return render_template("home.html", clients = clients)
        
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()


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
@login_required
def clients():
     return render_template('clients.html')

@app.route('/new_client', methods=["GET", "POST"])
@login_required
def new_client():
    print("hello")
    print(session["user_id"])
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone_number = request.form.get("phone_number")
        address = request.form.get("address")
        work_type = request.form.get("work_type")
        email = request.form.get("email")
        member_id = session["user_id"]
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not first_name or not last_name:
            return apology("must provide first and last name", 400)
        
        elif not phone_number or len(phone_number) != 10 or not phone_number.isdigit():
            return apology("must provide a valid phone number", 403)
        
        elif not email or not re.match(email_pattern,email):
            return apology("must provide a valid email", 403)
        
        elif not address or not work_type:
            return apology("must provide address and work type", 403)
        
        elif not member_id:
            return apology ("must login before adding contacts")
        
         # Initialize the cursor outside the try block
        c = None

        try:
            db = get_db()
            c = db.cursor()

            c.execute(
                "INSERT INTO contacts (first_name, last_name, phone_number, email, address, work_type, member_id) VALUES(?,?,?,?,?,?,?)",
                (first_name, last_name, phone_number, email, address, work_type, member_id))            
            db.commit()

            return redirect("/")
        
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()

    else:
     return render_template('new_client.html')
    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Initialize the cursor outside the try block
        c = None
        db = None
        try:
            db = get_db()
            c = db.cursor()
            # Query database for username
            rows = c.execute(
                "SELECT * FROM members WHERE username = ?", (username,)
            ).fetchall()

            # Check if the username exists and the password is correct
            if len(rows) == 1 and check_password_hash(rows[0]["hash"], password):
                session["user_id"] = rows[0]["member_id"]
                print("YES!")
                return redirect("/")
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            # Close the cursor and database connection
            if c is not None:
                
                c.close()
            if db is not None:
                db.close()

    # Moved the render_template outside the finally block
    return render_template("login.html")

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """Register user"""
    # Remove any user ID
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure first name was submitted

        phone_number = request.form.get("phone_number")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        company_name = request.form.get("company_name")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not first_name or not last_name or not company_name:
            return apology("must provide first and last name and company name", 400)
        
        elif not phone_number or len(phone_number) != 10 or not phone_number.isdigit():
            return apology("must provide a valid phone number", 403)
        
        elif not email or not re.match(email_pattern,email):
            return apology("must provide a valid email", 403)
        
        elif not username or not password:
            return apology("must provide username and password", 403)
        
        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password and confirmation match
        elif password != request.form.get("confirmation"):
            return apology("passwords must match", 400)

         # Initialize the cursor outside the try block
        c = None

        try:
            db = get_db()
            c = db.cursor()

           # Query database for username
            row = c.execute("SELECT * FROM members WHERE username = ?", (username,)).fetchone()

            # Ensure username exists
            if row is not None:
                return apology("Username already exists", 400)

            # Insert user into database
            c.execute(
                "INSERT INTO members (first_name, last_name, company_name, phone_number, email, username, password, hash) VALUES(?,?,?,?,?,?,?,?)",
                (first_name, last_name, company_name, phone_number, email, username, password, generate_password_hash(password)),
            )

            db.commit()

           # Query database for newly inserted user
            rows = c.execute("SELECT * FROM members WHERE username = ?", (username,)).fetchall()

            # Remember which user has logged in
            if rows:
                session["user_id"] = rows[0]["member_id"]

            # Redirect user to home page
            return redirect("/")
        
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()

    else:
        return render_template("create_account.html")
    

if __name__ == '__main__':
    app.run(debug=True)

