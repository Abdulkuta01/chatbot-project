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
def chatbot_response(msg):
    msg = msg.lower()

    faq = {

        # ---------------- ACADEMICS ----------------
        "what is cgpa": "CGPA (Cumulative Grade Point Average) is the average of a student's academic performance across all semesters.",
        "what is gpa": "GPA is Grade Point Average for a single semester.",
        "how is cgpa calculated": "CGPA is calculated by dividing total grade points by total credit units.",
        "what is credit unit": "A credit unit represents the weight of a course in academic workload.",
        "what is course registration": "Course registration is the process of selecting and enrolling in courses for a semester.",
        "what is transcript": "A transcript is an official record of a student's academic performance.",

        # ---------------- ADMISSION ----------------
        "how do i get admission": "Admission requires meeting the school's cut-off mark and passing the screening process.",
        "what is cut off mark": "Cut-off mark is the minimum score required for admission into a course.",
        "can i change course after admission": "Yes, but it depends on availability and school approval.",
        "what is jamb": "JAMB is the exam body responsible for university admissions in Nigeria.",
        "what is post utme": "Post UTME is a screening exam conducted by universities after JAMB.",

        # ---------------- FEES ----------------
        "how much is school fees": "School fees vary by department and level. Check the official portal for details.",
        "what is acceptance fee": "Acceptance fee is a compulsory payment to confirm admission.",
        "can i pay fees in installment": "Some schools allow installment payments depending on policy.",
        "what happens if i dont pay fees": "You may be denied access to exams and registration.",
        "where do i pay fees": "Fees are usually paid through the school portal or designated banks.",

        # ---------------- EXAMS ----------------
        "when is exam": "Exams are usually held at the end of each semester.",
        "what is exam slip": "An exam slip is a document that allows you to enter examination halls.",
        "what happens if i miss exam": "Missing an exam may lead to carryover or absence grading.",
        "what is carryover": "Carryover means retaking a failed course.",
        "how do i prepare for exam": "Study early, attend lectures, and review past questions.",

        # ---------------- RESULTS ----------------
        "how do i check result": "Results are checked through the student portal.",
        "why is my result withheld": "It may be due to unpaid fees or missing requirements.",
        "what is pass mark": "Pass mark is usually 40% or 45% depending on the institution.",
        "what is academic standing": "It shows your performance status (good, probation, etc).",
        "can result change": "Yes, after review or remarking.",

        # ---------------- STUDENT LIFE ----------------
        "what is hostel": "A hostel is student accommodation provided by the school.",
        "how do i get hostel": "Hostels are allocated based on availability and payment.",
        "what is siwes": "SIWES is industrial training for students to gain practical experience.",
        "what is clearance": "Clearance confirms that a student has no pending issues before graduation.",
        "what is matriculation": "Matriculation is the formal admission ceremony for new students.",

        # ---------------- GENERAL SUPPORT ----------------
        "hello": "Hello! I am your university assistant. How can I help you today?",
        "hi": "Hi there! Ask me anything about school.",
        "who are you": "I am a student support chatbot designed to help with academic questions.",
        "thank you": "You're welcome!",
        "bye": "Goodbye! Wish you success in your studies.",

        # ---------------- SYSTEM ----------------
        "what is login": "Login is the process of accessing your student account.",
        "what is register": "Register is creating a new account in the system.",
        "what is dashboard": "Dashboard is the main page showing your student information.",
        "what is admin": "Admin is the system controller who manages users and data.",
        "what is session": "Session is temporary login data stored while using the system.",

        # ---------------- EXTRA ACADEMIC ----------------
        "what is syllabus": "A syllabus is the outline of topics covered in a course.",
        "what is lecture": "A lecture is a formal teaching session in class.",
        "what is assignment": "An assignment is a task given to students for assessment.",
        "what is seminar": "A seminar is a group discussion or presentation session.",
        "what is project work": "Project work is a practical academic task based on research.",

        # ---------------- FINAL ----------------
        "default": "I'm here to help with CGPA, admission, fees, exams, results, and student life."
    }

    return faq.get(msg, faq["default"])

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