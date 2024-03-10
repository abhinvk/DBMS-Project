from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

import re
import datetime
import bcrypt
import base64

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
# app.secret_key = '1a2b3c4d5e6d7g8h9i10'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'id21973566_localhost'
app.config['MYSQL_PASSWORD'] = 'Community@123' #Replace ******* with  your database password.
app.config['MYSQL_DB'] = 'id21973566_community'


# Intialize MySQL
mysql = MySQL(app)


# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM resident WHERE Email = %s', (username,))
        account = cursor.fetchone()

        if account:
            # Verify password
            hashed_password_from_db = account['Password']
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db.encode('utf-8')):
                # Passwords match, proceed with login
                session['loggedin'] = True
                session['username'] = username
                return redirect(url_for('home'))
            else:
                # Incorrect password
                flash("Incorrect password!", "danger")
        else:
            # Account doesn't exist
            flash("Account doesn't exist!", "danger")

    return render_template('auth/login.html', title="Login")


# http://localhost:5000/pythonlogin/register 
# This will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        contact = request.form['contact']
        location = request.form['location']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM resident WHERE Email LIKE %s", [email] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO resident VALUES (NULL, %s, %s, %s,%s,%s)', (username,contact,email, hashed_password,location))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('auth/register.html',title="Register")

# http://localhost:5000/pythinlogin/home 
# This will be the home page, only accessible for loggedin users

@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT Name FROM Resident WHERE Email = %s", (session['username'],))
        username_row = cursor.fetchone()
        cursor.close()

        if username_row:
            username = username_row['Name']
        else:
            username = "Unknown"  # Or handle this case based on your application logic
        
        return render_template('home/home.html', username=username, title="Home")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))    

@app.route('/events',methods=['GET', 'POST'])
def events():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Event")
    events_data = cursor.fetchall()

    cursor.execute("SELECT * FROM Resident")
    resident_data = cursor.fetchall()

    cursor.close()
    if not events_data:
        message = "No upcoming events."
    else:
        message = ""
    # return render_template('events.html', username=session['username'], title="Home", events_data=events_data, message=message)

    current_date = datetime.datetime.now().date()
    
    upcoming_events = [event for event in events_data if event['Date1'] > current_date]

    if not upcoming_events:
        message = "No upcoming events."
    else:
        message = ""
        for event in upcoming_events:
            for resident in resident_data:
                if resident['ResidentID'] == event['ResidentID']:
                    event['OrganiserName'] = resident['Name']
                    event['ContactInfo'] = resident['ContactInfo']

    return render_template('events.html', username=session['username'], title="Home", events_data=upcoming_events, message=message)


@app.route('/eventorg', methods=['GET', 'POST'])
def eventorg():
    if request.method=='POST' and 'title' in request.form and 'date' in request.form and 'location' in request.form and 'description' in request.form :
        title = request.form['title']
        date =request.form['date']
        location =request.form['location']
        description = request.form['description']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT ResidentID FROM Resident WHERE Email = %s", (session['username'],))
        user = cursor.fetchone()
        user_id = user['ResidentID']
        cursor.execute('INSERT INTO Event (Title, Date1, Location, Details,ResidentID) VALUES (%s, %s, %s, %s,%s)', (title, date, location, description,user_id))
        mysql.connection.commit()
        flash("Event successfully registered!", "success")
        return redirect(url_for('events'))
    elif request.method == 'POST':
        flash("Please fill out the form!","danger")
    return render_template('eventsorg.html',username=session['username'],title="Eventsorg")

@app.route('/eventdelete',methods=['GET','POST'])
def delete_event():
    event_id = request.form['event_id']

    # Perform the deletion of the event with the given EventID
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM Event WHERE EventID = %s", (event_id,))
    mysql.connection.commit()
    cursor.close()

    # Optionally, you can redirect the user to another page after deletion
    return redirect('/events')


