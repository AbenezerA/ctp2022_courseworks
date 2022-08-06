# CTP Summer 2022 Student Courserworks Website
### Video Demo:  <URL HERE>
### Description: A mock website that lets students enrolled in the CTP mentorship program create accounts where they'll find uploaded instruction videos and assigned homework, in addition to resources and announcements.

## CTP Ethiopia

Counseling and Test Preparation Ethiopia (CTP Ethiopia) is an educational program founded by a group of Columbia University students that provides in-depth mentorship sessions to high school students in Ethiopia applying to universities in the United States.

During the start of the summer 2022 session of the CTP mentorship program, the Tech team (of which I am a part) decided to program a student courseworks web page where mentees would access course material provided by instructors. However, due to issues with hosting and deploying the website, the team scrapped the web page idea and went with a rudimentary Telegram channel instead.

However, having seen (and continuing to see) several inadequecies with using the Telegram channel, including but not limited to the fluidity of posts, efficiency of user interaction and notification (old posts will quickly get drowned out by newer ones). Thus, I decided to design and code a mock webpage (a sort of "what could have been" for the webpage) using the Flask framework for server-side validations and interactions.

Much of the inspiration for the visuals comes from a discussion that was had among Tech team members. In addition, Harvard's course CS50x: Introduction to Computer Science helped familiarize me to Flask, Python, and database managment. 

The site makes exhaustive use of Bootstrap and Boostrap's elements for style.

## Usage
The website comprises of multiple html pages and routes that clearly facilitate the user (presumably the CTP student/mentee) to access course content - of which there are three main types: instruction videos, assignments, and submission forms. The site is designed to let the student easily get at the content of the specific week and subject they prefer. Before accessing the content, however, the user has to create and log into an account. In summary, the two particular processes facilitated by the site are account creation and content access.

## HTML Pages
### layout
Being the layout, or base, HTML, `layout.html` consists of the skeletal templates that are inherited by every other html file in this project. The user might notice that every page consists of 3 major elements: a navbar at the top (`<nav>`), a main body element in the center (`<main>`), and a footer at the bottom (`<footer>`). All three of these have been included in `layout.html`. 

In addition, this HTML file also consists of the sub-elements contained within the big-3. Almost all of the content in the navbar, including the company logo and buttons for `Register` and `Log In` (before log-in) and  `Change Password` and `Log Out` (after log-in) are included in `layout.html`. Using Jinja2 and information from the `Session` dictionary, the template determines if the user has logged in and, thus, which group of buttons to display.

In its `<main>` body element, `layout.html` first renders any flashes that have been flashed by `app.py` (both errors and successes) before rendering the meat of the content, most of which is determined not by the template but by individual pages using Jinja2. To ease the display of html elements, `<main>` is implemented as a 2x2 CSS grid (see `styles.css`).

Finally, `<footer>` consists of copyright information and a link to the currently-active CTP information website. This element is static across all pages.

### index
The landing page, `index.html`, is the first loaded from the server. It is currently mostly barren and serves mainly to display content to a logged-out user. It is rendered when the `"/"` route is accessed and inherits the majority of its information using Jinja2 from `layout.html`.

Because the user hasn't yet signed in when accessing this page, `Session["user_id"]` has not been set. `layout.html` notices this and displays the correct pair of buttons - `Register` and `Log In` - on the navbar. The next step for the user is to click on one of these buttons.

`layout.html` also changes the route destination of clicking on the logo to `"/"` itself rather than the logged-in user dashboard `"/videos"`. Using Jinja2, `index.html` tells `layout.html` to display, in `<main>` a carousel depicting images of CTP crew members. `<footer>` is left unchanged.

### register
A new user will click on the `Register` button, which will send them to the "`/register`" route using `GET`. This process renders `register.html` to the user, displaying a form to receive the following credentials: Username, Email address, Password, and Section. 

All of these credentials are validated server-side. If any field is missing or entry is invalid, a `flash` message is returned which is picked up by `layout.html` and displayed as an alert. Existing usernames and email addresses are returned back as invalid and the password is confirmed again by the user. The user selects a section based on which class they were accepted into by CTP: `beginner` or `intermediate`. 

After validation, each credential is stored in the database, `ctp.db`, which also assigns to each registered user an autoincremented student id. Everything is stored as is except for the password, which is hashed then stored. Finally, a new key is added to the `Session` dictionary called "`user_id`" equal to the id generated by the database. This key is used throughout the website to check if the user is logged in or not.

In the end, "`/register`" redirects to "/`video`" which renders the dashboard html: `videos.html`.

In terms of visuals, the form is made to fit all 4 grids of `<main> `and centerd to the middle of the page.

### login
If the user clicks on the `Log In` button in the landing page, they'll be redirected to "/`login`", rendering `login.html`. Here, the user is met with a form where they enter only `Username` and `Password` credentials. If the password matches with the hashed password on record for the inputted username, the user is successfully logged in to their dashboard ("/`videos`").

If the input is invalid or the passwords don't match, however, the user is alerted using `Flask.flash` messaging and prompted to input again.

