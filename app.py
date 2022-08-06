import os

from cs50 import SQL
from flask import Flask, flash, Markup, redirect, render_template, request, send_from_directory, session, abort
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from functools import wraps
import re


# Start application
app = Flask(__name__)

# Auto-reload templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (and not cookies)
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create database to implement SQLite3 queries
db = SQL("sqlite:///ctp.db")


""" Prevent user responses from being cached (stored in fast-access memory)"""
@app.after_request
def add_header(r):
    """ https://thewebdev.info/2022/04/03/how-to-disable-caching-in-python-flask/#:~:text=To%20disable%20caching%20in%20Python%20Flask%2C%20we%20can%20set,response%20headers%20to%20disable%20cache.&text=to%20create%20the%20add_header%20function,after_request%20decorator."""

    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = 0
    r.headers["Cache-Control"] = 'public, max-age=0'
    return r


""" Decorator to require that user be logged in """
def login_required(f):   

    @wraps(f)
    def wrapped_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return wrapped_function


""" Display index(home) page """
@app.route("/")
def index(): 

    # Clear session
    session.clear()

    # Display index
    flash("This is a development server. Do not enter personal credentials anywhere on this site.", "error")
    return render_template("index.html")
    

""" Log user in """
@app.route("/login", methods=["GET", "POST"])
def login():

    # If reached through GET, render html page
    if request.method == "GET":
        return render_template("login.html")
    
    # If reached through POST, clear session and log user in
    session.clear()

    # Check for missing username and/or password
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        flash("Missing username and/or password!", "error")
        return redirect("/login")
    
    # Validate username and/or password using database
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    if len(rows) != 1:
        flash("Invalid username!", "error")
        return redirect("/login") 
    elif not check_password_hash(rows[0]["password"], password):
        flash("Incorrect password!", "error")
        return redirect("/login")

    # Update session variables
    session["user_id"] = rows[0]["id"]
    session["user_section"] = rows[0]["section"]
    session["weeks_visible"] = True

    # Alert user of log in and redirect to dashboard
    welcome_msg = "Welcome, " + str(username) + "!"
    flash(welcome_msg, "success")
    return redirect("/videos")


""" Log user out """
@app.route("/logout")
@login_required
def logout():

    # Clear session
    session.clear()   

    # Alert user of log out and redirect to index
    flash("You have been logged out!", "success")
    return render_template("index.html") 


""" Register new user """
@app.route("/register", methods=["GET", "POST"])
def register():

    # If reached through GET, render register page
    if request.method == "GET":
        return render_template("register.html")

    # If reached by POST, clear session and register user
    session.clear()

    # Check for missing username
    username = request.form.get("username")
    if not username:
        flash("Username required!", "error")
        return redirect("/register")
    
    # Check if username already exists
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    if len(rows) != 0:
        flash("Username already exists!", "error")
        return redirect("/register")

    # Check for missing email
    email = request.form.get("email")
    if not email:
        flash("Email required!", "error")
        return redirect("/register")

    # Check if email provided is valid using REGEX
    # https://devsheet.com/code-snippet/python-code-to-validate-email-address-using-regex/#:~:text=To%20validate%20email%20addresses%20using%20python%2C%20regex%20can,re%20def%20validate_email%28email%29%3A%20email_pattern%20%3D%20r%27b%20%5BA-Za-z0-9._%25%2B-%5D%2B%40%20%5BA-Za-z0-9.-%5D%2B.
    def validate_email(email):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.fullmatch(email_pattern, email)

    if not validate_email(email):
        flash("Invalid email!", "error")
        return redirect("/register")

    # Check if user with provided email already exists
    rows_e = db.execute("SELECT * FROM users WHERE email = ?", email)
    if len(rows_e) != 0:
        flash("User with email already exists!", "error")
        return redirect("/register")

    # Check if password provided is valid
    password = request.form.get("password")
    confirm_pw = request.form.get("confirm_pw")
    if not password or not confirm_pw:
        flash("Invalid password!", "error")
        return redirect("/register")
    if password != confirm_pw:
        flash("Passwords don't match!", "error")
        return redirect("/register")

    # Get section provided by user (default = beginner)
    section = request.form.get("section")

    # Hash password and store in database
    hashed_pass = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    db.execute("INSERT INTO users (username, email, password, section) VALUES(?, ?, ?, ?)", username, email, hashed_pass, section)

    # Alert user of registration then log user in
    rows_temp = db.execute("SELECT * FROM users WHERE username = ?", username)
    session["user_id"] = rows_temp[0]["id"]
    welcome_msg = "Welcome, " + str(username) + "!"
    flash(welcome_msg, "success")
    return redirect("/videos")


