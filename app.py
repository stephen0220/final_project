# This Eschedule webapp has been a collaboration between Elicia Reynolds and Stephen Reynolds

from flask import Flask, g, flash, redirect, request, session, redirect, url_for, render_template, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, time_passed
import sqlite3
import re
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'a;sldkfjghtyrueiwoqp1029384756' 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create tables to use in eschedule.db This will only execute if eschedule.db does not exist or has no data/tables

conn = sqlite3.connect('eschedule.db')
c = conn.cursor()

tables = [
    """CREATE TABLE IF NOT EXISTS members (
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

    """CREATE TABLE IF NOT EXISTS contacts (
        contacts_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        work_type TEXT NOT NULL,
        price INTEGER,
        status TEXT CHECK (status IN ('draft', 'sent', 'won', 'lost')),
        member_id INTEGER,
        FOREIGN KEY (member_id) REFERENCES members(member_id)
    );""",

    """CREATE TABLE IF NOT EXISTS schedule (
        month INTEGER NOT NULL,
        day INTEGER NOT NULL,
        year INTEGER NOT NULL,
        hour INTEGER CHECK (hour >= 1 AND hour < 24),
        minute INTEGER CHECK (minute >= 1 AND minute < 60),
        contacts_id INTEGER,
        FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
    );""",
]

# Iteration through the tables in create and implement them into the database
for table in tables:
    c.execute(table)

# Commit the changes and close the connection
conn.commit()
conn.close()

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

# Opening page for users who are non-members and don't have an account
@app.route('/', methods=["GET", "POST"])
def index():
    # Forget any user_id
    session.clear()
    c = None
    options = None  # Define options outside the try block

    # Initialize sqlite cursor
    try:
        db = get_db()
        c = db.cursor()

        options = c.execute("SELECT company_name FROM members").fetchall()

        # Client-side submission form
        if request.method == "POST":
            
            # New client information submission variables
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            phone_number = request.form.get("phone_number")
            address = request.form.get("address")
            work_type = request.form.get("work_type")
            email = request.form.get("email")
            company = request.form.get("company")

            # Email pattern using regular expressions
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

            # Checking for valid user input
            if not first_name or not last_name:
                return apology("must provide first and last name", 400)

            elif not phone_number or len(phone_number) != 10 or not phone_number.isdigit():
                return apology("must provide a valid phone number", 403)

            elif not email or not re.match(email_pattern, email):
                return apology("must provide a valid email", 403)

            elif not address or not work_type:
                return apology("must provide address and work type", 403)

            elif not company:
                return apology("must select a company")
            
            # Fetch the company_id from members who have an account so that new client will be added to that members contacts table
            company_id_row = c.execute(
                "SELECT member_id FROM members WHERE company_name = ?", (company,)
            ).fetchone()

            # Check if the company exists
            if company_id_row is not None:
                company_id = company_id_row[0]  # Extract the value from the row
                # insertion code for new client
                c.execute(
                    "INSERT INTO contacts (first_name, last_name, phone_number, email, address, work_type, member_id) VALUES(?,?,?,?,?,?,?)",
                    (first_name, last_name, phone_number, email, address, work_type, company_id)
                )
                db.commit()
                
                return render_template("index.html", options=options)

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        if c:
            c.close()

    return render_template("index.html", options=options)

# Home page for logged in members
@app.route('/home')
@login_required
def home():
    c = None
    try:
        db = get_db()
        c = db.cursor()

        # Create a list of clients from the members database with values joined from the contacts and schedule tables
        clients = c.execute("""
            SELECT
                contacts.contacts_id,
                contacts.first_name,
                contacts.last_name,
                contacts.address,
                contacts.work_type,
                contacts.price,
                contacts.status,
                schedule.month,
                schedule.day,
                schedule.year,
                schedule.hour,
                schedule.minute
            FROM
                contacts
            LEFT JOIN  -- Use LEFT JOIN to include contacts without a schedule
                schedule ON contacts.contacts_id = schedule.contacts_id
            WHERE
                contacts.member_id = ?""", (session['user_id'],)).fetchall()
        
        # Initialize variables to categorize the clients' statuses
        new = []
        scheduled = []
        draft = []
        sent = []
        won = []
        lost = []
        # Total amount made from scheduled client who accepted the estimate price
        total = 0

         

        # Iterate through clients
        for client in clients:
            new.append(client)
            # Initialize variables for schedule dates
            year = None
            month = None
            day = None
            hour = None
            minute = None
            price = 0
            # Check client to see if it has been scheduled
            if client['month'] is not None:
                scheduled.append(client)
                if client in new:
                    new.remove(client)
                # Gather data from schedule table from client
                year = int(client['year'])
                month = int(client['month'])
                day = int(client['day'])
                hour = int(client['hour'])
                minute = int(client['minute'])
            # Check status of client to see if client estimate datetime has already passed or if the status is set to 'draft'
            if client["status"] == 'draft' or (client["status"] is None and None not in (year, month, day, hour, minute) and time_passed(year, month, day, hour, minute) == True): 
                draft.append(client)
                if client in scheduled:
                    scheduled.remove(client)
            # Check status of client to see if status is set to 'sent'
            if client["status"] == 'sent':
                sent.append(client)
                if client in scheduled:
                    scheduled.remove(client)
                if client in draft:
                    draft.remove(client)
            # Check status of client to see if status is set to 'won' meaning the client accepted the job estimate
            if client["status"] == 'won':
                won.append(client)
                if client in sent:
                    sent.remove(client)
                if client in scheduled:
                    scheduled.remove(client)
            # Check status of client to see if status is set to 'lost', meaning the client rejected the offer
            if client["status"] == 'lost':
                lost.append(client)
                if client in sent:
                    sent.remove(client)
            # If client is won, check to see if price quote is added to the value 'price' in the contacts table
            if client["price"] is not None and client["price"] != 0:
                price = int(client["price"])
                total += price

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()
    return render_template("home.html", new = new, clients=clients, scheduled = scheduled, draft = draft, sent = sent, won = won, lost = lost, total = total)

# Function to use the radio buttons after the client is scheduled and after the estimate has been sent
@app.route('/update_status', methods=['POST'])
def update_status():
    try:
        db = get_db()
        c = db.cursor()
        # Id of the client based off of a hidden input for the radio button form
        selected_id = int(request.form.get('client_id'))
        # Fetch the value from which radio button has been selected, depending on the radio buttons in which form,
        # the values are either 'draft', 'sent', 'won' or 'lost'
        selected_status = request.form.get('status')

        # Update the 'status' in the 'contacts' table
        c.execute("UPDATE contacts SET status = ? WHERE contacts_id = ?", (selected_status, selected_id))
        db.commit()
    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()

    return redirect('/home')
# Input text field to submit price to the job
@app.route('/add_price', methods=['POST'])
def add_price():
    try:
        db = get_db()
        c = db.cursor()
        # Id of the client based off of a hidden input for the radio button form
        selected_id = int(request.form.get('client_id'))
        # Member input for job price
        price = int(request.form.get('price'))

        # Update the 'status' in the 'contacts' table
        c.execute("UPDATE contacts SET price = ? WHERE contacts_id = ?", (price, selected_id))
        db.commit()
    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()

    return redirect('/home')



# Delete client button available in certain divs on the home page
@app.route('/delete_client', methods=['POST'])
def delete_client():
    try:
        db = get_db()
        c = db.cursor()
        # Id of the client based off of a hidden input
        removing = request.form.get('contact_id')
        
        # Delete client that matches the contacts_id in contacts
        c.execute(
            "DELETE FROM contacts WHERE contacts_id = ?", (removing,)
        )

        db.commit()
        

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()

    
    return redirect("/home")

# Page to add client to the estimate schedule
@app.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():

    c = None
    try:
        db = get_db()
        c = db.cursor()
        # Options for select form to select which client to add to schedule
        options = c.execute(
            """SELECT first_name || ' ' || last_name AS full_name FROM contacts
                WHERE member_id = ?""", (session['user_id'],)).fetchall()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":        
            # Extract form values
            month_str = request.form.get("month")
            day_str = request.form.get("day")
            year_str = request.form.get("year")
            hour_str = request.form.get("hour")
            minute_str = request.form.get("minute")
            contact_name = request.form.get("contact_name")



            # Convert form values to integers
            month = int(month_str)
            day = int(day_str)
            year = int(year_str)
            hour = int(hour_str)
            minute = int(minute_str)
            max_days = (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
            contact_name = request.form.get("contact_name")
        
            # Check validation for input
            # Check to see if datetime is in the future
            if time_passed(year, month, day, hour, minute) == True:
                return apology("Time has already passed", 403)
            # Check to see if the day is within the month length
            elif day < 1 or day > max_days:
                return apology("must provide a valid day", 403)
            # Check to see if hour and minute are valid in Military Time  
            elif hour < 1 or hour > 24 or minute < 0 or minute > 59:
                return apology("must provide a valid time", 403)
            # Check to see if client name has been selected
            elif not contact_name:
                return apology ("Please select a client to schedule")


            # Fetch the contact_id
            contact_name_row = c.execute(
                "SELECT contacts_id FROM contacts WHERE first_name || ' ' || last_name = ? AND member_id = ?",
                (contact_name, session['user_id'])
            ).fetchone()


            # Check if the contact exists
            if contact_name_row is not None:
                contact_id = contact_name_row[0]  # Extract the value from the row
            else:
                return apology("no client found")
            
            # Query for database to find if client has already been scheduled
            existing_client = c.execute(
                "SELECT * FROM schedule WHERE contacts_id = ?",
                (contact_id,)
            ).fetchone()

            # Check to see if client already exists
            if existing_client:
                return apology("client has already been scheduled", 400)
            
            # Query database for same scheduled estimate
            existing_booking = c.execute(
            """SELECT * FROM schedule
            JOIN contacts ON schedule.contacts_id = contacts.contacts_id
            JOIN members ON contacts.member_id = members.member_id
            WHERE schedule.month = ? AND schedule.day = ? AND schedule.year = ? AND schedule.hour = ?
            AND schedule.minute = ? AND members.member_id = ?""",
            (month, day, year, hour, minute, session['user_id'])
            ).fetchone()

            # Check to see if schedule is open
            if existing_booking:
                return apology("No availability! Please select a different time", 400)

            # Insert booked client into schedule table
            c.execute(
                "INSERT INTO schedule (month, day, year, hour, minute, contacts_id) VALUES(?,?,?,?,?,?)",
                (month, day, year, hour, minute, contact_id))
            db.commit()

            return redirect("/home")
        else:
            return render_template('schedule.html', options = options)

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()

# Page to add a new client member-side
@app.route('/new_client', methods = ["GET", "POST"])
@login_required
def new_client():

     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Initialize variable for user input        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone_number = request.form.get("phone_number")
        address = request.form.get("address")
        work_type = request.form.get("work_type")
        email = request.form.get("email")
        member_id = session["user_id"]
        # Regular expression for email form
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        # Check for any invalid inputs from user
        # Check for first and last names
        if not first_name or not last_name:
            return apology("must provide first and last name", 400)
        # Check for phone number and the correct length
        elif not phone_number or len(phone_number) != 10 or not phone_number.isdigit():
            return apology("must provide a valid phone number", 403)
        # Check for email and correct format
        elif not email or not re.match(email_pattern,email):
            return apology("must provide a valid email", 403)
        # Check for address and job description
        elif not address or not work_type:
            return apology("must provide address and work type", 403)
        # Just in case someone hacked in and made it this far without logging in or having an account
        elif not member_id:
            return apology ("must login before adding contacts")
        
        # Initialize the cursor outside the try block
        c = None

        try:
            db = get_db()
            c = db.cursor()

            # Query contacts table for client
            existing_client = c.execute(
                "SELECT * FROM contacts WHERE first_name = ? AND last_name = ? AND member_id = ?",
                (first_name, last_name, session['user_id'])
            ).fetchone()

            # Check to see if client already exists
            if existing_client:
                return apology("client has already been added", 400)
            # Insert new client into contacts table
            c.execute(
                "INSERT INTO contacts (first_name, last_name, phone_number, email, address, work_type, member_id) VALUES(?,?,?,?,?,?,?)",
                (first_name, last_name, phone_number, email, address, work_type, member_id))            
            db.commit()

            return redirect("/home")
        
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()

    else:
     return render_template('new_client.html')
# Logout user 
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
# Login user
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Initialize variable from user input
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
                return redirect("/home")
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

# Create new member account
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    # Remove any user ID
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Initailize variable for user input

        phone_number = request.form.get("phone_number")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        company_name = request.form.get("company_name")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        # Regular expression for email format
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        # Check for valid user input
        # Check for first and last names
        if not first_name or not last_name or not company_name:
            return apology("must provide first and last name and company name", 400)
        # Check for phone number and correct length
        elif not phone_number or len(phone_number) != 10 or not phone_number.isdigit():
            return apology("must provide a valid phone number", 403)
        # Check for email and correct format
        elif not email or not re.match(email_pattern,email):
            return apology("must provide a valid email", 403)
        # Check for username and password
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

            # Ensure no duplicate username exists
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
            return redirect("/home")
        
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()

    else:
        return render_template("create_account.html")

 # Change password    
@app.route("/password", methods=["GET", "POST"])
@login_required
def password():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Initialize the cursor outside the try block
        c = None

        try:
            db = get_db()
            c = db.cursor()
            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)
        


            # Query database for username
            c.execute(
                "SELECT * FROM members WHERE username = ?",
                (request.form.get("username"),)
            )

            # Fetch the result (one row)
            row = c.fetchone()
            # Ensure username exists
            if row is None:
                return apology("Must provide a valid username", 400)

            # Ensure password was submitted
            elif not request.form.get("password"):
                return apology("must provide password", 400)

            # Ensure new password was submitted
            elif not request.form.get("new_password") or request.form.get(
                "new_password"
            ) == request.form.get("password"):
                return apology("must provide new password", 400)

            # Ensure confirmation for new password was submitted
            elif not request.form.get("confirmation"):
                return apology("must confirm password", 400)

            # Ensure password and confirmation match
            elif request.form.get("new_password") != request.form.get("confirmation"):
                return apology("passwords must match", 400)
            # Insert username with new password into database
            c.execute(
                "UPDATE members SET hash = ? WHERE username = ?",
                (generate_password_hash(request.form.get("new_password")), 
                request.form.get("username")
                ),
            )

            db.commit()

            # Query database for username
            c.execute(
                "SELECT * FROM members WHERE username = ?",
                (request.form.get("username"),)
            )

            # Fetch the result (one row)
            row = c.fetchone()

            # Ensure username exists and password
            if row is None:
                return apology("Must provide valid username", 400)

            # Remember which user has logged in
            session["user_id"] = row["member_id"]

            # Redirect user to home page
            return redirect("/home")
            # User reached route via GET (as by clicking a link or via redirect)
            
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()
    else:
        return render_template("password.html")

# Delete member account button  
@app.route('/delete_member', methods=['POST'])
def delete_member():
    try:
        db = get_db()
        c = db.cursor()
        # Value from hidden form
        removing = session['user_id']
        # Delete member's schedule
        c.execute(
            """DELETE FROM schedule
            WHERE contacts_id IN (SELECT contacts_id FROM contacts WHERE member_id = ?)""",
            (removing,)
        )
        # Delete members clients
        c.execute(
            """DELETE FROM contacts WHERE member_id = ?""", (removing,)
        )
        # Delete member
        c.execute(
            "DELETE FROM members WHERE member_id = ?", (removing,)
        )

        db.commit()

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()

    print("Account deleted!")
    return redirect("/")



    

if __name__ == '__main__':
    app.run(debug=True)

