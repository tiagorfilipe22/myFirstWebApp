from cs50 import SQL
from flask import Flask, render_template, request, redirect, flash, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import push_alert
import email_alert
import passgenerator
import re


app = Flask(__name__)
app.secret_key = "helothisisawensite99"

# session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set variable to database
db = SQL("sqlite:///data.db")

# set variable to csv to log add links and delete links
role = ["Admin", "Admin User", "Power User", "User", "New User", "Password Reset"]
status = ["Active", "Inactive"]
priority = ["Low", "Medium", "High"]
ticketStatus = ["No Status", "In Progress", "In Pause", "Terminated", "Archived"]
email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'






# index route
@app.route("/", methods=["GET", "POST"])
def index():
    # get user session user id
    userID = session.get("user_id")
    # get user permission value
    permission = session.get("permission")
    # permission = db.execute("SELECT permission FROM users WHERE id = ?", userID)
    # if userID is none go to login
    if userID is None:
        return render_template("index.html")
    # if userID in = 1 (admin) check for new users
    elif permission == 4:
        flash("Waiting for admin aproval")
        return render_template("index.html")
    elif permission == 5:
        return redirect("/profile")
    elif permission <  2:
        return redirect("/checkuser")



    # if login up go to links
    return redirect("/tickets")

@app.route("/checkuser", methods=["GET", "POST"])
def checkuser():
    if request.method == "POST":
        # do page to see new users and button to activate
        # get link ID
        userID = request.form.get("id")

        if userID:
            db.execute("UPDATE users SET permission = 3 WHERE id = ?", userID)
            user = db.execute("SELECT * FROM users WHERE id = ?", userID)

            name = user[0]["name"]
            email = user[0]["email"]

            text = "Hello " + name + "\nYour Registration has been aproved.\nLink: http://google.pt\nWelcome!"
            email_alert.email_alert("Help Desk Project CS50 - Aproval", text, email)
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

    # if post method
    if request.method == "POST":

        # get variables
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        pConfirmation = request.form.get("pConfirmation")

        
        
        if not re.match(email_pattern, email):
            flash("Have to register with a valid email!")
            return render_template("register.html")




        # variable validation
        if not email:
            flash("No email!")
            return render_template("register.html")
        if not name:
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

        # try to add to database if cant add becouse email already exists

        
        
        try:
            db.execute(
                "INSERT INTO users (email, hash, name) VALUES(?, ?, ?)", email, pHash, name
                )

            # remember user login and redirect to links

        except:

            # return to register and show message
            flash("Email already taken")
            return render_template("register.html")
        
        # send email to new user
        text = "Hello " + name + "\nYou have complete registration on Help Desk Project CS50.\nLink: http://www.google.pt\nWait for admin Aproval."
        email_alert.email_alert("Help Desk Project CS50 - Registration", text, email)
        
        # send email to admins
        text = "Email: " + email + "\nName:  " + name
        #push_alert.message("New USER", text)

        admins = db.execute("SELECT email FROM users WHERE permission < 2")

        for admin in admins:
            print(admin["email"])
            email_admin = admin["email"]
            email_alert.email_alert("Help Desk Project CS50 - New User", text, email_admin)

        return redirect("/")

    # if get method
    return render_template("register.html")

# login function
@app.route("/login", methods=["GET", "POST"])
def login():

    # if post method
    if request.method == "POST":

        # get variables
        email = request.form.get("email")
        password = request.form.get("password")

        # variables validation
        if not email:
            flash("No Email!")
            return render_template("index.html")
        elif not password:
            flash("No Password!")
            return render_template("index.html")

        # get database line where email
        rows = db.execute(
        "SELECT * FROM users WHERE email = ?", email)

        if not rows:
            flash("Invalid Email and/or Password")
            return render_template("index.html")

        if rows[0]["active"] == 1:
            flash("User not Active, call admin")
            return render_template("index.html")

        # if password not check or email
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):

            # return to login and show message
            flash("Invalid Email and/or password")
            return render_template("index.html")

        # remember user login and redirect to links
        session["user_id"] = rows[0]["id"]
        session["permission"] = rows[0]["permission"]

        return redirect("/")

    # if get method
    return render_template("login.html")





