# from flask import Flask, render_template, request, redirect, url_for, session
# import sqlite3
# import re
# from datetime import datetime
# import os
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
# from flask_bcrypt import Bcrypt
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address

# app = Flask(__name__)
# app.secret_key = os.environ.get("SECRET_KEY", "fallbacksecret")

# bcrypt = Bcrypt(app)
# limiter = Limiter(get_remote_address, app=app)

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# # ---------------- DATABASE ----------------
# def init_db():
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     c.execute('''CREATE TABLE IF NOT EXISTS users(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT UNIQUE,
#         password TEXT)''')

#     c.execute('''CREATE TABLE IF NOT EXISTS messages(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id INTEGER,
#         sender TEXT,
#         message TEXT,
#         timestamp TEXT)''')

#     conn.commit()
#     conn.close()

# init_db()

# # ---------------- USER ----------------
# class User(UserMixin):
#     def __init__(self, id):
#         self.id = id

# @login_manager.user_loader
# def load_user(user_id):
#     return User(user_id)

# # ---------------- SECURITY ----------------
# def is_safe_input(text):
#     return not re.search(r"(DROP|DELETE|INSERT|SELECT|UPDATE)", text, re.I)

# # ---------------- CHATBOT ----------------
# import random

# def chatbot_response(msg):
#     msg = msg.lower()

#     greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
#     greet_reply = ["Hello! 👋", "Hi there! 😊", "Hey! 👋", "Welcome! 🎓", "Good to see you!"]

    
        
#     data = {

# "cgpa": ["CGPA is your overall academic average.", "It measures total performance.", "It combines all semesters.", "It reflects academic consistency.", "Higher CGPA means better results."],
# "gpa": ["GPA is per semester performance.", "It measures one term.", "It contributes to CGPA.", "It resets each semester.", "It tracks short-term results."],
# "admission": ["Admission requires requirements.", "You need JAMB score.", "Screening is needed.", "Depends on course.", "Documents must be complete."],
# "cutoff": ["Cut-off is minimum score.", "Varies by course.", "Higher is safer.", "Changes yearly.", "Important for entry."],
# "jamb": ["JAMB is entrance exam.", "Required for admission.", "Score matters.", "First step.", "Used for screening."],
# "postutme": ["Post-UTME is screening.", "After JAMB.", "Affects admission.", "Some schools skip.", "Prepare well."],
# "fees": ["Fees vary by course.", "Check portal.", "Pay early.", "Late penalty.", "Confirm payment."],
# "acceptance": ["Confirms admission.", "Paid once.", "Non-refundable.", "Very important.", "Secures slot."],
# "exam": ["End of semester test.", "Requires registration.", "Schedule released.", "Missing is risky.", "Prepare well."],
# "carryover": ["Failed course repeat.", "Retake required.", "Delays progress.", "Avoid it.", "Common issue."],
# "result": ["Check via portal.", "Shows grades.", "May delay.", "Needs payment.", "Updated online."],
# "transcript": ["Academic record.", "Used for jobs.", "Official doc.", "Request from school.", "Contains results."],
# "registration": ["Done each semester.", "Select courses.", "Compulsory.", "Late penalty.", "Needs approval."],
# "hostel": ["Student housing.", "Limited space.", "Apply early.", "On campus.", "Requires payment."],
# "siwes": ["Industrial training.", "Gives experience.", "Attach to firm.", "Submit report.", "Important program."],
# "clearance": ["Confirms no debt.", "Needed to graduate.", "Multiple units.", "Avoid delay.", "Start early."],
# "matriculation": ["Admission ceremony.", "Welcomes students.", "Official entry.", "Take oath.", "Important event."],
# "graduation": ["Program completion.", "Get certificate.", "Requires clearance.", "Celebration.", "Final stage."],
# "lecture": ["Teaching session.", "By lecturers.", "Attend always.", "Take notes.", "Important learning."],
# "assignment": ["Given tasks.", "Graded work.", "Submit early.", "Improves learning.", "Can be group."],
# "project": ["Final year work.", "Research-based.", "Supervisor guides.", "Defense needed.", "Tests knowledge."],
# "portal": ["Student system.", "Check results.", "Register courses.", "Secure login.", "Very important."],
# "login": ["Access account.", "Use credentials.", "Keep safe.", "Required always.", "Private entry."],
# "password": ["Protects account.", "Keep secret.", "Use strong one.", "Change often.", "Do not share."],
# "department": ["Handles courses.", "Student belongs here.", "Guides academics.", "Manages subjects.", "Important unit."],
# "faculty": ["Group of departments.", "Led by dean.", "Oversees study.", "Academic body.", "Manages programs."],
# "library": ["Study center.", "Books available.", "Quiet space.", "Supports research.", "Digital access."],
# "semester": ["Study period.", "2 per year.", "Contains courses.", "Ends with exams.", "Important timeline."],
# "session": ["Full academic year.", "Contains semesters.", "Starts admission.", "Ends yearly.", "Academic cycle."],
# "defer": ["Postpone admission.", "Needs approval.", "Valid reason.", "Temporary break.", "Resume later."],
# "withdraw": ["Leave program.", "Formal exit.", "Can reapply.", "Serious step.", "Requires process."],
# "idcard": ["Student ID.", "Proof of identity.", "Needed on campus.", "Issued by school.", "Carry always."],
# "timetable": ["Lecture schedule.", "Shows time.", "Helps planning.", "Updated often.", "Check regularly."],
# "venue": ["Lecture location.", "Exam hall.", "In timetable.", "Avoid confusion.", "Know your class."],
# "attendance": ["Presence in class.", "Important for marks.", "Tracked often.", "Required sometimes.", "Boost learning."],
# "probation": ["Low CGPA warning.", "Improve quickly.", "Risk removal.", "Temporary status.", "Needs effort."],
# "expulsion": ["Permanent removal.", "Due to misconduct.", "Serious case.", "Strict rule.", "Avoid issues."],
# "dresscode": ["School dressing.", "Follow rules.", "Applies in exams.", "Avoid punishment.", "Maintain discipline."],
# "deadline": ["Submission date.", "Must meet it.", "Late penalty.", "Important timing.", "Plan ahead."],
# "groupwork": ["Team assignment.", "Shared tasks.", "Work together.", "Improves teamwork.", "Common task."],
# "presentation": ["Oral explanation.", "Use slides.", "Speak clearly.", "Part of grading.", "Confidence matters."],
# "defense": ["Project presentation.", "Panel review.", "Answer questions.", "Final step.", "Important stage."],
# "internship": ["Work experience.", "Like SIWES.", "Build skills.", "Real exposure.", "Career growth."],
# "certificate": ["Proof of study.", "Issued after grad.", "Official doc.", "Needed for jobs.", "Important record."],
# "alumni": ["Past students.", "Stay connected.", "Support network.", "Events held.", "Career help."],
# "bursary": ["Handles payments.", "School finance unit.", "Confirms fees.", "Important office.", "Payment issues."],
# "hod": ["Head of department.", "Leads department.", "Academic authority.", "Handles issues.", "Guides students."],
# "dean": ["Faculty head.", "Oversees departments.", "Academic leader.", "Manages faculty.", "Important role."],
# "examofficer": ["Manages exams.", "Handles schedules.", "Controls records.", "Important staff.", "Exam authority."],
# "ict": ["Tech department.", "Handles systems.", "Portal issues.", "Support services.", "Important unit."],