@app.route('/maintenance',methods=['GET','POST'])
def maintenance():
    if 'username' not in session:
        flash("Please log in to view maintenance requests!", "danger")
        return redirect(url_for('login'))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM MaintenanceRequest ORDER BY Date DESC")

    all_requests = cursor.fetchall()
    if not all_requests:
        message = "No upcoming events."
    else:
        message = ""
        cursor.execute("SELECT ResidentID,Name FROM Resident WHERE Email = %s", (session['username'],))
        user = cursor.fetchone()
        user_id = user['ResidentID']
        cursor.execute("SELECT * FROM MaintenanceRequest WHERE ResidentID = %s", (user_id,))
        user_request =  cursor.fetchall()

    return render_template('maintenance.html', username=session['username'], requests=all_requests, title="Maintenance",user_id=user_id,user_request=user_request,message=message)

@app.route('/filter_requests', methods=['POST'])
def filter_requests():
    if request.method == 'POST':
        from_date = request.form['from_date']
        to_date = request.form['to_date']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM MaintenanceRequest WHERE Date BETWEEN %s AND %s", (from_date, to_date))
        filtered_requests = cursor.fetchall()

        # Retrieve user-specific requests
        cursor.execute("SELECT ResidentID, Name FROM Resident WHERE Email = %s", (session['username'],))
        user = cursor.fetchone()
        user_id = user['ResidentID']
        user_name = user['Name']
        cursor.execute("SELECT * FROM MaintenanceRequest WHERE ResidentID = %s", (user_id,))
        user_request = cursor.fetchall()

        return render_template('maintenance.html', username=session['username'], requests=filtered_requests, title="Maintenance", user_id=user_id, user_name=user_name, user_request=user_request)

@app.route('/requests',methods=['GET','POST'])
def requests():
    if request.method=='POST' and 'details' in request.form and 'date' in request.form and 'location' in request.form :
        details = request.form['details']
        date =request.form['date']
        location =request.form['location']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("SELECT ResidentID FROM Resident WHERE Email = %s", (session['username'],))
        user = cursor.fetchone()
        user_id = user['ResidentID']
        status = "Request processing"
        cursor.execute('INSERT INTO MaintenanceRequest (ResidentID, Description, Date, Location,Status) VALUES (%s, %s, %s, %s,%s)', (user_id, details,date , location,status))
        mysql.connection.commit()
        flash("Request Submitted!", "success")
        return redirect(url_for('maintenance'))
    elif request.method == 'POST':
        flash("Please fill out the form!","danger")
    return render_template('maintenance.html',username=session['username'],title="Maintenance")
    
@app.route('/requeststatus', methods=['GET', 'POST'])
def requeststatus():
    if request.method == 'POST':
        requests_id=request.form['request_id']
        new_status = request.form['status']  # Set the new status

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE MaintenanceRequest SET Status = %s WHERE RequestID = %s", (new_status, requests_id,))
        mysql.connection.commit()

        flash("Status updated successfully!", "success")
        return redirect(url_for('maintenance'))
    else:
        flash("Invalid request method!", "danger")
        return redirect(url_for('maintenance'))


@app.route('/lostandfound', methods=['GET', 'POST'])
def lost_and_found():
    if request.method == 'POST':
        # Fetch data from the form
        item_name = request.form['item_name']
        location = request.form['location']
        description = request.form['description']
        image_data = request.files['image'].read()

        # Insert data into the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT ResidentID FROM Resident WHERE Email = %s", (session['username'],))
        user = cursor.fetchone()
        user_id = user['ResidentID']
        sql = "INSERT INTO lost_items (user_id, item_name, image_data, location, description) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (user_id, item_name, image_data, location, description))
        mysql.connection.commit()
        flash("Submitted!", "success")
    return render_template('lostandfound.html')

@app.route('/found')
def found():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM lost_items")
    lost_items = cursor.fetchall()
    cursor.close()

    for item in lost_items:
        # Encode the image data to base64
        item['image_data'] = base64.b64encode(item['image_data']).decode('utf-8')

    return render_template('found.html', lost_items=lost_items)

