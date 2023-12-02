from flask import Flask, g, render_template, flash, redirect, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'a;sldkfjghtyrueiwoqp1029384756' 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('eschedule.db')
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
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            db = get_db()
            c = db.cursor()

            # Query database for username
            rows = c.execute(
                "SELECT * FROM members WHERE username = ?", (username,)
            ).fetchall()

            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                return apology("invalid username and/or password", 403)

            session["user_id"] = rows[0]["id"]
            return redirect("/")

        except Exception as e:
            return f"Error: {str(e)}"

        finally:
            c.close()

    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)