Like the one in `register.html`, the form in `login.html` is also made to fit all 4 grids of `<main>` and centerd on the page, all made possible by CSS gridding.

### videos
When a new user registers succesfully or an existing user logs in, the first page (**dashboard**) to be displayed is `videos.html`, rendered by "/`videos`". Here, the user gains access to instruction videos that populate the page in the form of embedded YouTube videos.

Visually, `videos.html` has a sidebar to the left which is trigerred by `layout.html` because "/`videos`" sets Session["weeks_visible"] to `True`. The sidebar allows the user to choose the specific video to display, classified based on week number and subject type. It is also made to take up the two left slots of the `<main>` CSS grid. With a series of dropdows and buttons, the user can select `week number` and `subject`, which `app.py` uses to get the embed link and code for the right video to display on the content side of the page.

There are 7 weeks depicted in the side bar, 6 for each instruction week and a resources week (for all intents taken as week 0). There are theoretically 3 subjects - `SAT Reading`, `SAT Writing`, and `SAT Math` - for each numbered week. The resources week has 2 subjects - `Orientation` and `Others` - that can be expanded upon, just like any other week.

The content side of the page takes up the two right slots of the `<main>` CSS grid to display the embedded YouTube video requested by the user.
Using an `extra` variable, the content side can accomodate one extra video (see **Week 2, SAT Reading**).

The user will also notice a new pair of buttons in the navbar: `Videos` and `Assignments`. These are part of the individual pages (instead of the template) and the user can change between the two pages as they wish as long as they're logged in.

### assignments
A sister page for `videos.html`, assignments has basically the same set up. However, instead of videos, it displays to the user the assigned homeworks and assignments for each subject during each week (selected via the sidebar) as well as a link to the Google submission form for that week.

Since the layout is very similar to `videos.html`, the user won't have trouble travelling to the corresponding assignment of a specific video.

The page is rendered by "/`assignments`" which also sends necessary information to display the assignment file and submission form link. After getting information on the week and subject from the buttons on the sidebar, "/`assignments`" assembles a filename which the page uses to open a file in the statics folder that corresponds to the assignment file in question. 

The route also gathers the submission link ur for that week from a dictionary in `app.py` and sends it to `assignments.html` to display the submission form.

### change_pw
In addition to viewing the course content, a logged in user has the option to change their password using the `Change Password` button on the navbar.

The button routes to "/`change_pw`" through a `GET` command, rendering `change_pw.html`. The page itself contains a form very similar to those in `Register` and `Log In`.

In the form, the user submits their old password, which is cross-checked with their hashed password on record (the username is read in from `session["user_id"]`). The user then submits a new password which is reconfirmed. If all goes well, the hashed password in the database attached to the user's username is changed to a hashed version of the new password and the user is redirected to "/`login`" for security purposes.

If there is an error with the user's entries, the user is alerted of which entry is erroneous through a `Flask.flash` message.

### log_out
Though there technically isn't a `log_out.html` page, there is a "/`log_out`" route triggered when the `Log Out` button in the nav bar is pressed which simply clears the active session (and all dictionary variables defined) before redirecting the user to the landing page, `index.html`

### home
The `home.html` page had previously served as the dashboard page of a newly-logged-in user but was **scrapped** for being too redundant.

### usermgmt
This page can only be accessed by appending the route "/`usermgmt`" in the browser's search bar. Note that it has been configured to only work for the `admin` (more specifically, the user with `session["user_id"] = 1`). If a non-admin tries to access this route, an error alert message will be displayed and the user will be redirected to the dashboard.

This page is used to display the `ctp.db` database in the form of an HTML table. The table shows all the information shared with every account in the database, including `ID`, `Username`, `Email`, and `Section`. As such, viewing the database entries is made easier than accessing `ctp.db` with `MySQL` or `SQLite3` syntax.

In addition to the user information, each row in the table also contains a button Deregister which deletes the user from the database. The button itself routes to "/`deregister`" which takes care of opening the database and removing the user with `SQLite3` code.

## Application
### app.py
app.py is a `Flask` application written in `Python` that handles almost all of the server-side functionality. `app.py` has the power to modify and create SQL tables in the database `ctp.db`, render `HTML` templates, and handle user account managment.

Accounts are managed as `sessions` using Flask. Instead of caching user data, `app.py` ensures that sessions use the filesystem and not cookies.

### Helper functions
#### login_required
The majority of the routes in this web app (and the website in general) require that the user be logged in to access their content. This check is made by the `decorator` function `login_required()` which essentially searches if `session["user_id"]` has been set when a route is called - a signal that the user has logged in.

If `session["user_id"]` has not been set and the user has not signed in, any function that is wrapped by `login_required` redirects the user to the Log In page and route.

### Routing functions
There is one function (and routes) for each html page as well as three functions associated with routes but which don't render HTML pages (`deregister`, `get_pdf`, and `log_out`). The following is a list of routing functionsaccoding to order of appearance in `app.py`
##### index - "/"
Clears the current session (logs user out) and displays `index.html` to the user. This is the landing page that is called upon running the Flask application.

