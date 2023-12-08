Welcome to our EScheduler!
This is a web app to help contractors keep track of their clients and contacts with scheduling
and keeping track of how much money had been made with 'Jobs Accepted'

We installed several packages to make this work. Please run 'pip list' to make sure
you have the following installed, and if not, here is a list to install:
blinker            1.7.0
cachelib           0.10.2
certifi            2023.11.17
charset-normalizer 3.3.2
click              8.1.7
colorama           0.4.6
Flask              3.0.0
Flask-Session      0.5.0
idna               3.6
itsdangerous       2.1.2
Jinja2             3.1.2
MarkupSafe         2.1.3
pip                23.3.1
python-dotenv      1.0.0
requests           2.31.0
setuptools         68.2.2
urllib3            2.1.0
Werkzeug           3.0.1
wheel              0.41.3

navigate to the folder containing the app.py,
then run in the terminal: Flask run

We have code in app.py between lines **-** that create a database incase there isn't one already created

===== New Client =====
After the home page is loaded ('index') you will see a form to add a new client. This page is accesible
to any person loading the page, whether they are logged in or not. Fill out the form with your data,
and then select a contractor to submit your information to via the drop down option form at the bottom
of the form. This will submit the client's information into the database and connect it to that specific
contractor's account.

===== Contractor Account =====

To create a new contractor account, go to the 'Log In' at the top right of the navigation bar above. Once
there, click the button on the bottom left that says: "Register"
Fill out the information including company name, username, and password. Once created, you will be 
automatically navigated to the page that displays your clients (once you get some!)
Feel free at this time to create some new clients, making sure to select your company on the new client
form.

===== Client Management =====

Once you have a new client, you will see two buttons: Set Schedule and Delete Client. Delete client
will remove it from the database and your account. Use the Set Schedule Button to 