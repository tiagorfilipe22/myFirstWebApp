from cs50 import SQL
from flask import Flask, render_template, request, redirect, flash, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import re
import resources


app = Flask(__name__)
app.secret_key = "helothisisawensite99"

# session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set variable to database
db = SQL("sqlite:///data.db")

# set variable
role = ["Admin", "Admin User", "Power User", "User", "New User", "Password Reset"]
priority = ["Low", "Medium", "High"]
ticketStatus = ["No Status", "In Progress", "In Pause", "Terminated", "Unresolved", "Archived"]
email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'




# check login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect("/") # Redirect to the login page or wherever necessary
        return f(*args, **kwargs)  # Proceed with the actual route if logged in
    return decorated_function



# index route
@app.route("/", methods=["GET", "POST"])
def index():

    # get user session user id and permission
    userID = session.get("user_id")
    permission = session.get("permission")
    # if userID is none go to login
    if userID is None:
        return render_template("index.html")
    # if userID in < 2 (administrators) check for new users
    elif permission == 4: # new user
        flash("Waiting for admin aproval.")
        return render_template("index.html")
    elif permission == 5: # reset password
        return redirect("/profile")
    elif permission <  2: # administrators 
        return redirect("/checkuser")



    # if login go to tickets
    return redirect("/tickets")


# login function
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        # get variables
        email = request.form.get("email")
        password = request.form.get("password")

        # check variables
        if not email:
            flash("No Email!")
            return render_template("index.html")      
        elif not password:
            flash("No Password!")
            return render_template("index.html")

        # select user in DB
        user = db.execute("SELECT * FROM users WHERE email = ?", email)

        # if user not found
        if not user:
            flash("Invalid Email and/or Password.")
            return render_template("index.html")
        # if user not active
        elif user[0]["active"] == 1:
            flash("User not Active, call admin.")
            return render_template("index.html")
        # if password not check or email
        elif len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            # return to login and show message
            flash("Invalid Email and/or password.")
            return render_template("index.html")

        # remember user login in session and redirect to links
        session["user_id"] = user[0]["id"]
        session["permission"] = user[0]["permission"]

        return redirect("/")

    # if get method
    return render_template("login.html")

# check user route
@app.route("/checkuser", methods=["GET", "POST"])
@login_required
def checkuser():


    if request.method == "POST":
        # get userID selected
        userID = request.form.get("id")

        if userID:
            db.execute("UPDATE users SET permission = 3 WHERE id = ?", userID)
            user = db.execute("SELECT * FROM users WHERE id = ?", userID)

            # get name and email
            name = user[0]["name"]
            email = user[0]["email"]

            # compose email text
            text = "Hello " + name + "\nYour Registration has been aproved.\nLink: https://animated-journey-p94gx55q6gvhrrv5-5000.app.github.dev/\nWelcome!"
            # send email
            resources.email_alert("Help Desk Project CS50 - Aproval", text, email)
            return redirect("/checkuser")
        
    # check for new registered USERS
    # get info from database and render in links
    users = db.execute("SELECT * FROM users WHERE permission = 4 AND id > 1")
    if users:
        return render_template("checkuser.html", users = users)
    else:
        return redirect("/tickets")

# register function
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # get variables
        email = request.form.get("email")
        name = request.form.get("name")
        # uppercase letters
        name = name.title()
        password = request.form.get("password")
        pConfirmation = request.form.get("pConfirmation")

        # check if valid email
        if not re.match(email_pattern, email):
            flash("Have to register with a valid email!")
            return render_template("register.html")
        # variable validation
        elif not email:
            flash("No email!")
            return render_template("register.html")
        elif not name:
            flash("No Name!")
            return render_template("register.html")
        elif not password:
            flash("No Password!")
            return render_template("register.html")
        elif len(password) != 8:
            flash("Password must have 8 Chars or more")
            return render_template("register.html")
        elif not pConfirmation:
            flash("You have to confirm the password!")
            return render_template("register.html")
        elif password != pConfirmation:
            flash("Passwords don't match!")
            return render_template("register.html")

        # generate hash from password
        pHash = generate_password_hash(password)

        # try to add to database if not add its because email already exists
        try:
            db.execute(
                "INSERT INTO users (email, hash, name) VALUES(?, ?, ?)", email, pHash, name
                )
        except:
            # return to register and show message
            flash("Email already taken")
            return render_template("register.html")
        
        # send email to new user
        text = "Hello " + name + "\nYou have complete registration on Help Desk Project CS50.\nLink: https://animated-journey-p94gx55q6gvhrrv5-5000.app.github.dev/\nWait for admin Aproval."
        resources.email_alert("Help Desk Project CS50 - Registration", text, email)
        
        # send email to each admin
        # get admins
        admins = db.execute("SELECT email FROM users WHERE permission < 2")
        text = "Email: " + email + "\nName:  " + name

        for admin in admins:
            email_admin = admin["email"]
            resources.email_alert("Help Desk Project CS50 - New User", text, email_admin)

        flash("Wait for Admin aproval! Check Email!")
        return redirect("/")

    return render_template("register.html")