""" Change user's password """
@app.route("/change_pw", methods=["GET", "POST"])
@login_required
def change_pw():

    # If reached through GET, render change_pw page
    if request.method == "GET":
        session["weeks_visible"] = False
        return render_template("change_pw.html")

    # Get old password from user, check if missing
    oldpass = request.form.get("oldpass")
    if not oldpass:
        flash("Old password required!", "error")
        return redirect("/change_pw")

    # Check if old password matches hashed password on record
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if not check_password_hash(rows[0]["password"], oldpass):
        flash("Incorrect old password!", "error")
        return redirect("/change_pw")

    # Get new password, check if valid and matches confirmation
    newpass = request.form.get("newpass")
    newpass_confirm = request.form.get("newpass_confirm")
    if not newpass or not newpass_confirm or newpass != newpass_confirm:
        flash("Invalid new password!", "error")
        return redirect("/change_pw")

    # Update user's password in the database
    hashed_newpass = generate_password_hash(newpass, method='pbkdf2:sha256', salt_length=8)
    db.execute("UPDATE users SET password = ? WHERE id= ?", hashed_newpass, session["user_id"])

    # Log user out
    session.clear()

    # Alert user of password change and redirect to login
    flash("Password changed successfully! Log in to continue.", "success")
    return redirect("/login")


""" User managment hub for admin """
@app.route("/usermgmt")
@login_required
def usermgmt():

    # Prevent page from displaying sidebar
    session["weeks_visible"] = False

    # Only allow a logged in admin to access page, else redirect to dashboard
    if "user_id" in session.keys() and session["user_id"] == 1:
        all_rows = db.execute("SELECT * FROM users")
        return render_template("usermgmt.html", rows=all_rows)
    else:
        flash("Invalid request", "error")
        return redirect("/videos")


""" Deregister user from database """
@app.route("/deregister", methods=["GET", "POST"])
@login_required
def deregister():

    # If reached through GET, simply redirect to dashboard
    if request.method == "GET":
        flash("Invalid request!", "error")
        return redirect("/videos")
    
    # Get user id to be deregistered from form
    id = request.form.get("id")

    # Can not deregister admin
    if str(id) == "1":
        flash("Invalid request", "error")
        return redirect("/videos")

    # Delete user from database and update usermgmt table
    db.execute("DELETE FROM users WHERE id = ?", id)
    return redirect("/usermgmt")


""" Display videos to user """
@app.route("/videos", methods=["GET", "POST"])
@login_required
def videos():

    # If reached through GET, set default variables
    if request.method == "GET":
        week = "1"
        subject = "reading"
    # If reached through POST, get video information from form
    else:
        week = str(request.form.get("week"))
        subject = str(request.form.get("subject"))

    # Get url/s of video/s to display
    embed_url = Markup(WEEKS[week][subject]["video_url"])
    extra = WEEKS[week][subject]["extra"]
    if extra:
        extra = Markup(extra)

    # Ensure sidebar is displayed
    session["weeks_visible"] = True

    # Render videos html with information on the video to be displayed
    return render_template("videos.html", embed_url=embed_url, week=int(week), subject=subject, extra=extra)


""" Display assignments to user """
@app.route("/assignments", methods=["GET", "POST"])
@login_required
def assignments():
    """ Display videos to user """

    # If reached through GET, set default variables
    if request.method == "GET":
        week = "1"
        subject = "reading"
    # If reached through POST, get video information from form
    else:
        week = str(request.form.get("week"))
        subject = str(request.form.get("subject"))

    # Get user's section type from database
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    section = rows[0]["section"]

    # Prepare name of document to be linked to
    file_name = "week" + week + subject + "_" + section + ".pdf"

    # Get submission form link
    sub_form = WEEKS[week]["sub_form"]

    # Ensure sidebar is displayed
    session["weeks_visible"] = True

    # Render assignments html with information on the document and submission form to be displayed
    return render_template("assignments.html", file_name=file_name, week=int(week), subject=subject, section=section, sub_form=sub_form)