# "default": ["Ask about academics.", "I can help you.", "Try school topics.", "Rephrase please.", "I am here to assist."]
# }


#     is_greet = any(g in msg for g in greetings)

#     for key in data:
#         if key in msg:
#             response = random.choice(data[key])
#             return f"{random.choice(greet_reply)} {response}" if is_greet else response

#     return f"{random.choice(greet_reply)} How can I assist you?" if is_greet else random.choice(data["default"])
# # ---------------- REGISTER ----------------
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = bcrypt.generate_password_hash(request.form["password"]).decode()

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()

#         try:
#             c.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
#             conn.commit()
#         except:
#             return "User already exists"

#         return redirect(url_for("login"))

#     return render_template("register.html")

# # ---------------- LOGIN ----------------
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         conn = sqlite3.connect("database.db")
#         c = conn.cursor()
#         c.execute("SELECT * FROM users WHERE username=?", (username,))
#         user = c.fetchone()
#         conn.close()

#         if user and bcrypt.check_password_hash(user[2], password):
#             login_user(User(user[0]))
#             return redirect(url_for("chat"))

#         return "Invalid login details"

#     return render_template("login.html")

# # ---------------- CHAT ----------------
# @app.route("/", methods=["GET", "POST"])
# @login_required
# @limiter.limit("10 per minute")
# def chat():
#     user_id = session.get("_user_id")

#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     if request.method == "POST":
#         msg = request.form["message"]

#         if not is_safe_input(msg):
#             return "Invalid input detected!"

#         reply = chatbot_response(msg)
#         time = datetime.now().strftime("%H:%M")

#         c.execute("INSERT INTO messages(user_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
#                   (user_id, "user", msg, time))

#         c.execute("INSERT INTO messages(user_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
#                   (user_id, "bot", reply, time))

#         conn.commit()

#     c.execute("SELECT sender, message, timestamp FROM messages WHERE user_id=?", (user_id,))
#     chats = c.fetchall()

#     conn.close()

#     return render_template("chat.html", chats=chats)

# # ---------------- ADMIN ----------------
# @app.route("/admin")
# @login_required
# def admin():
#     conn = sqlite3.connect("database.db")
#     c = conn.cursor()

#     c.execute("SELECT COUNT(*) FROM users")
#     users = c.fetchone()[0]

#     c.execute("SELECT COUNT(*) FROM messages")
#     messages = c.fetchone()[0]

#     conn.close()

#     return render_template("admin.html", users=users, messages=messages)

# # ---------------- LOGOUT ----------------
# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for("login"))