# logout function
@app.route("/logout")
def logout():
    

    # forget user and redirect to index
    session.clear()
    return redirect("/")

# change function
@app.route("/profile", methods=["GET", "POST"])
@login_required
def password():


    # get user by the session
    userID = session.get("user_id")
    user = db.execute("SELECT * FROM users WHERE id = ?", userID)
    # if post method
    if request.method == "POST":

        # get VALUES
        pOld = request.form.get("pOld")
        password = request.form.get("password")
        pConfirmation = request.form.get("pConfirmation")
        name = request.form.get("name")
        name = name.title()

        # variable validation
        if not name and not pOld and not password and not pConfirmation:
            flash("No information changed")
            return redirect("/profile")
        
        # in name is unputed change in db
        if name:
            flash("Name Changed!")
            db.execute("UPDATE users SET name = ? WHERE id = ?", name, userID)

        
        
        if pOld and password and pConfirmation:
             # get user ID and data from db

            if len(password) != 8:
                flash("Password must have 8 Chars or more")
                return redirect("/profile")
            # check if old password in corret
            if password == pConfirmation:
                # get hash only if passowrd its equal the Pass Confirmation
                dbPass = db.execute("SELECT hash FROM users WHERE id = ?", userID)[0]["hash"]
                if  check_password_hash(dbPass, pOld):
                    # generate new password hash
                    new = generate_password_hash(password)
                    db.execute("UPDATE users SET hash = ? WHERE id = ?", new, userID)
                    if session.get('permission') == 5:
                        db.execute("UPDATE users SET permission = 3 WHERE id = ?", userID)
                        flash("You have changed Password!")
                        return redirect("/logout")
                    flash("You have changed Password!")
                    return redirect("/profile")
                else:
                    flash("Provided Old Password not match!")
                    return redirect("/profile")
            else:
                flash("Confirmed password dont match")
                return redirect("/profile")    
            
        elif pOld or password or pConfirmation:
            flash("You have to confirm the passwords fields!")
            return redirect("/profile")
        else:
            return redirect("/profile")


    return render_template("profile.html", user = user)


# users function
@app.route("/users")
@login_required
def users():

    # get serssion id
    userID = session.get("user_id")

    # get info from database and render users diferent from admin and itself
    users = db.execute("SELECT * FROM users WHERE id > 1 AND id != ?", userID)

    return render_template("users.html", users = users, role = role)

# EDIT USER
@app.route("/edituser")
@login_required
def edituser():
  
    # get ticket id
    userID = request.args.get("id")

    if userID:
        # save show ticket in session
        session["edit_user"] = userID
    else:
        # ticket id get from session
        userID = session["edit_user"]

    # get info from database and render in links
    user = db.execute("SELECT * FROM users WHERE id = ?", userID)
    return render_template("edituser.html", user = user, role = role)

# DEACTIVATE USER
@app.route("/deactivateuser")
@login_required
def deactivateuser():

    # get edit user session ID
    userID = session["edit_user"]
    if userID:
        db.execute("UPDATE users SET active = 1 WHERE id = ?", userID)
        flash("User Deactivated!")
        return redirect("/edituser")
    else:
        flash("Error ocurred!")
        return redirect("/users")

# ACTIVATE USER
@app.route("/activateuser")
@login_required
def activateuser():

    # get edit user session ID
    userID = session["edit_user"]
    if userID:
        db.execute("UPDATE users SET active = 0 WHERE id = ?", userID)
        flash("User Activated!")
        return redirect("/edituser")
    else:
        flash("Error ocurred!")
        return redirect("/users")

# CHANGE VALUES USER
@app.route("/changeuser")
@login_required
def changeuser():

    # get edit user session ID
    userID = session["edit_user"]
    permission = request.args.get("permission")
    if not permission:
        flash("Must Select a permission")
        return redirect("/edituser")
    if userID:
        db.execute("UPDATE users SET permission = ? WHERE id = ?", permission, userID)
        flash("Permission changed")
        return redirect("/edituser")
    else:
        flash("Error ocurred!")
        return redirect("/users")



