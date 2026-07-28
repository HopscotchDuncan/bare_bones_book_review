from flask import Flask
import sqlite3 as sql
# if this ends up being bigger should probably use a mysql connection

# TODO:
# - Add search bar to home page
# - Develop update and create functions
# - Add ability to create new book entry
#  - Add ability to create new genre entries per book
# - Add ability to create new review entry
# - Add custom sql statement method (I think I'm gonna need this for the review rating)
# - Generic date formatter? Treat this like an extra
# Error checks
# - If anything is not given
# - If SQL statement is incomplete (should be trivial)

app = Flask(__name__)
connection_string = "./final_project_db.db"

# get column names, used for construct_db_response in get and read
def get_table_columns(table):
    con = sql.connect(connection_string)
    cur = con.cursor()

    execute = cur.execute("pragma table_info(" + table + ")")
    headers = execute.fetchall()    
    column_names = []

    for i in headers:
        column_names.append(i[1])

    return column_names


# get keyed response from db, used in get and read
def construct_db_response(select_statement, column_names):
    con = sql.connect(connection_string)
    cur = con.cursor()
    formatted_length = len(column_names)

    result = cur.execute(select_statement)
    constructed_full = []
    for entry in result.fetchall():
        constructed = {}
        for i in range(0, formatted_length):
            constructed[column_names[i]] = entry[i]
        constructed_full.append(constructed)
    return constructed_full


# get based on table and id
def get(table, id):
    response = construct_db_response("select * from " + table + " where " + table[:len(table)-1] + "_id = " + str(id), get_table_columns(table))
    if len(response) > 0:
        return response[0]
    else:
        return None


# read based on table and a dictionary of params that will be filled into the where clause
def read(table, params):
    select_statement = "select * from " + table + " where "
    where_array = []

    for i in params:
        where_array.append(i + " = " + str(params[i]))

    select_statement += " and ".join(where_array)

    response = construct_db_response(select_statement, get_table_columns(table))
    if len(response) > 0:
        return response
    else:
        return None


def update():
    #todo
    return


def create():
    #todo
    return


# todo I think I need this for an average rating thru review averages
def custom():
    #todo, use for average rating
    return


@app.route("/")
def main():
    #todo
    return '<h1>Welcome to Bare Bones Book Reviews!</h1>'


@app.route("/test")
def test():
    return read("reviews", {"book_id": "2"})


@app.route("/book/<int:book_id>")
def book(book_id):
    body = "<body>"

    # construct book
    book = get("books", book_id)

    if (book == None):
        return "<h1>Book not found!</h1>"

    body += "<h1>" + book["name"] + "</h1>"
    body += "<h3>" + "Written by " + book["author"] + ", " + str(book["year"]) + "</h3>"
    body += "<a href=http://" + book["url"] + " target=_blank>Buy it here for " + str(book["price"]) + "!</a>" # open in new tab
    # todo add average rating here

    # construct reviews
    reviews = read("reviews", {"book_id": book_id})

    if (reviews != None):
        body += "<br><br>"
        for review in reviews:
            body += "<h4>" + review["title"] + " - " + str(review["rating"]) + "*</h4>"
            body += "<div>Written by " + review["reviewer"] + " on " + review["date"] + "</div>"
            body += "<details><summary>Review</summary>" + review["description"] + "</details>"

    body += "</body>"
    return body