# logout function
@app.route("/logout")
def logout():

    # forget user and redirect to index
    session.clear()
    return redirect("/")

# change function
@app.route("/profile", methods=["GET", "POST"])
def password():
    userID = session.get("user_id")
    user = db.execute("SELECT * FROM users WHERE id = ?", userID)
    # if post method
    if request.method == "POST":

        # get VALUES
        pOld = request.form.get("pOld")
        password = request.form.get("password")
        pConfirmation = request.form.get("pConfirmation")
        name = request.form.get("name")

        # variable validation
        if not name and not pOld and not password and not pConfirmation:
            flash("No information changed")
            return redirect("/profile")
        
        if name:
            flash("Name Changed!")
            db.execute("UPDATE users SET name = ? WHERE id = ?", name, userID)

        
        
        if pOld and password and pConfirmation:
             # get user ID and data from db

            if len(password) != 8:
                flash("Password must have 8 Chars or more")
                return redirect("/profile")
        
            dbPass = db.execute("SELECT hash FROM users WHERE id = ?", userID)[0]["hash"]

            # check if old password in corret
            if password == pConfirmation:
                if  check_password_hash(dbPass, pOld):
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
def users():

    # get serssion id
    userID = session.get("user_id")

    # get info from database and render in links
    users = db.execute("SELECT * FROM users WHERE id > 1 AND id != ?", userID)

    
    

    return render_template("users.html", users = users, role = role, status = status)

# EDIT USER
@app.route("/edituser", methods=["GET", "POST"])
def edituser():

    if request.method == "POST":
        # get link id
        userID = request.form.get("id")

        session["edit_user"] = userID
        # get info from database and render in links
        user = db.execute("SELECT * FROM users WHERE id = ?", userID)
        return render_template("edituser.html", user = user, role = role)

    userID = session["edit_user"]
    user = db.execute("SELECT * FROM users WHERE id = ?", userID)
    return render_template("edituser.html", user = user, role = role)

# DEACTIVATE USER
@app.route("/deactivateuser", methods=["GET", "POST"])
def deactivateuser():

    if request.method == "POST":

        # get link ID
        userID = session["edit_user"]

        if userID:
            db.execute("UPDATE users SET active = 1 WHERE id = ?", userID)

            return redirect("/edituser")
        else:
            flash("Error ocurred!")
            return redirect("/users")

# ACTIVATE USER
@app.route("/activateuser", methods=["GET", "POST"])
def activateuser():

    if request.method == "POST":

        # get link ID
        userID = session["edit_user"]

        if userID:
            db.execute("UPDATE users SET active = 0 WHERE id = ?", userID)

            return redirect("/edituser")
        else:
            flash("Error ocurred!")
            return redirect("/users")

# CHANGE VALUES USER
@app.route("/changeuser", methods=["GET", "POST"])
def changeuser():

    if request.method == "POST":
        userID = session["edit_user"]
        permission = request.form.get("permission")

        if not permission:
            flash("Must Select a permission")
            return redirect("/edituser")

        if userID:
            db.execute("UPDATE users SET permission = ? WHERE id = ?", permission, userID)

            return redirect("/edituser")
        else:
            flash("Error ocurred!")
            return redirect("/users")



# DELETE USER
@app.route("/deleteuser", methods=["GET", "POST"])
def deleteuser():

    if request.method == "POST":

        userID = session["edit_user"]

        if userID:
            db.execute("DELETE FROM users WHERE id = ?", userID)
            flash("USER is DELETED")
            return redirect("/users")
        else:
            flash("Error ocurred!")
            return redirect("/edituser")
        

