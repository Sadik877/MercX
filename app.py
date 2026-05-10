from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# DATABASE PATH FOR VERCEL
DB_PATH = "/tmp/database.db"


# CONNECT DATABASE
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


# INITIALIZE DATABASE
def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    db.commit()
    db.close()


# RUN DATABASE INIT
init_db()


# MAINTENANCE PAGE
@app.route("/")
def home():
    return render_template("maintenance.html")


# TEST ROUTE
@app.route("/test")
def test():
    return "MERCX Maintenance Mode Active"


# START APP
if __name__ == "__main__":
    app.run(debug=True)