""" Configure folder access for accessing documents """
app.config["DOCS_FOLDER"] = "/mnt/c/Users/abenezer/Desktop/Programming Files/CS50/Final Project/static/docs"


""" Retrieve and open documents """
@app.route("/get-pdf/<filename>")
@login_required
def get_pdf(filename):

    try:
        return send_from_directory(app.config["DOCS_FOLDER"], filename, as_attachment=False)
    except FileNotFoundError:
        abort(404)    


""" Dictionary to store information on videos and submission forms """
WEEKS = {
    "0": {
        "orientation": {"video_url": '<iframe width="618" height="279" src="https://www.youtube.com/embed/1AjrdmVC3TA" title="CTP 2022 Beginner and Intermediate Orientation" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},
        "other": {"video_url": 'url', "extra": 'url'},
        "sub_form": "url"
    },
    "1": {
        "reading" : {"video_url": '<iframe width="654" height="409" src="https://www.youtube.com/embed/NpNdC8Ysbew" title="SAT READING | Week 1 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},
        "writing" : {"video_url": '<iframe width="654" height="409" src="https://www.youtube.com/embed/DfSicO_uRug" title="SAT WRITING | Week 1 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},
        "math" : {"video_url": '<iframe width="727" height="409" src="https://www.youtube.com/embed/Bn5R0c2q8aI" title="SAT MATH | Week 1 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},   
        "sub_form": "https://forms.gle/BofMetXXHmvQauDL7"
    }, 
    "2": {
        "reading" : {"video_url": '<iframe width="640" height="360" src="https://www.youtube.com/embed/LvjFv7dTdRg" title="SAT READING | Week 2 - Part 1 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": '<iframe width="616" height="324" src="https://www.youtube.com/embed/9P-0q2PILX8" title="SAT READING | Week 2 - Part 2 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'},
        "writing" : {"video_url": '<iframe width="640" height="360" src="https://www.youtube.com/embed/9urYaY-5yZU" title="SAT WRITING | Week 2 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},
        "math" : {"video_url": '<iframe width="640" height="360" src="https://www.youtube.com/embed/wiZJ5uoVfcU" title="SAT MATH | Week 2 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},   
        "sub_form": "https://forms.gle/eSqgFhwPoMTCogAU7"
    },
    "3": {
        "reading" : {"video_url": '<iframe width="633" height="340" src="https://www.youtube.com/embed/-9Fpq9totUQ" title="SAT READING | Week 3 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},
        "writing" : {"video_url": '<iframe width="616" height="385" src="https://www.youtube.com/embed/dlm3AfOZR10" title="SAT WRITING | Week 3 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},
        "math" : {"video_url": '<iframe width="640" height="360" src="https://www.youtube.com/embed/fwrvRn7ehOU" title="SAT MATH | Week 3 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},   
        "sub_form": "https://forms.gle/wnfpNKFBhuuciMTi7"
    },
    "4": {
        "reading" : {"video_url": "url", "extra": None},
        "writing" : {"video_url": '<iframe width="616" height="277" src="https://www.youtube.com/embed/51BWcBb4NVw" title="SAT WRITING | Week 4 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},
        "math" : {"video_url": '<iframe width="640" height="360" src="https://www.youtube.com/embed/CNc-qDnslR4" title="SAT MATH | Week 4 - CTP 2022 Summer Session Beginner & Intermediate Videos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', "extra": None},   
        "sub_form": "url"
    },
    "5": {
        "reading" : {"video_url": "url", "extra": None},
        "writing" : {"video_url": "url", "extra": None},
        "math" : {"video_url": "url", "extra": None},   
        "sub_form": "url"
    },
    "6": {
        "reading" : {"video_url": "url", "extra": None},
        "writing" : {"video_url": "url", "extra": None},
        "math" : {"video_url": "url", "extra": None},   
        "sub_form": "url"
    }
}