# DELETE USER
@app.route("/deleteuser")
@login_required
def deleteuser():

    # get edit user session ID
    userID = session["edit_user"]
    if userID:
        db.execute("DELETE FROM users WHERE id = ?", userID)
        flash("USER is DELETED")
        return redirect("/users")
    else:
        flash("Error ocurred!")
        return redirect("/users")
        

# RESET PASSWORD USER
@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():

    if request.method == "POST":

        # try to get edit user session ID
        try:
            userID = session["edit_user"]
        # reset password in "forgot password button"
        except:
            email = request.form.get("email")

            # validade email
            if not re.match(email_pattern, email):
                flash("Input a valid email!")
                return redirect("/resetpassword")

            password = resources.get_random_string()
            hash = generate_password_hash(password)
            
            # change permission to 5
            # change password
            try:
                db.execute("UPDATE users SET hash = ?, permission = 5 WHERE email = ?", hash, email)
                
            except:
                flash("Error ocurred!")
                return redirect("/")


            # send new email with one time password
            user = db.execute('SELECT * FROM users WHERE email = ?', email)
            name = user[0]['name']
            text = "Hello " + name + "\nYour password has been reseted.\nNew Password: " + password
            resources.email_alert("Help Desk Project CS50 - Password Reset", text, email)
            # return users
            flash("Check your email with password!")
            return redirect("/")


        # admin reset password 
        password = resources.get_random_string()
        hash = generate_password_hash(password)
            
        # change permission to 5
        # change password
        db.execute("UPDATE users SET hash = ?, permission = 5 WHERE id = ?", hash, userID)


        # send email with one time password
        user = db.execute('SELECT * FROM users WHERE id = ?', userID)
        email = user[0]['email']
        name = user[0]['name']
        text = "Hello " + name + "\nYour password has been reseted.\nNew Password: " + password
        resources.email_alert("Help Desk Project CS50 - Password Reset", text, email)
        # return users
        flash("Password reseted to " + name + "!")
        return redirect("/users")
            
    
    return render_template("getemail.html")
        

# tickets
@app.route("/tickets", methods=["GET", "POST"])
@login_required
def tickets():



    if request.method == "POST":
        # select option filter
        status = request.form.get("status")
        if status == "reset":
            return redirect("/tickets")

        # if administrator or poweruser get all tickets
        if session.get("permission") < 3:
            tickets = db.execute(
                """
                SELECT tickets.id, tickets.subject, tickets.status, tickets.priority,
                users.name AS creator_name FROM tickets
                LEFT JOIN users ON tickets.creator = users.id
                WHERE tickets.status = ? ORDER BY priority DESC, time ASC
                """
                , status
                )

            return render_template("tickets.html", tickets = tickets, status = ticketStatus, priority = priority)
        # if not get only their own tickets
        else:
            userID = session.get("user_id")
            tickets = db.execute(
                """
                SELECT tickets.id, tickets.subject, tickets.status, tickets.priority,
                users.name AS creator_name FROM tickets
                LEFT JOIN users ON tickets.creator = users.id
                WHERE tickets.status = ? AND users.id = ? ORDER BY priority DESC, time ASC
                """
                , status, userID
                )
            
            return render_template("tickets.html", tickets = tickets, status = ticketStatus, priority = priority)

    # if administrator or poweruser get all tickets
    if session.get("permission") < 3:

        tickets = db.execute(
            """
            SELECT tickets.id, tickets.subject, tickets.status, tickets.priority,
            users.name AS creator_name FROM tickets
            LEFT JOIN users ON tickets.creator = users.id
            WHERE tickets.status < 5 ORDER BY priority DESC, time ASC
            """
            )
        return render_template("tickets.html", tickets = tickets, status = ticketStatus, priority = priority)
    # if not get only their own tickets
    else:
        userID = session.get("user_id")
        tickets = db.execute(
            """
            SELECT tickets.id, tickets.subject, tickets.status, tickets.priority,
            users.name AS creator_name FROM tickets
            LEFT JOIN users ON tickets.creator = users.id
            WHERE tickets.status < 5 AND users.id = ? ORDER BY priority DESC, time ASC
            """
            , userID
            )
        
        return render_template("tickets.html", tickets = tickets, status = ticketStatus, priority = priority)


