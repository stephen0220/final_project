import os
import sqlite3

from flask import Flask, render_template
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Create database file

conn = sqlite3.connect('eschedule.db')

c = conn.cursor()

""" To ensure no stored caches """
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

@app.route('/new_client')
def new_client():
     return render_template('new_client.html')