# RESET PASSWORD USER
@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():

    if request.method == "POST":

        # try to get link ID
        try:
            userID = session["edit_user"]
        # if can get its a Forgot password situation
        except:
            email = request.form.get("email")

            if not re.match(email_pattern, email):
                flash("Input a valid email!")
                return redirect("/resetpassword")

            password = passgenerator.get_random_string()
            hash = generate_password_hash(password)
            
            # alterar estado permission to 5
            # alterar password
            try:
                db.execute("UPDATE users SET hash = ?, permission = 5 WHERE email = ?", hash, email)
                
            except:
                return redirect("/")


            # enviar email com nova password
            user = db.execute('SELECT * FROM users WHERE email = ?', email)
            name = user[0]['name']
            text = "Hello " + name + "\nYour password has been reseted.\nNew Password: " + password
            email_alert.email_alert("Help Desk Project CS50 - Password Reset", text, email)
            # return users
            return redirect("/")


        # admin reset password 
        password = passgenerator.get_random_string()
        print(password)
        hash = generate_password_hash(password)
        print(hash)
            
        # alterar estado permission to 5
        # alterar password
        db.execute("UPDATE users SET hash = ?, permission = 5 WHERE id = ?", hash, userID)


        # enviar email com nova password
        user = db.execute('SELECT * FROM users WHERE id = ?', userID)
        email = user[0]['email']
        name = user[0]['name']
        text = "Hello " + name + "\nYour password has been reseted.\nNew Password: " + password
        email_alert.email_alert("Help Desk Project CS50 - Password Reset", text, email)
        # return users
        return redirect("/users")
            
    
    return render_template("getemail.html")
        

# tickets
@app.route("/tickets", methods=["GET", "POST"])
def tickets():

    

    if request.method == "POST":
        status = request.form.get("status")
        if status == "reset":
            return redirect("/tickets")

        # tickets = db.execute("SELECT * FROM tickets WHERE status = ? ORDER BY priority DESC, time ASC", status)


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


    if session.get("permission") < 3:

        tickets = db.execute(
            """
            SELECT tickets.id, tickets.subject, tickets.status, tickets.priority,
            users.name AS creator_name FROM tickets
            LEFT JOIN users ON tickets.creator = users.id
            WHERE tickets.status < 4 ORDER BY priority DESC, time ASC
            """
            )
        return render_template("tickets.html", tickets = tickets, status = ticketStatus, priority = priority)
    else:
        userID = session.get("user_id")
        tickets = db.execute(
            """
            SELECT tickets.id, tickets.subject, tickets.status, tickets.priority,
            users.name AS creator_name FROM tickets
            LEFT JOIN users ON tickets.creator = users.id
            WHERE tickets.status < 4 AND users.id = ? ORDER BY priority DESC, time ASC
            """
            , userID
            )
        
        return render_template("tickets.html", tickets = tickets, status = ticketStatus, priority = priority)


# add tickets
@app.route("/newticket", methods=["GET", "POST"])
def newticket():

    

    if request.method == "POST":
        userID = session.get("user_id")

        # get variables
        subject = request.form.get("subject")
        problem = request.form.get("problem")
        priority = request.form.get("priority")

        # variable validation
        if not subject:
            flash("No subject!")
            return render_template("newticket.html")
        if not problem:
            flash("No problem!")
            return render_template("newticket.html")
        elif not priority:
            flash("No priority!")
            return render_template("newticket.html")
        

        # add to links database
        db.execute(
            "INSERT INTO tickets (subject, description, priority, creator) VALUES(?, ?, ?, ?)",
            subject, problem, priority, userID
        )

        name = db.execute("SELECT name FROM users WHERE id = ?", userID)

        text = "Subject: " + subject + "\nFrom: " + name[0]["name"] + "\nPriority: " + priority + "\nDescription: " + problem

        #push_alert.message("New Ticket", text)
        email_alert.email_alert("New User", text, "vyrustr@gmail.com")
        return redirect("/tickets")

    return render_template("newticket.html")