# add tickets
@app.route("/newticket", methods=["GET", "POST"])
@login_required
def newticket():



    if request.method == "POST":
        userID = session.get("user_id")

        # get variables
        subject = request.form.get("subject")
        problem = request.form.get("problem")
        prioritie = request.form.get("priority")

        # First Letter UpperCase
        subject = resources.getFirstUpper(subject)
        problem = resources.getFirstUpper(problem)

        # variable validation
        if not subject:
            flash("No subject!")
            return render_template("newticket.html")
        elif not problem:
            flash("No problem!")
            return render_template("newticket.html")
        elif not prioritie:
            flash("No priority!")
            return render_template("newticket.html")
        

        # add to tickets database
        db.execute(
            "INSERT INTO tickets (subject, description, priority, creator) VALUES(?, ?, ?, ?)",
            subject, problem, prioritie, userID
        )

        # get name from users
        name = db.execute("SELECT name FROM users WHERE id = ?", userID)

        ticketID = db.execute("SELECT id FROM tickets ORDER BY id DESC LIMIT 1")

        # get name of priority with the value
        prioritys = priority[int(prioritie)]
        text = "Subject: " + subject + "\nFrom: " + name[0]["name"] + "\nPriority: " + prioritys + "\nDescription: " + problem + "\nLink: https://animated-journey-p94gx55q6gvhrrv5-5000.app.github.dev/showticket?id=" + str(ticketID[0]["id"])
        admins = db.execute("SELECT email FROM users WHERE permission < 3")

        # send email for each admin
        for admin in admins:
            email_admin = admin["email"]
            resources.email_alert("Help Desk Project CS50 - New Ticket", text, email_admin)

        return redirect("/tickets")

    return render_template("newticket.html")

@app.route("/showticket")
@login_required
def showticket():



    # get ticket id
    ticketID = request.args.get("id")

    if ticketID:
        # save show ticket in session
        session["show_ticket"] = ticketID
    else:
        # ticket id get from session
        ticketID = session["show_ticket"]

    # get tickets
    ticket = db.execute(
        """
        SELECT tickets.id, tickets.subject, tickets.description, tickets.status, tickets.priority, tickets.time, tickets.creator, users.name AS creator_name
        FROM tickets LEFT JOIN users ON tickets.creator = users.id
        WHERE tickets.id = ?
        """
        , ticketID
        )
    
    # get solutions
    solutions = db.execute(
        """
        SELECT s.*, u.name AS creator_name
        FROM solutions s
        JOIN interchange i ON s.id = i.solution_id
        JOIN tickets t ON t.id = i.ticket_id
        JOIN users u ON s.creator = u.id
        WHERE t.id = ?;
        """
        , ticketID
        )
    messages = db.execute(
        """
        SELECT messages.ticket_id, messages.message, messages.time, users.name AS creator_name
        FROM messages LEFT JOIN users ON messages.creator = users.id
        WHERE ticket_id = ?
        ORDER BY messages.time DESC
        """,
        ticketID
    )
    return render_template("showticket.html", ticket = ticket, priority = priority, status = ticketStatus, solutions = solutions, messages = messages)

@app.route("/saveticket", methods=["GET", "POST"])
@login_required
def saveticket():

    if request.method == "POST":
        status = request.form.get("status")
        ticketID = session["show_ticket"]
        

        db.execute("UPDATE tickets SET status = ? WHERE id = ?", status, ticketID)
        
        # if ticket terminated
        if status == '3':
            # get info to send email, admin that terminated ticket, ticket information, and email of the creator
            admin = db.execute("SELECT name FROM users WHERE id = ?", session['user_id'])
            ticket = db.execute("SELECT * FROM tickets WHERE id = ?", ticketID)
            creator = ticket[0]["creator"]
            email = db.execute("SELECT email FROM users WHERE id = ?", creator)
            text = "Subject: " + ticket[0]['subject'] + "\nTerminated by: " + admin[0]["name"] + "\n\nGo Review the Ticket" + "\n\nLink: https://animated-journey-p94gx55q6gvhrrv5-5000.app.github.dev/showticket?id=" + str(ticketID)

            resources.email_alert("Help Desk Project CS50 - Ticket Terminated", text, email[0]["email"])

        return redirect("/showticket")
    

@app.route("/solutions", methods=["GET", "POST"])
@login_required
def solutions():


    listcategories = db.execute("SELECT DISTINCT category FROM solutions ORDER BY category")

    if request.method == "POST":
        # select option filter
        category = request.form.get("category")
        if category == "reset":
            return redirect("/solutions")

        # get solutions
        solutions = db.execute(
            """
            SELECT solutions.id, solutions.subject, solutions.category, solutions.time, users.name AS creator_name
            FROM solutions LEFT JOIN users ON solutions.creator = users.id
            WHERE category = ? ORDER BY subject
            """
            , category)
        
        # get single category for table
        categories = db.execute("SELECT DISTINCT category FROM solutions WHERE category = ?", category)

        return render_template("solutions.html", solutions = solutions, categories = categories, list = listcategories)


    solutions = db.execute(
        """
        SELECT solutions.id, solutions.subject, solutions.category, solutions.time, users.name AS creator_name
        FROM solutions LEFT JOIN users ON solutions.creator = users.id ORDER BY subject;
        """
        )
    # list of categories for tables
    categories = listcategories
    return render_template("solutions.html", solutions = solutions, categories = categories, list = listcategories)

