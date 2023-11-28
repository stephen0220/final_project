import os

from flask import Flask, render_template #flash, redirect, request, session
#from flask_session import Session
#from werkzeug.security import check_password_hash, generate_password_hash
#from helpers import apology

app = Flask(__name__)

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
