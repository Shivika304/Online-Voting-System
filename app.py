from flask import Flask, render_template, request, jsonify,request, redirect, url_for, session
from models import create_tables
from auth import register_user, login_user
from voting import cast_vote
from flask import flash
from database import get_db

# 1️⃣ CREATE APP FIRST
app = Flask(__name__)
app.secret_key = "secret123"

# 2️⃣ CREATE DATABASE TABLES
create_tables()

# 3️⃣ ROUTES (AFTER app is defined)
@app.route("/")
def home():
    return render_template("login.html")


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        success = register_user(username, password)

        if success:
            flash("Account created. Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Account already exists. Please login.", "error")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = login_user(username, password)

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("vote_page"))
        else:
            flash("Account does not exist. Please register or login with a valid account.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/vote-page")
def vote_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "vote.html",
        username=session["username"]
    )

@app.route("/vote", methods=["POST"])
def vote():
    if "user_id" not in session:
        return redirect(url_for("login"))

    voter_id = session["user_id"]
    candidate_id = request.form.get("candidate_id")

    success = cast_vote(voter_id, candidate_id)

    session.clear()

    if success:
        flash("You have already completed the voting process.", "success")
    else:
        flash("You have already voted. Multiple voting is not allowed.", "error")

    return redirect(url_for("login"))


@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    db = get_db()
    cursor = db.cursor()

    # voters (NO PASSWORD)
    cursor.execute("""
        SELECT id, username, has_voted
        FROM voters
    """)
    voters = cursor.fetchall()

    # results
    cursor.execute("""
        SELECT candidates.name, COUNT(votes.id) as total_votes
        FROM candidates
        LEFT JOIN votes ON candidates.id = votes.candidate_id
        GROUP BY candidates.id
    """)
    results = cursor.fetchall()

    db.close()

    return render_template(
        "admin_dashboard.html",
        voters=voters,
        results=results
    )


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Change these credentials as you want
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

# 4️⃣ RUN SERVER (LAST)
if __name__ == "__main__":
    app.run(debug=True)