@app.route("/newsolution", methods=["GET", "POST"])
@login_required
def newsolution():


    # if post method
    if request.method == "POST":

        
        # if new category inserted get from the field addcategory and category
        if request.form.get("category") == "newcategory":
            category = request.form.get("addcategory")
        else:
            category = request.form.get("category")
        
        # get variables
        category = category.title()
        subject = request.form.get("subject")
        description = request.form.get("description")
        
        # uppercase first letter
        subject = resources.getFirstUpper(subject)
        description = resources.getFirstUpper(description)

        # check variables
        if not subject or not category or not description:
            flash("information required!")
            return redirect("/newsolution")

        # get user id
        userID = session["user_id"]

        # add to links database
        db.execute(
            "INSERT INTO solutions (category, subject, description, creator) VALUES(?, ?, ?, ?)",
            category, subject, description, userID
        )

        return redirect("/solutions")

    categories = db.execute("SELECT DISTINCT category FROM solutions ORDER BY category")
    return render_template("newsolution.html", categories = categories)

@app.route("/showsolution")
@login_required
def showsolution():


    # get solution id
    solutionID = request.args.get("id")

    if  solutionID:
        # save show solution in session
        session["show_solution"] = solutionID
    else:
        # solution id get from session
        solutionID = session["show_solution"]


    # get solutions
    solution = db.execute(
        """
        SELECT solutions.id, solutions.subject, solutions.category, solutions.description, solutions.time, solutions.creator, users.name AS creator_name
        FROM solutions LEFT JOIN users ON solutions.creator = users.id
        WHERE solutions.id = ?
        """
        , solutionID
        )

    return render_template("showsolution.html", solution = solution)

@app.route("/newsolutiontoticket", methods=["GET", "POST"])
@login_required
def newsolutiontoticket():

    # if post method
    if request.method == "POST":

        # check if its a new category or not
        if request.form.get("category") == "newcategory":
            category = request.form.get("addcategory")
        else:
            category = request.form.get("category")
        
        # get variables
        subject = request.form.get("subject")
        description = request.form.get("description")
        ticketID = session["show_ticket"]

        # check variables
        if not subject or not category or not description:
            flash("information required!")
            return redirect("/newsolution")

        # get user id
        userID = session["user_id"]

        # add to solution database
        db.execute(
            "INSERT INTO solutions (category, subject, description, creator) VALUES(?, ?, ?, ?)",
            category, subject, description, userID
        )

        # get last add solution ID
        solutionID = db.execute("SELECT id FROM solutions ORDER BY id DESC LIMIT 1")

        # add solution ID interchange with ticket ID
        db.execute("INSERT INTO interchange (solution_id, ticket_id) VALUES(?, ?)", solutionID[0]["id"], ticketID)

        return redirect("/showticket")

    # render html with saved show ticket ID
    ticketID = session["show_ticket"]
    # get list of categories from solutions
    categories = db.execute("SELECT DISTINCT category FROM solutions ORDER BY category")
    return render_template("newsolutiontoticket.html", categories = categories, ticketID = ticketID)


# add tickets
@app.route("/newmessage", methods=["GET", "POST"])
@login_required
def newmessage():


    
    if request.method == "POST":
        # get variables
        userID = session.get("user_id")
        ticketID = session.get("show_ticket")
        # get variables
        message = request.form.get("message")
        # get uppercase letter
        message = resources.getFirstUpper(message)


        # variable validation
        if not message:
            return redirect("/showticket")
        

        # add to links database
        db.execute(
            "INSERT INTO messages (ticket_id, creator, message) VALUES(?, ?, ?)",
            ticketID, userID, message
        )

        return redirect("/showticket")
    
@app.route("/deleteticket")
@login_required
def deleteticket():
    
    # get ticket id from session
    ticketID = session.get("show_ticket")
    db.execute("DELETE FROM tickets WHERE id = ?", ticketID)
    return redirect('/tickets')
    
@app.route("/deletesolution")
@login_required
def deletesolution():
    
    # get solution id from session
    solutionID = session.get("show_solution")
    db.execute("DELETE FROM solutions WHERE id = ?", solutionID)
    return redirect('/solutions')


