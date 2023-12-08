from datetime import datetime
from flask import redirect, render_template, session
from functools import wraps

# Page to display client-side errors. Courtesy of CS50. We love Grumpy Cat! ^__^
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

# Function to make certain pages only accessible to logged in clients
def login_required(f):
    """ Decorate routes to require login. http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Function to be used for checking datetimes for scheduling a client. 
# If the datetime for scheduling a client is prior to current timestamp, it will return true.   
def time_passed(year, month, day, hour, minute):
    now = datetime.now()
    timestamp = now.timestamp()
    timestamp_year = datetime.utcfromtimestamp(timestamp).year
    timestamp_month = datetime.utcfromtimestamp(timestamp).month
    timestamp_day= datetime.utcfromtimestamp(timestamp).day
    timestamp_hour= datetime.utcfromtimestamp(timestamp).hour
    timestamp_minute = datetime.utcfromtimestamp(timestamp).minute
    print(now)

    if (
        timestamp_year > year or
        (timestamp_year == year and timestamp_month > month) or
        (timestamp_year == year and timestamp_month == month and timestamp_day > day) or
        (timestamp_year == year and timestamp_month == month and timestamp_day == day and timestamp_hour > hour) or
        (timestamp_year == year and timestamp_month == month and timestamp_day == day and timestamp_hour == hour and timestamp_minute > minute)
    ):
        print("time has passed")
        return True
    else:
        print("time has not yet passed")

