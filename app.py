from flask import Flask, g, flash, redirect, request, session, redirect, url_for, render_template, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import sqlite3
import re
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'a;sldkfjghtyrueiwoqp1029384756' 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# PLEASE LEAVE THIS COMMENTED UNTIL I AM FINISHED WITH EDITING THE TABLES!

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
        status TEXT CHECK (status IN ('lost','won')),
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

@app.route('/', methods=["GET", "POST"])
def index():
    c = None
    options = None  # Define options outside the try block

    try:
        db = get_db()
        c = db.cursor()

        # Code for the home page for non-members or those who are not logged in
        options = c.execute("SELECT company_name FROM members").fetchall()

        # Client-side submission form
        if request.method == "POST":
            # Initialize the cursor outside the try block

            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            phone_number = request.form.get("phone_number")
            address = request.form.get("address")
            work_type = request.form.get("work_type")
            email = request.form.get("email")
            company = request.form.get("company")

            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

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
            # Fetch the company_id
            company_id_row = c.execute(
                "SELECT member_id FROM members WHERE company_name = ?", (company,)
            ).fetchone()

            # Check if the company exists
            if company_id_row is not None:
                company_id = company_id_row[0]  # Extract the value from the row
                # Your insertion code here
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


@app.route('/home')
def home():
    c = None
    now = datetime.now()
    timestamp = now.timestamp()
    timestamp_year = datetime.utcfromtimestamp(timestamp).year
    timestamp_month = datetime.utcfromtimestamp(timestamp).month
    timestamp_day= datetime.utcfromtimestamp(timestamp).day
    timestamp_hour= datetime.utcfromtimestamp(timestamp).hour
    timestamp_minute = datetime.utcfromtimestamp(timestamp).minute
    try:
        db = get_db()
        c = db.cursor()

        # Code for the home page after member login
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
        
        new = []
        scheduled = []
        draft = []
        #sent = []
        #won = []


        
        for client in clients:
            new.append(client)
            if client['month'] is not None:
                scheduled.append(client)
                if client in new:
                    new.remove(client)

                year = int(client['year'])
                month = int(client['month'])
                day = int(client['day'])
                hour = int(client['hour'])
                minute = int(client['minute'])

            if (
                timestamp_year > year or
                (timestamp_year == year and timestamp_month > month) or
                (timestamp_year == year and timestamp_month == month and timestamp_day > day) or
                (timestamp_year == year and timestamp_month == month and timestamp_day == day and timestamp_hour > hour) or
                (timestamp_year == year and timestamp_month == month and timestamp_day == day and timestamp_hour == hour and timestamp_minute > minute)
            ):
                draft.append(client)
                if client in scheduled:
                    scheduled.remove(client)
            

        print(len(new))
        print(len(scheduled))
        print(len(draft))
        #print(won)
        #print(lost)


    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()
    return render_template("home.html", new = new, clients=clients, scheduled = scheduled, draft = draft)

@app.route('/delete_client', methods=['POST'])
def delete_client():
    try:
        db = get_db()
        c = db.cursor()

        removing = request.form.get('contact_id')
        print(f"Deleting client with contacts_id: {removing}")

        c.execute(
            "DELETE FROM contacts WHERE contacts_id = ?", (removing,)
        )

        db.commit()
        print("Deletion successful")

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        c.close()

    print("Client deleted!")
    return redirect("/home")


@app.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():

    c = None
    try:
        db = get_db()
        c = db.cursor()

        options = c.execute("SELECT first_name || ' ' || last_name AS full_name FROM contacts").fetchall()

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
            
            print(month)
            print(day)
            print (year)
            print (hour)
            print(minute)
            print(max_days)

            #if not month or not day or not year or not hour or not minute:
            #    return apology("must provide date and time to schedule an appointment", 400)

            #elif month < 1 or month > 12:
            #    return apology("must provide a valid month (1-12)", 403)

            if day < 1 or day > max_days:
                return apology("must provide a valid day", 403)
                
            elif hour < 1 or hour > 24 or minute < 0 or minute > 59:
                return apology("must provide a valid time", 403)

            elif not contact_name:
                return apology ("Please select a client to schedule")


            # Fetch the contact_id
            contact_name_row = c.execute(
                "SELECT contacts_id FROM contacts WHERE first_name || ' ' || last_name = ?", (contact_name,)
            ).fetchone()

            # Check if the contact exists
            if contact_name_row is not None:
                contact_id = contact_name_row[0]  # Extract the value from the row
            else:
                return apology("no client found")
            
            existing_client = c.execute(
                "SELECT * FROM schedule WHERE contacts_id = ?",
                (contact_id,)
            ).fetchone()

            # Check to see if client already exists
            if existing_client:
                return apology("client has already been scheduled", 400)
            
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


 

@app.route('/clients')
@login_required
def clients():
     return render_template('clients.html')

@app.route('/new_client', methods = ["GET", "POST"])
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

            # Query contacts table for client
            existing_client = c.execute(
                "SELECT * FROM contacts WHERE first_name = ? AND last_name = ? AND member_id = ?",
                (first_name, last_name, session['user_id'])
            ).fetchone()

            # Check to see if client already exists
            if existing_client:
                return apology("client has already been added", 400)

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
            return redirect("/home")
        
        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()

    else:
        return render_template("create_account.html")
    
@app.route("/password", methods=["GET", "POST"])
def password():
    """Change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        try:
            db = get_db()
            c = db.cursor()
            # Ensure username was submitted
            if not request.form.get("username"):
                return apology("must provide username", 400)
        


            # Query database for username
            rows = c.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )

            # Ensure username exists and password
            if len(rows) == 0:
                return apology("Must place valid username", 400)

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

            # Query database for username
            # db.execute("DELETE FROM users WHERE username = ?", request.form.get("username"))

            # Insert username new password into database
            db.execute(
                "UPDATE users SET hash = ? WHERE username = ?",
                generate_password_hash(request.form.get("new_password")),
                request.form.get("username"),
            )

            # Query database for newly inserted user
            db.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")

            # User reached route via GET (as by clicking a link or via redirect)
            
        except Exception as e:
                return f"Error: {str(e)}"

        finally:
            c.close()
    else:
        return render_template("password.html")


    

if __name__ == '__main__':
    app.run(debug=True)

