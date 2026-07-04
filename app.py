from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
from datetime import datetime
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallbacksecret")

bcrypt = Bcrypt(app)
limiter = Limiter(get_remote_address, app=app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sender TEXT,
        message TEXT,
        timestamp TEXT)''')

    conn.commit()
    conn.close()

init_db()

# ---------------- USER ----------------
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ---------------- SECURITY ----------------
def is_safe_input(text):
    return not re.search(r"(DROP|DELETE|INSERT|SELECT|UPDATE)", text, re.I)

# ---------------- CHATBOT (STABLE VERSION) ----------------
import random

def chatbot_response(msg):
    msg = msg.lower()

    data = {

        "cgpa": [
            "CGPA is the cumulative average of your grade points across all semesters.",
            "It reflects your overall academic performance throughout your program.",
            "CGPA is calculated by dividing total grade points by total credit units.",
            "It helps measure long-term academic success.",
            "A higher CGPA indicates better academic performance."
        ],

        "gpa": [
            "GPA is your grade point average for a single semester.",
            "It shows your academic performance within a semester.",
            "Each semester has its own GPA.",
            "GPA contributes to your overall CGPA.",
            "It helps track short-term performance."
        ],

        "credit": [
            "Credit unit represents the weight of a course.",
            "Courses have different credit units based on importance.",
            "Higher credit courses affect your CGPA more.",
            "Credits determine workload and grading weight.",
            "Each course contributes differently based on its credit."
        ],

        "admission": [
            "Admission requires meeting cut-off marks and passing screening.",
            "You need a good JAMB score and proper documentation.",
            "Admission depends on performance and course availability.",
            "Screening results also affect admission chances.",
            "Ensure all requirements are complete before applying."
        ],

        "cut off": [
            "Cut-off mark is the minimum score required for admission.",
            "Each department sets its own cut-off mark.",
            "Higher scores increase your chances.",
            "Cut-off marks may vary yearly.",
            "Always aim above the minimum requirement."
        ],

        "jamb": [
            "JAMB is required for university admission in Nigeria.",
            "Your JAMB score determines eligibility.",
            "It is the first step to gaining admission.",
            "You must meet the required score.",
            "JAMB result is used for screening."
        ],

        "post utme": [
            "Post-UTME is conducted after JAMB.",
            "It helps schools screen candidates.",
            "Performance affects admission chances.",
            "Some schools conduct online screening.",
            "Prepare well for Post-UTME exams."
        ],

        "fees": [
            "School fees depend on your course and level.",
            "Check the portal for exact fee details.",
            "Fees must be paid before exams.",
            "Late payment may attract penalties.",
            "Always confirm payments officially."
        ],

        "acceptance": [
            "Acceptance fee confirms your admission.",
            "It must be paid after admission is offered.",
            "Failure to pay may lead to losing admission.",
            "It is usually non-refundable.",
            "Pay it through official channels."
        ],

        "exam": [
            "Exams are held at the end of each semester.",
            "You must register courses before exams.",
            "Exam schedules are released early.",
            "Missing exams can lead to failure.",
            "Preparation is key to success."
        ],

        "carryover": [
            "Carryover means retaking a failed course.",
            "It happens when you fail a subject.",
            "You must register it again.",
            "It can delay graduation.",
            "Avoid carryover by preparing well."
        ],

        "result": [
            "Results are released on the student portal.",
            "You can check using your login details.",
            "Results reflect your academic performance.",
            "Sometimes results may be delayed.",
            "Ensure fees are paid to access results."
        ],

        "transcript": [
            "Transcript shows your academic record.",
            "It contains all your results.",
            "It is used for further studies.",
            "You can request it from your school.",
            "It is an official academic document."
        ],

        "registration": [
            "Course registration is done every semester.",
            "You must select your courses carefully.",
            "Late registration may attract penalties.",
            "Approval may be required.",
            "Registration is compulsory."
        ],

        "hostel": [
            "Hostels provide accommodation for students.",
            "Allocation depends on availability.",
            "Apply early to secure a space.",
            "Hostels are located on campus.",
            "Payment is required for allocation."
        ],

        "siwes": [
            "SIWES is industrial training for students.",
            "It provides practical experience.",
            "Students work in companies.",
            "It is required for some courses.",
            "You must submit a report."
        ],

        "clearance": [
            "Clearance confirms no outstanding issues.",
            "It is required before graduation.",
            "You must complete all departments.",
            "Incomplete clearance causes delays.",
            "Always start early."
        ],

        "matriculation": [
            "Matriculation is the official admission ceremony.",
            "It welcomes new students.",
            "Attendance is important.",
            "It marks your entry into university.",
            "Students take an oath during it."
        ],

        "graduation": [
            "Graduation marks completion of studies.",
            "Students receive certificates.",
            "It is held annually.",
            "Clearance is required before graduation.",
            "It celebrates academic success."
        ],

        "lecture": [
            "Lectures are teaching sessions.",
            "They are conducted by lecturers.",
            "Attendance is important.",
            "Notes help in exams.",
            "Lectures may be physical or online."
        ],

        "assignment": [
            "Assignments are given for assessment.",
            "They contribute to your grades.",
            "Submit before deadlines.",
            "They improve understanding.",
            "They can be individual or group work."
        ],

        "project": [
            "Projects are final year research work.",
            "You will have a supervisor.",
            "It involves detailed study.",
            "Defense is required.",
            "It tests your knowledge."
        ],

        "portal": [
            "The portal is used for student activities.",
            "You can check results there.",
            "Login with your credentials.",
            "Keep your details secure.",
            "It is very important."
        ],

        "login": [
            "Login gives access to your account.",
            "Use your username and password.",
            "Keep your login details safe.",
            "Do not share your credentials.",
            "It is required for portal access."
        ],

        "password": [
            "Passwords protect your account.",
            "Use strong passwords.",
            "Do not share your password.",
            "Change it regularly.",
            "Keep it secure."
        ],

        "department": [
            "Departments manage specific courses.",
            "Each student belongs to a department.",
            "Departments handle academic matters.",
            "They set course requirements.",
            "They guide students."
        ],

        "faculty": [
            "A faculty is a group of related departments.",
            "It oversees academic programs.",
            "Each faculty has a dean.",
            "Students belong to faculties.",
            "It manages departments."
        ],

        "library": [
            "Library provides academic resources.",
            "Students can read and borrow books.",
            "It supports research.",
            "Quiet study is encouraged.",
            "Digital resources are also available."
        ],

        "default": [
            "I can help with admission, fees, CGPA, exams, and more.",
            "Please ask a clear academic-related question.",
            "Try asking about student activities or academics.",
            "I'm here to assist you with school information.",
            "Kindly rephrase your question for better understanding."
        ]
    }

    for key in data:
        if key in msg:
            return random.choice(data[key])

    return random.choice(data["default"])

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):
            login_user(User(user[0]))
            return redirect(url_for("chat"))

        return "Invalid login details"

    return render_template("login.html")

# ---------------- CHAT ----------------
@app.route("/", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")
def chat():
    user_id = session.get("_user_id")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        msg = request.form["message"]

        if not is_safe_input(msg):
            return "Invalid input detected!"

        reply = chatbot_response(msg)
        time = datetime.now().strftime("%H:%M")

        c.execute("INSERT INTO messages(user_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                  (user_id, "user", msg, time))

        c.execute("INSERT INTO messages(user_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                  (user_id, "bot", reply, time))

        conn.commit()

    c.execute("SELECT sender, message, timestamp FROM messages WHERE user_id=?", (user_id,))
    chats = c.fetchall()

    conn.close()

    return render_template("chat.html", chats=chats)

# ---------------- ADMIN ----------------
@app.route("/admin")
@login_required
def admin():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM messages")
    messages = c.fetchone()[0]

    conn.close()

    return render_template("admin.html", users=users, messages=messages)

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)