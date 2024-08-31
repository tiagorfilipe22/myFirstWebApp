from cs50 import SQL
from flask import Flask, render_template, request, redirect, flash, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "helothisisawensite99"

# session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set variable to database
db = SQL("sqlite:///data.db")

# set variable to csv to log add links and delete links

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
        flash("Your Password is Reseted")
        return render_template("resetpassword.html")
    elif permission <  2:
        return redirect("/checkuser")



    # if login up go to links
    return redirect("/links")

@app.route("/checkuser", methods=["GET", "POST"])
def checkuser():
    if request.method == "POST":
        # do page to see new users and button to activate
        # get link ID
        userID = request.form.get("id")

        if userID:
            db.execute("UPDATE users SET permission = 3 WHERE id = ?", userID)

            return redirect("/checkuser")
    # check for new registered USERS
    # get info from database and render in links
    users = db.execute("SELECT * FROM users WHERE permission = 4 AND id > 1")
    print(users)
    if users:
        return render_template("checkuser.html", users = users)
    else:
        return redirect("/links")



# register function
@app.route("/register", methods=["GET", "POST"])
def register():

    # if post method
    if request.method == "POST":

        # get variables
        username = request.form.get("username")
        password = request.form.get("password")
        pConfirmation = request.form.get("pConfirmation")

        # variable validation
        if not username:
            flash("No Username!")
            return render_template("register.html")
        elif not password:
            flash("No Password!")
            return render_template("register.html")
        elif not pConfirmation:
            flash("You have to confirm the password!")
            return render_template("register.html")
        elif password != pConfirmation:
            flash("Passwords don't match!")
            return render_template("register.html")

        # generate hash from password
        pHash = generate_password_hash(password)

        # try to add to database if cant add becouse username already exists
        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)", username, pHash
            )

            # remember user login and redirect to links
            return redirect("/")

        except:

            # return to register and show message
            flash("Username already taken")
            return render_template("register.html")

    # if get method
    return render_template("register.html")

# login function
@app.route("/login", methods=["GET", "POST"])
def login():

    # if post method
    if request.method == "POST":

        # get variables
        username = request.form.get("username")
        password = request.form.get("password")

        # variables validation
        if not username:
            flash("No Username!")
            return render_template("index.html")
        elif not password:
            flash("No Password!")
            return render_template("index.html")

        # get database line where username
        rows = db.execute(
        "SELECT * FROM users WHERE username = ?", username
        )

        if rows[0]["active"] == 1:
            flash("User not Active, call admin")
            return render_template("index.html")

        # if password not check or username
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):

            # return to login and show message
            flash("Invalid username and/or password")
            return render_template("index.html")

        # remember user login and redirect to links
        session["user_id"] = rows[0]["id"]
        session["permission"] = rows[0]["permission"]

        return redirect("/")

    # if get method
    return render_template("login.html")

# add function
@app.route("/add", methods=["GET", "POST"])
def add():

    # if post method
    if request.method == "POST":

        # get variables
        type = request.form.get("type")
        name = request.form.get("name")
        link = request.form.get("link")

        # check variables
        if not name or not type or not link:
            flash("information required!")
            return render_template("add.html")

        # get user id
        userID = session["user_id"]

        # add to links database
        db.execute(
            "INSERT INTO links (type, name, link) VALUES(?, ?, ?)",
            type, name, link
        )

        # get last ID
        linkID = db.execute("SELECT id FROM links ORDER BY id DESC LIMIT 1")

        # add to links database
        # db.execute(
        #    "INSERT INTO logs (user_id, link_id, type) VALUES(?, ?, ?)",
        #    userID, linkID[0]["id"], "add"
        #)


        # redirect to links
        return redirect("/links")

    # if get method
    return render_template("add.html")