# @app.route('/found', methods=['GET', 'POST'])
# def found(item_id):
#     if request.method == 'POST':
#         if 'user_id' in session:
#             found_by = session['user_id']
#             # Mark the item as found in the database
#             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             cursor.execute("UPDATE lost_items SET is_found = TRUE, found_by = %s WHERE id = %s", (found_by, item_id))
#             mysql.connection.commit()
#             return redirect(url_for('lost_and_found'))
#         else:
#             return redirect(url_for('login'))
#     else:
#         # Fetch the found item from the database
#         cursor.execute("SELECT * FROM lost_items WHERE id = %s", (item_id,))
#         item = cursor.fetchone()
#         return render_template('found.html', item=item)
    
@app.route('/transport')
def index2():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect the user to the login page if they are not logged in
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM notifications WHERE user_id != (SELECT ResidentID FROM Resident WHERE Email = %s)", (session['username'],))
    notifications = cursor.fetchall()
    cursor.close()
    return render_template('transport1.html', notifications=notifications, title="Transport")



@app.route('/save_seat1', methods=['Get','POST'])
def save_seat():
    name = request.form['name']
    age = int(request.form['age']) 
    stop = request.form['stop'] if 'stop' in request.form else None
    notification_id = request.form['notification_id']

    # Decrease the count of available seats for the transportation notification
    cursor = mysql.connection.cursor()


    cursor.execute("UPDATE notifications SET seats_available = seats_available - 1 WHERE id = %s", (notification_id,))
    mysql.connection.commit()

    cursor.execute('INSERT INTO seat_details(notification_id,name,age,stop) VALUES(%s,%s,%s,%s)',(notification_id,name,age,stop))
    mysql.connection.commit()
    # Check if all seats are taken
    cursor.execute("SELECT seats_available FROM notifications WHERE id = %s", (notification_id,))
    result = cursor.fetchone()
    # if result is not None:  # Check if a result is returned
    #     seats_available = result[0]  # Extract the seats_available value
    #     if seats_available < 0:
    #         # Remove the transportation details if all seats are taken
    #         cursor.execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
    #         mysql.connection.commit()

    cursor.close()

    return render_template('notification.html', notifications=notification_id, title="Transport") # Redirect to the transportation page



@app.route('/transportation', methods=['POST'])
def transportation2():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect the user to the login page if they are not logged in

    destination = request.form['destination']
    departure_time = request.form['departure_time']
    seats_available = request.form['seats_available']

    cur = mysql.connection.cursor()
    cur.execute("SELECT ResidentID FROM Resident WHERE Email = %s", (session['username'],))
    user = cur.fetchone()
    user_id = user[0]  # Access the first element of the tuple using index

    cur.execute('INSERT INTO notifications (destination, departure_time, seats_available, user_id) VALUES (%s, %s, %s, %s)',(destination, departure_time, seats_available, user_id))
    mysql.connection.commit()
    cur.close()

    return render_template('transport1.html', title="Transport")  # Redirect to the transportation page or any other valid response


@app.route('/notification')
def notification():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect the user to the login page if they are not logged in

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Fetching the notification associated with the logged-in user
        cur.execute("SELECT * FROM notifications WHERE user_id = (SELECT ResidentID FROM Resident WHERE Email = %s)", (session['username'],))
        notification = cur.fetchone()
        print("Notification:", notification)  # Print the fetched notification

        seat_details = None
        has_notification = False

        if notification:
            notification_id = notification['id']
            # Fetching seat details associated with the fetched notification
            cur.execute("SELECT * FROM seat_details WHERE notification_id = %s", (notification_id,))
            seat_details = cur.fetchall()
            print("Seat Details:", seat_details)  # Print the fetched seat details
            has_notification = True

        cur.close()

        return render_template('notification.html', username=session['username'], title="Notification", has_notification=has_notification, seat_details=seat_details, notification=notification)
    except Exception as e:
        print("An error occurred:", e)  # Print any exception that occurs
        return render_template('error.html', error="An error occurred while fetching notification.")

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('auth/profile.html', username=session['username'],title="Profile")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))  

if __name__ =='__main__':
	app.run(debug=True)
