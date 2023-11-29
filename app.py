import os
import sqlite3

from flask import Flask, render_template #flash, redirect, request, session
#from flask_session import Session
#from werkzeug.security import check_password_hash, generate_password_hash
#from helpers import apology

app = Flask(__name__)

# Create database file

conn = sqlite3.connect('eschedule.db')

c = conn.cursor()

# Create Tables (Leave as commented once eschedule.db has been created after first run)

"""eschedule_tables = (""" CREATE TABLE members (
    member_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE contacts (
    contacts_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email TEXT NOT NULL,
    address TEXT NOT NULL,
    work_type TEXT NOT NULL,
    member_id INTEGER,
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

CREATE TABLE schedule (
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    year INTEGER NOT NULL,
    contacts_id INTEGER,
    FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
);

CREATE TABLE proposals (
    price INTEGER,
    description TEXT,
    contacts_id INTEGER,
    draft TEXT CHECK (draft IN ('draft','sent'))
    FOREIGN KEY (contacts_id) REFERENCES contacts(contacts_id)
);""")"""

db.execute(eschedule_tables)
""" To ensure no stored caches """
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