# links function
@app.route("/links")
def links():

    # get serssion id
    userID = session["user_id"]

    # select user from db
    rows = db.execute(
    "SELECT * FROM users WHERE id = ?", userID
    )

    # get username
    username = rows[0]["username"]

    # get info from database and render in links
    links = db.execute("SELECT type, name, link, id FROM links WHERE active = 0")
    return render_template("links.html", links = links, username = username)

# logout function
@app.route("/logout")
def logout():

    # forget user and redirect to index
    session.clear()
    return redirect("/")

# change function
@app.route("/password", methods=["GET", "POST"])
def password():
    # if post method
    if request.method == "POST":

        # get VALUES
        pOld = request.form.get("pOld")
        password = request.form.get("password")
        pConfirmation = request.form.get("pConfirmation")

        # variable validation
        if not pOld:
            flash("Have to insert old Password")
            return render_template("change.html")
        elif not password:
            flash("No New Password!")
            return render_template("change.html")
        elif not pConfirmation:
            flash("You have to confirm the password!")
            return render_template("change.html")
        elif password != pConfirmation:
            flash("Passwords don't match!")
            return render_template("change.html")

        # get user ID and data from db
        userID = session.get("user_id")
        dbPass = db.execute("SELECT hash FROM users WHERE id = ?", userID)[0]["hash"]

        # check if old password in corret
        if check_password_hash(dbPass, pOld):
            new = generate_password_hash(password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", new, userID)
            flash("You have changed Password!")
            return render_template("change.html")
        else:
            flash("Provided Old Password not match!")
            return render_template("change.html")

    # if get method
    return render_template("change.html")






@app.route("/edit", methods=["GET", "POST"])
def edit():

    if request.method == "POST":
        # get link id
        linkID = request.form.get("id")

        # get info from database and render in links
        links = db.execute("SELECT type, name, link, id FROM links WHERE id = ?", linkID)
        return render_template("edit.html", links = links)

@app.route("/delete", methods=["GET", "POST"])
def delete():

    if request.method == "POST":
        # get serssion id
        userID = session["user_id"]

        # get link ID
        linkID = request.form.get("id")

        if linkID:
            db.execute("UPDATE links SET active = 1 WHERE id = ?", linkID)


            # add to links database
            # db.execute(
            #    "INSERT INTO logs (user_id, link_id, type) VALUES(?, ?, ?)",
            #    userID, linkID, "delete"
            # )
            return redirect("/")
        else:
            return redirect("/")

@app.route("/change", methods=["GET", "POST"])
def change():

    if request.method == "POST":
        return redirect("/")


# hisotry function
# @app.route("/history")
# def history():

    # get serssion id
    # userID = session["user_id"]

    # get info from database and render in links
    # logs = db.execute("SELECT users.username, links.name, logs.type, logs.comment, logs.time FROM logs JOIN users ON logs.user_id = users.id JOIN links ON logs.link_id = links.id")
    # print(logs)
    # return render_template("history.html", logs = logs)

# users function
@app.route("/users")
def users():

    # get serssion id
    userID = session["user_id"]

    # get info from database and render in links
    users = db.execute("SELECT * FROM users WHERE id > 1")
    return render_template("users.html", users = users)

@app.route("/edituser", methods=["GET", "POST"])
def edituser():

    if request.method == "POST":
        # get link id
        userID = request.form.get("id")

        session["edit_user"] = userID
        # get info from database and render in links
        user = db.execute("SELECT username, permission, active, id FROM users WHERE id = ?", userID)
        return render_template("edituser.html", user = user)

    userID = session["edit_user"]
    user = db.execute("SELECT username, permission, active, id FROM users WHERE id = ?", userID)
    return render_template("edituser.html", user = user)

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

@app.route("/resetstatus", methods=["GET", "POST"])
def resetpassword():

    if request.method == "POST":

        userID = session["edit_user"]


        if userID:
            db.execute("UPDATE users SET permission = 5 WHERE id = ?", userID)
            flash("Password now Reset")
            return redirect("/edituser")
        else:
            flash("Error ocurred!")
            return redirect("/users")
