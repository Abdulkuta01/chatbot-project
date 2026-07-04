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

    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    greet_reply = ["Hello! 👋", "Hi there! 😊", "Hey! 👋", "Welcome! 🎓", "Good to see you!"]

    data = {

        "cgpa": ["CGPA is your overall academic average.", "It reflects total performance.", "It is calculated across semesters.", "It shows academic consistency.", "Higher CGPA means better results."],

        "gpa": ["GPA is per semester performance.", "It measures one semester.", "It contributes to CGPA.", "It resets each semester.", "It tracks short-term performance."],

        "admission": ["Admission requires meeting requirements.", "You need JAMB score.", "Screening is required.", "Depends on course demand.", "Documents must be complete."],

        "cut off": ["Cut-off is minimum score.", "Each course differs.", "Higher is better.", "Changes yearly.", "Important for admission."],

        "jamb": ["JAMB is entrance exam.", "Required for admission.", "Score determines eligibility.", "First step to university.", "Used for screening."],

        "post utme": ["Post-UTME is screening.", "Comes after JAMB.", "Affects admission.", "Some schools skip it.", "Prepare well."],

        "fees": ["Fees vary by course.", "Check portal.", "Must be paid early.", "Late payment penalty.", "Confirm payment."],

        "acceptance": ["Confirms admission.", "Paid after offer.", "Non-refundable.", "Very important.", "Secure your spot."],

        "exam": ["End of semester test.", "Must register courses.", "Schedule released early.", "Missing leads to fail.", "Prepare well."],

        "carryover": ["Failed course repeat.", "Register again.", "Delays graduation.", "Avoid by studying.", "Common issue."],

        "result": ["Check via portal.", "Shows performance.", "May delay sometimes.", "Requires fee payment.", "Updated online."],

        "transcript": ["Academic record.", "Used for jobs/studies.", "Official document.", "Request from school.", "Contains results."],

        "registration": ["Done each semester.", "Select courses.", "Compulsory.", "Late penalty.", "Needs approval."],

        "hostel": ["Student accommodation.", "Limited spaces.", "Apply early.", "On campus.", "Requires payment."],

        "siwes": ["Industrial training.", "Gives experience.", "Required in some courses.", "Attach to company.", "Submit report."],

        "clearance": ["Confirms no issues.", "Required before graduation.", "Done across units.", "Avoid delay.", "Start early."],

        "matriculation": ["Admission ceremony.", "Welcomes students.", "Official entry.", "Take oath.", "Important event."],

        "graduation": ["End of program.", "Receive certificate.", "Requires clearance.", "Celebration event.", "Marks success."],

        "lecture": ["Teaching session.", "By lecturers.", "Important to attend.", "Provides notes.", "May be online."],

        "assignment": ["Given tasks.", "Part of grading.", "Submit early.", "Improves learning.", "Can be group work."],

        "project": ["Final year work.", "Research-based.", "Supervisor assigned.", "Defense required.", "Tests knowledge."],

        "portal": ["Student system.", "Check results.", "Register courses.", "Secure login.", "Important tool."],

        "login": ["Access account.", "Use credentials.", "Keep safe.", "Required always.", "Private access."],

        "password": ["Protects account.", "Keep secret.", "Use strong one.", "Change regularly.", "Do not share."],

        "department": ["Handles courses.", "Student belongs here.", "Manages academics.", "Guides students.", "Important unit."],

        "faculty": ["Group of departments.", "Led by dean.", "Oversees programs.", "Academic structure.", "Manages departments."],

        "library": ["Study center.", "Books available.", "Quiet space.", "Supports research.", "Digital access too."],

        "semester": ["Academic period.", "Usually 2 per year.", "Contains courses.", "Ends with exams.", "Important timeline."],

        "session": ["Academic year.", "Includes semesters.", "Starts admission.", "Ends with results.", "Full academic cycle."],

        "defer": ["Postpone admission.", "Requires approval.", "Valid reason needed.", "Temporary delay.", "Resume later."],

        "withdraw": ["Leave program.", "Can reapply later.", "Requires process.", "Formal exit.", "Important decision."],

        "id card": ["Student identity.", "Used for access.", "Must carry it.", "Issued by school.", "Very important."],

        "timetable": ["Schedule of lectures.", "Shows time/venue.", "Helps planning.", "Updated regularly.", "Check often."],

        "venue": ["Place of lecture.", "Exam location.", "Specified in timetable.", "Important to know.", "Avoid confusion."],

        "attendance": ["Presence in class.", "Important for grading.", "Required sometimes.", "Tracked by lecturers.", "Improves learning."],

        "probation": ["Low performance warning.", "Improve CGPA.", "Risk of withdrawal.", "Temporary status.", "Needs attention."],

        "expulsion": ["Permanent removal.", "Due to misconduct.", "Serious consequence.", "Strict rule.", "Avoid violations."],

        "dress code": ["School dressing rule.", "Must follow guidelines.", "Applies to exams.", "Maintains discipline.", "Avoid sanctions."],

        "deadline": ["Submission date.", "Must meet it.", "Late penalty.", "Important for tasks.", "Plan ahead."],

        "group work": ["Team assignment.", "Collaboration needed.", "Shared tasks.", "Improves teamwork.", "Common in school."],

        "presentation": ["Oral explanation.", "Part of grading.", "Prepare slides.", "Speak clearly.", "Confidence needed."],

        "defense": ["Project presentation.", "Panel evaluation.", "Final assessment.", "Answer questions.", "Important stage."],

        "internship": ["Work experience.", "Similar to SIWES.", "Build skills.", "Real-world exposure.", "Career growth."],

        "certificate": ["Proof of study.", "Issued after graduation.", "Important document.", "Used for jobs.", "Official record."],

        "alumni": ["Past students.", "Remain connected.", "Support network.", "Events organized.", "Career help."],

        "default": ["I can help with academic questions.", "Ask about school topics.", "Try CGPA, admission, etc.", "I’m here to assist.", "Please rephrase."]
    }

    is_greet = any(g in msg for g in greetings)

    for key in data:
        if key in msg:
            response = random.choice(data[key])
            return f"{random.choice(greet_reply)} {response}" if is_greet else response

    return f"{random.choice(greet_reply)} How can I assist you?" if is_greet else random.choice(data["default"])

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