@app.route("/showticket", methods=["GET", "POST"])
def showticket():

    if request.method == "POST":
        # get link id
        ticketID = request.form.get("id")

        session["show_ticket"] = ticketID

        ticket = db.execute("SELECT tickets.id, tickets.subject, tickets.description, tickets.status, tickets.priority, tickets.time, tickets.creator, users.name AS creator_name FROM tickets LEFT JOIN users ON tickets.creator = users.id WHERE tickets.id = ?", ticketID)
        #solutions = db.execute("SELECT solutions.id, solutions.subject, solutions.category, solutions.time, users.name AS creator_name FROM solutions LEFT JOIN users ON solutions.creator = users.id ORDER BY category, subject")
        solutions = db.execute(
            """
            SELECT s.*, u.name AS creator_name
            FROM solutions s
            JOIN interchange i ON s.id = i.solution_id
            JOIN tickets t ON t.id = i.ticket_id
            JOIN users u ON s.creator = u.id
            WHERE t.id = ?;
            """,
            ticketID)
        
        answers = db.execute(
        """
        SELECT answers.ticket_id, answers.answer, answers.time, users.name AS creator_name
        FROM answers LEFT JOIN users ON answers.creator = users.id
        WHERE ticket_id = ?
        """,
        ticketID
    )
        print(answers)
        return render_template("showticket.html", ticket = ticket, priority = priority, status = ticketStatus, solutions = solutions, answers = answers)

    # get link id
    ticketID = session["show_ticket"]

    session["show_ticket"] = ticketID
    ticket = db.execute("SELECT tickets.id, tickets.subject, tickets.description, tickets.status, tickets.priority, tickets.time, tickets.creator, users.name AS creator_name FROM tickets LEFT JOIN users ON tickets.creator = users.id WHERE tickets.id = ?", ticketID)
    #solutions = db.execute("SELECT solutions.id, solutions.subject, solutions.category, solutions.time, users.name AS creator_name FROM solutions LEFT JOIN users ON solutions.creator = users.id ORDER BY category, subject")
    solutions = db.execute("SELECT s.* FROM solutions s JOIN interchange i ON s.id = i.solution_id JOIN tickets t ON t.id = i.ticket_id WHERE t.id = ?", ticketID)
    answers = db.execute(
        """
        SELECT answers.ticket_id, answers.answer, answers.time, users.name AS creator_name
        FROM answers LEFT JOIN users ON answers.creator = users.id
        WHERE ticket_id = ?
        """,
        ticketID
    )
    print(answers)
    return render_template("showticket.html", ticket = ticket, priority = priority, status = ticketStatus, solutions = solutions, answers = answers)

@app.route("/saveticket", methods=["GET", "POST"])
def saveticket():

    if request.method == "POST":
        status = request.form.get("status")
        ticketID = session["show_ticket"]

        db.execute("UPDATE tickets SET status = ? WHERE id = ?", status, ticketID)
        return redirect("/showticket")
    
@app.route("/archiveticket", methods=["GET", "POST"])
def archiveticket():

    if request.method == "POST":
        status = request.form.get("status")
        ticketID = session["show_ticket"]

        db.execute("UPDATE tickets SET status = ? WHERE id = ?", status, ticketID)
        return redirect("/tickets")
    

@app.route("/solutions", methods=["GET", "POST"])
def solutions():

    listcategories = db.execute("SELECT DISTINCT category FROM solutions ORDER BY category")

    if request.method == "POST":
        category = request.form.get("category")
        if category == "reset":
            return redirect("/solutions")

        solutions = db.execute("SELECT solutions.id, solutions.subject, solutions.category, solutions.time, users.name AS creator_name FROM solutions LEFT JOIN users ON solutions.creator = users.id WHERE category = ? ORDER BY subject", category)
        categories = db.execute("SELECT DISTINCT category FROM solutions WHERE category = ?", category)


        return render_template("solutions.html", solutions = solutions, categories = categories, list = listcategories)




    solutions = db.execute("SELECT solutions.id, solutions.subject, solutions.category, solutions.time, users.name AS creator_name FROM solutions LEFT JOIN users ON solutions.creator = users.id ORDER BY subject;")
    categories = listcategories
    return render_template("solutions.html", solutions = solutions, categories = categories, list = listcategories)

@app.route("/newsolution", methods=["GET", "POST"])
def newsolution():

    # if post method
    if request.method == "POST":

        # get variables
        if request.form.get("category") == "newcategory":
            category = request.form.get("addcategory")
        else:
            category = request.form.get("category")
        
        subject = request.form.get("subject")
        description = request.form.get("description")

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

