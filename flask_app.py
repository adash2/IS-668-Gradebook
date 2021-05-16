from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_required, login_user, LoginManager, logout_user, UserMixin
from datetime import timedelta
from werkzeug.security import check_password_hash, generate_password_hash


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
    "admin": User("admin", generate_password_hash("secret"), 1),
    "testUser": User("testUser", generate_password_hash("is668"), 2)
}


@login_manager.user_loader
def load_user(user_id):
    return all_users.get(user_id)


class Students(db.Model):

    __tablename__ = "students"

    s_id = db.Column(db.Integer, primary_key=True)
    s_last_name = db.Column(db.String(120))
    s_first_name = db.Column(db.String(120))
    s_major = db.Column(db.String(45))
    s_email = db.Column(db.String(120))

class Class(db.Model):

    __tablename__ = "class"

    c_id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(45))
    c_prof = db.Column(db.String(120))

class StudentClass(db.Model):

    __tablename__ = "studentClass"

    s_id = db.Column(db.Integer, db.ForeignKey('students.s_id'), primary_key=True)
    c_id = db.Column(db.Integer, db.ForeignKey('class.c_id'), primary_key=True)

class Assignment(db.Model):

    __tablename__ = "assignment"

    a_id = db.Column(db.Integer, primary_key=True)
    a_name = db.Column(db.String(120))
    a_grade = db.Column(db.Float())
    s_id = db.Column(db.Integer, db.ForeignKey('studentClass.s_id'))
    c_id = db.Column(db.Integer, db.ForeignKey('studentClass.c_id'))

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

@app.route("/class/", methods=["GET", "POST"])
def viewAddClass():
    if request.method == "GET":
        return render_template("class_page.html", classList=Class.query.all(), user=User)

    newClass = Class(c_name=request.form["c_name"], c_prof=request.form["c_prof"])
    db.session.add(newClass)
    db.session.commit()
    return redirect(url_for('viewAddClass'))

@app.route("/assignment/", methods=["GET", "POST"])
def viewAddAssignment():
    assignmentInfo = db.session.query(Class, Students, Assignment).filter(Assignment.c_id == Class.c_id).filter(Assignment.s_id == Students.s_id)
    multiJoin = db.session.query(Class, Students, StudentClass).filter(Class.c_id == StudentClass.c_id).filter(Students.s_id == StudentClass.s_id)
    if request.method == "GET":
        return render_template("assignment_page.html", classList=multiJoin.all(), assignmentInfo=assignmentInfo.all(), user=User)

    id = request.form["studentID"].split(',')
    newAssignment = Assignment(a_name=request.form["a_name"], a_grade=request.form["a_grade"], s_id=id[0], c_id=id[1])
    db.session.add(newAssignment)
    db.session.commit()
    return redirect(url_for('viewAddAssignment'))

@app.route("/deleteAssignment/", methods=["GET", "POST"])
def deleteAssignment():
    assignmentInfo = db.session.query(Class, Students, Assignment).filter(Assignment.c_id == Class.c_id).filter(Assignment.s_id == Students.s_id)
    if request.method == "GET":
        return render_template("delete_assignment_page.html", assignmentInfo=assignmentInfo.all(), user=User)

    Assignment.query.filter_by(a_id=request.form["a_id"]).delete()
    db.session.commit()
    return redirect(url_for('deleteAssignment'))

@app.route("/editAssignment/", methods=["GET", "POST"])
def editAssignment():
    assignmentInfo = db.session.query(Class, Students, Assignment).filter(Assignment.c_id == Class.c_id).filter(Assignment.s_id == Students.s_id)
    if request.method == "GET":
        return render_template("edit_assignment_page.html", assignments=Assignment.query.all(), assignmentInfo=assignmentInfo.all(), user=User)

    Assignment.query.filter_by(a_id=request.form["a_id"]).first().a_grade = request.form["new_grade"]
    db.session.commit()
    return redirect(url_for('editAssignment'))

@app.route("/studentAggregate/", methods=["GET", "POST"])
def studentAggregate():
    if request.method == "GET":
        return render_template("student_aggregate_page.html", students=Students.query.all(), user=User)

    if request.method == "POST":
        selectedStudent = request.form["s_id"]
        studentAssignments = Assignment.query.with_entities(Assignment.a_grade).filter(Assignment.s_id==selectedStudent)
        studentName = Students.query.filter(Students.s_id==selectedStudent)
        total = 0;
        assignmentCount = studentAssignments.count()
        if(assignmentCount>0):
            for grade in studentAssignments.all():
                total = total + grade.a_grade
        else:
            return render_template("student_aggregate_page.html", avg=-1, studentName=studentName.first(), user=User)
        avg = total/assignmentCount
        return render_template("student_aggregate_page.html", avg=avg, studentName=studentName.first(), user=User)

    return redirect(url_for('studentAggregate'))

@app.route("/chooseStudentForAggregate/", methods=["GET", "POST"])
def chooseStudentForAggregate():
    selectedStudent = request.form["s_id"]
    studentAssignments = Assignment.query.with_entities(Assignment.a_grade).filter(Assignment.s_id==selectedStudent)
    total = 0;
    assignmentCount = studentAssignments.count()
    if(assignmentCount>0):
        for grade in studentAssignments.all():
            total = total + grade.a_grade
    else:
        return render_template("student_aggregate_page.html", avg=-1, user=User)

    avg = total/assignmentCount

    return render_template("student_aggregate_page.html", avg=avg, user=User)