##### login - "/login"
Renders `login.html` if reached through a `GET` command (such as through redirecting from a press of the `Log In` button).

If reached through a `POST` command (such as when the form on `login.html` is submitted), this function collects all user-inputted data from the form and logs the user in. Any errors are returned as `flash` messages which are later picked up by the template layout.html and displayed as `alerts`.

A logged in user has the three properties `session["user_id]` and `session["user_section"]` set to the user's `id` and `section` (from the database). In addition, `session["weeks_visible"]`, which determines if the sidebar is displayed, is set to True - it is then set to False by any route that requires the sidebar to be toggled off (such as by `change_pw`, `logout`, and `usermgmt`).

The user is also greeted by a welcome alert toggled by `Flask`'s `flash` function.

##### logout - "/logout"
Clears current session, effectively logging user out, and redirects to `index.html`

##### register - "/register"
Renders `register.html` if accessed through a `GET` command (such as by a button clicked from the landing page).

Registers new user if accessed through `POST` (such as when the user submits the form on `register.html`). The user submits their information (see `register.html` above) which is then added to the database through a `SQLite3` command from the `cs50` library and any errors are returned as flash messages.

The password is hashed using `generate_password_hash` from the `werkzeug.security` library before being registered in the database.

`REGEX` is used to validate the user-inputted email (see code comments for acknowledgment).

The registration process is similar to the login process in terms of the session variables altered.

##### change_pw - "/change_pw"
If accessed through `GET`, it sets `session["weeks_visible"]` to `False` before rendering `change_pw.html` in order not to display the sidebar.

If accessed through `POST`, it changes the hashed password stored in the database corresponding to the current user. To do this, it collects and validates data from the form on `change_pw.html`. Any errors are returned as flash messages.

The user is logged out upon form submission and has to log back in with the newly changed password to access course content.

##### usermgmt - "/usermgmt"
Displays `usermgmt.html` with the sidebar toggled off. This page is the user managment hub designed for the admin of the site making it easier to access user information and remove users.

The route can only be accessed by a logged in `admin` (`user_id = 1`) and redirects back to "/`videos`" otherwise.

##### deregister - "/deregister"
Does nothing if reached by `GET` (which is possible only if the user types route in search bar).

If accessed through `POST`, such as through one of the `Deregister` button present on each row in the `usermgmt.html` table, this function removes a user (along with all their stored data) from the database. The id of the user in question is retrieved from the button, which, along with a hidden input type of value `user_id`, serves as a form.

The deletion is made with a `SQLite3` query using the `cs50` library's `db` funtion.

##### videos - "/videos"
Displays `videos.html`, along with one or two instruction videos to user. The videos are assembled as embedded YouTube iframes whose urls are stored in a dictionary called `WEEKS`.

The `WEEKS` dictionary also maps the week number and subject type to each video url.

After receiving the week and subject requested by the user from the buttons on the sidebar, this function looks up the `WEEKS` dictionary to find the url of the video for the specified week and subject.

The default week is `1` and the default subject is `reading` (useful if accessed through `GET`, for instance).

New video urls can be added simply by adding the link to the right key in the `WEEKS` dictionary.

In the end, this function renders `videos.html` with all the necessary information about the video to be displayed.

##### assignments - "/assignments"
Displays `assignments.html`, along with the assignment and submission link for the requested week and subject.

The assignments are PDF files stored as static files in `/static/docs`. The names of these files follow the formula:

> "week[week_number][subject]_[section].pdf"

The main purpose of this function is to build a file name that will open up the correct file when accessed. It does so by getting week and subject information from the buttons in the sidebar of `assignments.html`.

This function also uses the `WEEKS` dictionary to retrieve the corresponding submission link stored for a specific week and subject.

In the end, the function renders `assignments.html` by passing through information about the file and submission link to display.

##### get_pdf(filename) - "/get-pdf/<filename>"
Used to display a link that, when clicked, opens up a PDF file to display to the user

Used by "/`assignments`" to display the appropriate assignment file to the user.

## Database
The database used to store user information is `ctp.db`. It is modified by `app.py` using `SQLite3` commands made simpler by `cs50`'s `db()` function.

The database consists of a single table called '`users`' which stores the user's `id` (an autoincrementing value set by the database itself), `username`, `email`, `password` (hashed), and `section`. These values can all be accessed at any time by a similar `SQLite3` command.

The database is displayed in `usermgmt.html` and "/`usermgmt`" from which it accepts deletion commands as well.

## Other files
#### requirements.txt
Contains all libraries used in the making of the program (along with their versions) so that anyone can download and locally modify program files.

#### .env
Contains the environmental variables configured during the making of this program.

#### config.py
Contains the environmental variables configured during the making of this program.

## Folders
#### static and templates
Contain the static files and template html files used to run the program.

##### static/docs
Contains the assignment files that are displayed to the user in `assignments.html` by "/` `"

##### static/img
Contains the image files used throughout the site.

#### flask_session
Contains information about the sessions created as the program runs.

#### __pycache__
Contains leftover cached user responses.
