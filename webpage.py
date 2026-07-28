from flask import Flask
import sqlite3 as sql
# if this ends up being bigger should probably use a mysql connection

app = Flask(__name__)
connection_string = "./final_project_db.db"

def test_get_all_data():
    con = sql.connect(connection_string)
    cur = con.cursor()
    result = cur.execute("select * from books limit 5")
    return result.fetchall()

def read():
    return;

def get():
    return;

def create():
    return;

def update():
    return;

@app.route("/")
def main():
    return test_get_all_data()

@app.route("/rerouted")
def rerouted():
    return "<a href='/'>This is re routed view</a>"

@app.route("/book/<int:book_id>")
def book(book_id):
    return "<div>book_id " + str(book_id) + "</div>"