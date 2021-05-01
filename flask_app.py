from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_required, login_user, LoginManager, logout_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="acis668",
    password="Test1234!",
    hostname="acis668.mysql.pythonanywhere-services.com",
    databasename="acis668$gradebookDB",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = "something random"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):

    def __init__(self, username, password_hash, numID):
        self.username = username
        self.password_hash = password_hash
        self.numID = numID

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

    def get_num(self):
        return self.numID

all_users = {
    "admin": User("admin", generate_password_hash("secret"), 1)
}


@login_manager.user_loader
def load_user(user_id):
    return all_users.get(user_id)


class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    posted = db.Column(db.DateTime, default=datetime.now)
    username = db.Column(db.String(4096))
    userID = db.Column(db.Integer)



@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=Comment.query.all(), user=User)

    comment = Comment(content=request.form["contents"], username=session['username'], userID=session['user-id'])
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))



@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    username = request.form["username"]
    session['username'] = username
    if username not in all_users:
        return render_template("login_page.html", error=True)
    user = all_users[username]
    session['user-id'] = user.numID

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))