@app.route("/showsolution", methods=["GET", "POST"])
def showsolution():

    if request.method == "POST":
        # get link id
        solutionID = request.form.get("id")

        session["show_solution"] = solutionID

        #ticket = db.execute("SELECT tickets.id, tickets.subject, tickets.description, tickets.status, tickets.priority, tickets.time, users.name AS creator_name FROM tickets LEFT JOIN users ON tickets.creator = users.id WHERE tickets.id = ?", ticketID)
        solution = db.execute("SELECT solutions.id, solutions.subject, solutions.category, solutions.description, solutions.time, solutions.creator, users.name AS creator_name FROM solutions LEFT JOIN users ON solutions.creator = users.id WHERE solutions.id = ?", solutionID)
        print(solution)
        return render_template("showsolution.html", solution = solution)

    # get link id
    solutionID = session["show_solution"]

    session["show_solution"] = solutionID

    #ticket = db.execute("SELECT tickets.id, tickets.subject, tickets.description, tickets.status, tickets.priority, tickets.time, users.name AS creator_name FROM tickets LEFT JOIN users ON tickets.creator = users.id WHERE tickets.id = ?", ticketID)
    solution = db.execute("SELECT solutions.id, solutions.subject, solutions.category, solutions.description, solutions.time, solutions.creator, users.name AS creator_name FROM solutions LEFT JOIN users ON solutions.creator = users.id WHERE solutions.id = ?", solutionID)
    print(solution)

    return render_template("showsolution.html", solution = solution)

@app.route("/newsolutiontoticket", methods=["GET", "POST"])
def newsolutiontoticket():

    # if post method
    if request.method == "POST":

        # get variables
        if request.form.get("category") == "newcategory":
            category = request.form.get("addcategory")
        else:
            category = request.form.get("category")
        
        subject = request.form.get("subject")
        description = request.form.get("description")
        ticketID = session["show_ticket"]

        # check variables
        if not subject or not category or not description:
            flash("information required!")
            return redirect("/newsolution")

        # get user id
        userID = session["user_id"]











        print("NEW SOLUTUTION TO TICKET")

        # add to links database
        db.execute(
            "INSERT INTO solutions (category, subject, description, creator) VALUES(?, ?, ?, ?)",
            category, subject, description, userID
        )

        solutionID = db.execute("SELECT id FROM solutions ORDER BY id DESC LIMIT 1")
        print(solutionID)

        db.execute(
            "INSERT INTO interchange (solution_id, ticket_id) VALUES(?, ?)", solutionID[0]["id"], ticketID

        )

        return redirect("/showticket")

    #inserir ticket id then in page solutions if ticket id fazer newsolutionstoticket
    ticketID = session["show_ticket"]
    print(ticketID)
    categories = db.execute("SELECT DISTINCT category FROM solutions ORDER BY category")
    return render_template("newsolutiontoticket.html", categories = categories, ticketID = ticketID)


# add tickets
@app.route("/newanswer", methods=["GET", "POST"])
def newanswer():

    

    if request.method == "POST":
        userID = session.get("user_id")
        ticketID = session.get("show_ticket")

        # get variables
        answer = request.form.get("answer")

        # variable validation
        if not answer:
            return redirect("/showticket")
        

        # add to links database
        db.execute(
            "INSERT INTO answers (ticket_id, creator, answer) VALUES(?, ?, ?)",
            ticketID, userID, answer
        )

        return redirect("/showticket")
    
@app.route("/deleteticket", methods=['GET', 'POST'])
def deleteticket():
    if request.method == 'POST':
        ticketID = request.form.get('ticketID')
        print(ticketID)

        db.execute("DELETE FROM tickets WHERE id = ?", ticketID)
        return redirect('/tickets')
    
@app.route("/deletesolution", methods=['GET', 'POST'])
def deletesolution():
    if request.method == 'POST':
        solutionID = request.form.get('solutionID')
        print(solutionID)

        db.execute("DELETE FROM solutions WHERE id = ?", solutionID)
        return redirect('/solutions')