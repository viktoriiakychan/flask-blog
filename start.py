from flask import Flask, render_template, redirect, request, flash, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml, os
from flask_login import LoginManager, login_required, logout_user 


app = Flask(__name__)
login_manager = LoginManager(app)
Bootstrap(app)

db = yaml.safe_load(open("settings.yaml"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["SECRET_KEY"] = os.urandom(24)
mysql = MySQL(app)

@login_manager.user_loader

@app.route("/")
def index():
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM posts")
    if result > 0:
        posts = cursor.fetchall()
        print(f"fetch posts: {posts}")
        cursor.close()
        return render_template("index.html", posts=posts)
    return render_template("index.html", posts=None)
    

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/post/<int:id>")
def posts(id):
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM posts WHERE id= %s", ([id]))
    post = cursor.fetchall()
    print(f"fetch posts: {post}")
    return render_template("post.html", post=post[0])

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_details = request.form
        cursor = mysql.connection.cursor()
        
        
        user_by_username = cursor.execute("SELECT * FROM users WHERE username = %s", ([user_details["username"]]))
        user_by_email = cursor.execute("SELECT * FROM users WHERE email = %s", ([user_details["email"]]))
       
        if not user_details["first_name"]: flash("Enter first name!", "danger")
        elif not user_details["last_name"]: flash("Enter last name!", "danger")
        elif not user_details["username"]: flash("Enter username!", "danger")
        elif not user_details["email"]: flash("Enter email!", "danger")
        elif not user_details["password"]: flash("Enter password!", "danger")
        elif not user_details["confirm_password"]: flash("Enter password confirmation!", "danger")
        elif user_by_username > 0:
            flash("This username is already taken", "danger")
            return redirect("/register")
        elif user_by_email > 0:
            flash("This email is already taken", "danger")
            return redirect("/register")    
        elif user_details["password"] != user_details["confirm_password"]:
            flash("Passwords do not match!", "danger")
            return redirect("/register")
        else:
            cursor.execute("INSERT INTO users(id, first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s, %s)",("", user_details['first_name'], user_details['last_name'], user_details['username'], user_details['email'], generate_password_hash(user_details['password'])))
            cursor.connection.commit()
            cursor.close()
            flash("You were successefully registered", "success")
            return redirect("/login")
    
    return render_template("register.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_details = request.form
        username = user_details["username"]
        cursor = mysql.connection.cursor()
        result = cursor.execute("SELECT * FROM users WHERE username = %s", ([username]))
        if result > 0:
            user = cursor.fetchone()
            if check_password_hash(user['password'], user_details['password']):
                session['login'] = True
                session['first_name'] = user['first_name']
                session['last_name'] = user['last_name']
            else: 
                cursor.close()
                flash("Username or password is incorrect!", "danger")
                return redirect("/login")
        cursor.close()
        session['username'] = username
        return redirect('/')
    return render_template("login.html")

@app.route("/logout/")
def logout():
    session.clear()
    return redirect("/")

@app.route("/new-post/", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        post_details = request.form
        cursor = mysql.connection.cursor()
        print(session['username'])
        if not post_details["title"]: flash("Enter title!", "danger")
        elif not post_details["description"]: flash("Enter description!", "danger")
        elif not post_details["text"]: flash("Enter text!", "danger")
        else:
            cursor.execute("INSERT INTO posts(id, title, description, text) VALUES (%s, %s, %s, %s)",("", post_details['title'], post_details['description'], post_details['text']))
            cursor.connection.commit()
            cursor.close()
            flash("You successefully created a new post", "success")
            return redirect("/")

    return render_template("new_post.html")

@app.route("/edit-post/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    return render_template("edit_post.html", post=id)

@app.route("/delete-post/<int:id>")
def delete_post(id):
    # return render_template("delete_post.html", post=id)
    return redirect("/my-posts/")

@app.route("/my-posts/")
def my_posts():
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM posts")
    if result > 0:
        posts = cursor.fetchall()
        print(f"fetch posts: {posts}")
        cursor.close()
        return render_template("my_posts.html", posts=posts)
    return render_template("my_posts.html", posts=None)



if __name__ == "__main__":
    app.run(debug=True)