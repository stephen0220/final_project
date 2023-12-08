Our webapp, ESchedule, is designed for contractors to have a database of clients with their contact information,
estimate schedule date, whether or not an estimate/price quote has been sent, whether or not the client accepted or rejected the quote, and, if accepted, the quoted price.

First we created an outline of the basic format of what this app would do and what features we wanted to have.

We researched the best SQL program to use for implementing the queries I wanted to make for this app.
We used Python's SQLite library for this application using a filesystem instead of a separate server. If this
application grows and grows into a larger database, then using something like MySQL or SQL Alchemy would be
the better program to use.

Next, we planned what tables and values would be used from the database and how best to link them together when 
we needed to query values using foreign keys. Then, we figured that using AUTOINCREMENT for the ids of the members
and the contacts would be ideal to have unique member and contact ids.

AFter that, we formulated the foundational layout to be implemented to the other pages using CSS, Bootstrap, and Jinja. We even used a couple of lines of JavaScript in the head tag of the html files to logout the user if the page is closed.

Then we began writing the Python code to add and implement Flask to create a user session for each logged in member.

The next step was to write all of the Python code for each page and button to alter the database using queries and other implemented functions(see helpers.py for some external functions), starting with the create_account, the new_client, and the schedule pages. Finally, we rendered the home page to categorize each of the clients into divs depending on the client being scheduled and the status of the estimate for that client using buttons, radio buttons, and finally a number field for the price of the quote once the client status for the estimate was "won".

While one of us debugged the Python code, the other one implemented the Bootstrap and CSS code to make the website attractive and created a good GUI for the user.