# # ---------------- RUN ----------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=10000)


# ================= IMPORTS =================

# Flask and web handling
from flask import Flask, render_template, request, redirect, url_for, session

# Database
import sqlite3

# Security (input validation)
import re

# Time for message timestamps
from datetime import datetime

# Environment variables (for API key & secret key)
import os

# Authentication system
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

# Password hashing
from flask_bcrypt import Bcrypt

# Rate limiting (prevent spam/DoS)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Gemini AI
import google.generativeai as genai


# ================= APP CONFIG =================
app = Flask(__name__)

# Secret key for sessions (important for security)
app.secret_key = os.environ.get("SECRET_KEY", "fallbacksecret")


# ================= GEMINI AI SETUP =================
# Get API key from environment variable
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Load AI model
model = genai.GenerativeModel("gemini-1.5-flash-latest")


# ================= SECURITY TOOLS =================
bcrypt = Bcrypt(app)  # For password hashing
limiter = Limiter(get_remote_address, app=app)  # Rate limiter


# ================= LOGIN MANAGER =================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ================= DATABASE SETUP =================
def init_db():

    #Create database tables if they dont exist
    
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT)''')

    # Messages table (stores chat history)
    c.execute('''CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sender TEXT,
        message TEXT,
        timestamp TEXT)''')

    conn.commit()
    conn.close()

# Initialize DB when app starts
init_db()


# ================= USER CLASS =================
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Load user from session
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# ================= INPUT SECURITY =================
def is_safe_input(text):
    
   # Prevent basic SQL injection keywords
    
    return not re.search(r"(DROP|DELETE|INSERT|SELECT|UPDATE)", text, re.I)


# ================= AI CHATBOT =================
# Stores chat history per user
chat_history = {}

def chatbot_response(msg, user_id):
    
    #Generate AI response using Gemini
    
    try:
        # Initialize user history if not exists
        if user_id not in chat_history:
            chat_history[user_id] = []

        # System instruction (controls AI behavior)
        system_prompt = """
        You are a smart university chatbot designed to assist students.

        You ONLY answer questions related to:
        - admission
        - school fees
        - courses
        - exams
        - results
        - CGPA
        - student life

        Rules:
        - Be clear and helpful
        - Be concise
        - If unrelated, politely say you only handle school-related questions
        - Sound natural and friendly
        
"""
        # Add user message to history
        chat_history[user_id].append(f"User: {msg}")

        # Build full conversation prompt
        prompt = system_prompt + "\n" + "\n".join(chat_history[user_id]) + "\nBot:"

        # Generate AI response
        response = model.generate_content(prompt)
        bot_reply = response.text

        # Save AI reply
        chat_history[user_id].append(f"Bot: {bot_reply}")

        return bot_reply

    except Exception as e:
        print("Gemini Error:", e)
        return f"Error: {str(e)}"



# ================= REGISTER ROUTE =================
@app.route("/register", methods=["GET", "POST"])
def register():
    
  #  Handle user registration
    
    if request.method == "POST":
        username = request.form["username"]

        # Hash password for security
        password = bcrypt.generate_password_hash(request.form["password"]).decode()

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        try:
            # Insert new user
            c.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        return redirect(url_for("login"))

    return render_template("register.html")


# ================= LOGIN ROUTE =================
@app.route("/login", methods=["GET", "POST"])
def login():
    
   # Handle user login
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        # Fetch user from DB
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        # Check password
        if user and bcrypt.check_password_hash(user[2], password):
            login_user(User(user[0]))
            return redirect(url_for("chat"))

        return "Invalid login details"

    return render_template("login.html")


# ================= CHAT ROUTE =================
@app.route("/", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")  # Prevent spam
def chat():
    
   # Main chatbot interface
    
    user_id = session.get("_user_id")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if request.method == "POST":
        msg = request.form["message"]

        # Validate input
        if not is_safe_input(msg):
            return "Invalid input detected!"

        # Get AI response
        reply = chatbot_response(msg, user_id)

        # Timestamp
        time = datetime.now().strftime("%H:%M")

        # Save user message
        c.execute("INSERT INTO messages(user_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                  (user_id, "user", msg, time))

        # Save bot response
        c.execute("INSERT INTO messages(user_id, sender, message, timestamp) VALUES (?, ?, ?, ?)",
                  (user_id, "bot", reply, time))

        conn.commit()

    # Fetch chat history
    c.execute("SELECT sender, message, timestamp FROM messages WHERE user_id=?", (user_id,))
    chats = c.fetchall()

    conn.close()

    return render_template("chat.html", chats=chats)


# ================= ADMIN ROUTE =================
@app.route("/admin")
@login_required
def admin():

   # Admin dashboard showing statistics

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM messages")
    messages = c.fetchone()[0]

    conn.close()

    return render_template("admin.html", users=users, messages=messages)


# ================= LOGOUT =================
@app.route("/logout")
@login_required
def logout():
    
   # Logout user
    
    logout_user()
    return redirect(url_for("login"))


# ================= RUN APP =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