@app.route("/addStudentToClass/", methods=["GET", "POST"])
def addStudentToClass():
    if request.method == "GET":
        return render_template("add_studentClass_page.html", students=Students.query.all(), user=User)

    if request.method == "POST":
        studentClass = request.form["studentClass"].split(',')
        newStudentClass = StudentClass(s_id=studentClass[1], c_id=studentClass[0])
        db.session.add(newStudentClass)
        db.session.commit()

    return redirect(url_for('addStudentToClass'))

@app.route("/chooseStudentForClass/", methods=["GET", "POST"])
def chooseStudentForClass():
    selectedStudent = request.form["s_id"]
    subquery = StudentClass.query.with_entities(StudentClass.c_id).filter(StudentClass.s_id==selectedStudent)
    if(subquery.count()>0):
        query = Class.query.filter(Class.c_id.notin_(subquery))
    else:
        query = Class.query
    multiJoin = db.session.query(Class, Students, StudentClass).filter(Class.c_id == StudentClass.c_id).filter(Students.s_id == StudentClass.s_id).filter(Students.s_id==selectedStudent)

    return render_template("add_studentClass_page.html", students=Students.query.all(), availableClasses=query.all(), selectedStudent=multiJoin.all(), studentId=selectedStudent, user=User)

@app.route("/removeStudentFromClass/", methods=["GET", "POST"])
def removeStudentFromClass():
    if request.method == "GET":
        return render_template("remove_studentClass_page.html", students=Students.query.all(), user=User)

    if request.method == "POST":
        studentClass = request.form["studentClass"].split(',')
        StudentClass.query.filter(StudentClass.c_id==studentClass[0]).filter(StudentClass.s_id==studentClass[1]).delete()
        db.session.commit()

    return redirect(url_for('removeStudentFromClass'))

@app.route("/chooseStudentForRemovingClass/", methods=["GET", "POST"])
def chooseStudentForRemovingClass():
    selectedStudent = request.form["s_id"]
    subquery = StudentClass.query.with_entities(StudentClass.c_id).filter(StudentClass.s_id==selectedStudent)
    assignmentQuery = Assignment.query.with_entities(Assignment.c_id).filter(Assignment.s_id == selectedStudent).distinct()
    studentID = Students.query.filter(Students.s_id==selectedStudent)
    multiJoin = db.session.query(Class, Students, StudentClass).filter(Class.c_id == StudentClass.c_id).filter(Students.s_id == StudentClass.s_id).filter(Students.s_id==selectedStudent)
    if(subquery.count() > 0):
        query = Class.query.filter(Class.c_id.in_(subquery))
        if(assignmentQuery.count() > 0):
            query = query.filter(Class.c_id.notin_(assignmentQuery))
    else:
        return render_template("remove_studentClass_page.html", students=Students.query.all(), availableClasses=[], studentEntity=studentID.all(), user=User)

    return render_template("remove_studentClass_page.html", students=Students.query.all(), availableClasses=query.all(), selectedStudent=multiJoin.all(), studentEntity=studentID.all(), user=User)

@app.route("/viewStudentRecords/", methods=["GET", "POST"])
def viewStudentRecords():
    if request.method == "GET":
        return render_template("view_records_page.html", students=Students.query.all(), user=User)

    if request.method == "POST":
        selectedStudent = request.form["s_id"]
        assignments = db.session.query(Assignment, Class).filter(Assignment.s_id == selectedStudent).filter(Assignment.c_id == Class.c_id)
        multiJoin = db.session.query(Class, Students, StudentClass).filter(Class.c_id == StudentClass.c_id).filter(Students.s_id == StudentClass.s_id).filter(Students.s_id==selectedStudent)

        return render_template("view_records_page.html", multiJoin=multiJoin.all(), assignments=assignments.all(), user=User)

    return redirect(url_for('viewStudentRecords'))

@app.route("/studentRoster/", methods=["GET", "POST"])
def studentRoster():
    assignmentInfo = db.session.query(Class, Students, Assignment).filter(Assignment.c_id == Class.c_id).filter(Assignment.s_id == Students.s_id)
    if request.method == "GET":
        return render_template("student_roster_page.html", students=Students.query.all(), assignments=assignmentInfo.all(), classes=Class.query.all(), user=User)

@app.route("/studentRosterAlphabetical/", methods=["GET", "POST"])
def studentRosterAlphabetical():
    assignmentInfo = db.session.query(Class, Students, Assignment).filter(Assignment.c_id == Class.c_id).filter(Assignment.s_id == Students.s_id).order_by(Assignment.a_name.asc())
    if request.method == "GET":
        return render_template("student_roster_alphabetical_page.html", students=Students.query.order_by(Students.s_first_name.asc()).all(), assignments=assignmentInfo.all(),
        classes=Class.query.order_by(Class.c_name.asc()).all(), user=User)

@app.route("/", methods=["GET", "POST"])
def index():
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
    return redirect(url_for('dashboard'))


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard/", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "GET":
        return render_template("dashboard.html", error=True)



