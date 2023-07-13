from flask import Flask, render_template, redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml, os

app = Flask(__name__)
Bootstrap(app)

db = yaml.safe_load(open("settings.yaml"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["SECRET_KEY"] = os.urandom(24)
mysql = MySQL(app)

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

@app.route("/posts/<int:id>")
def posts(id):
    return render_template("posts.html", post=id)

@app.route("/register/", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/new-post/", methods=["GET", "POST"])
def new_post():
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

@app.route("/logout/")
def logout():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)