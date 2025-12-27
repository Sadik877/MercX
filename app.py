from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__, static_folder="static")
app.secret_key = "mercx_secret"

def get_db():
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_blocked INTEGER DEFAULT 0
    )""")
    db.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT
    )""")
    db.commit()

init_db()

# ===== LOGIN =====
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        db=get_db()
        u=db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (request.form["username"],request.form["password"])
        ).fetchone()
        if u:
            if u["is_blocked"]: return "Blocked by admin"
            session["user_id"]=u["id"]
            return redirect("/users")
    return render_template("login.html")

# ===== REGISTER =====
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        db=get_db()
        db.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (request.form["username"],request.form["password"])
        )
        db.commit()
        return redirect("/verify")
    return render_template("register.html")

# ===== VERIFY =====
@app.route("/verify", methods=["GET","POST"])
def verify():
    if request.method=="POST":
        return redirect("/")
    return render_template("verify.html")

# ===== USERS =====
@app.route("/users")
def users():
    if "user_id" not in session: return redirect("/")
    db=get_db()
    users=db.execute(
        "SELECT id,username FROM users WHERE id!=?",
        (session["user_id"],)
    ).fetchall()
    return render_template("users.html",users=users)

# ===== CHAT =====
@app.route("/chat/<int:user_id>", methods=["GET","POST"])
def chat(user_id):
    if request.method=="POST":
        get_db().execute(
            "INSERT INTO messages(sender_id,receiver_id,message) VALUES (?,?,?)",
            (session["user_id"],user_id,request.form["message"])
        )
        get_db().commit()
    other=get_db().execute(
        "SELECT username FROM users WHERE id=?",(user_id,)
    ).fetchone()
    return render_template("chat.html",other=other["username"])

@app.route("/fetch/<int:user_id>")
def fetch(user_id):
    db=get_db()
    msgs=db.execute("""
    SELECT sender_id,message FROM messages
    WHERE (sender_id=? AND receiver_id=?)
    OR (sender_id=? AND receiver_id=?)
    """,(session["user_id"],user_id,user_id,session["user_id"])).fetchall()
    return jsonify([dict(m) for m in msgs])

# ===== ADMIN =====
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST":
        if request.form["username"]=="admin" and request.form["password"]=="admin123":
            session["admin"]=True
            return redirect("/admin/dashboard")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dash():
    if not session.get("admin"): return redirect("/admin")
    db=get_db()
    users=db.execute("SELECT * FROM users").fetchall()
    msgs=db.execute("SELECT * FROM messages").fetchall()
    return render_template("admin_dashboard.html",users=users,messages=msgs)

@app.route("/admin/block/<int:id>")
def block(id):
    get_db().execute("UPDATE users SET is_blocked=1 WHERE id=?",(id,))
    get_db().commit()
    return redirect("/admin/dashboard")

@app.route("/admin/unblock/<int:id>")
def unblock(id):
    get_db().execute("UPDATE users SET is_blocked=0 WHERE id=?",(id,))
    get_db().commit()
    return redirect("/admin/dashboard")

app.run(debug=True)