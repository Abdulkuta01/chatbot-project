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

# ---------------- AI-LIKE CHATBOT ----------------
import os
import requests

def chatbot_response(msg):

    api_key = os.environ.get("AI_API_KEY")

    if not api_key:
        return "AI not configured."

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"You are a helpful university assistant.\nUser: {msg}"}
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        # 🔍 SHOW REAL ERROR (VERY IMPORTANT)
        if response.status_code != 200:
            return f"Gemini error: {response.text}"

        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"]

   except Exception as e:
    return f"Connection error: {str(e)}"
       

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