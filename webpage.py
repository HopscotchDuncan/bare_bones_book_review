from flask import Flask, render_template, request
import sqlite3 as sql
# if this ends up being bigger should probably use a mysql connection

# TODO:
# - Add search bar
# - Develop update, create, and delete functions
# - Add ability to create new book entry
#  - Add ability to create new genre entries per book
# - Add ability to create new review entry
# - Generic date formatter? Treat this like an extra

app = Flask(__name__)
connection_string = "./final_project_db.db"

# I think it's fine to keep this dumb, handling can be done higher up
def sql_call(query):
    if (!sql.complete_statement(query)):
        return []

    con = sql.connect(connection_string)
    cur = con.cursor()

    result = cur.execute(query)
    return result.fetchall()  


# get column names, used for construct_db_response in get and read
def get_table_columns(table):
    headers = sql_call("pragma table_info(" + table + ")")
    column_names = []

    for i in headers:
        column_names.append(i[1])

    return column_names


# get keyed response from db, used in get and read
def construct_db_response(select_statement, column_names):
    formatted_length = len(column_names)
    constructed_full = []
    for entry in sql_call(select_statement):
        constructed = {}
        for i in range(0, formatted_length):
            constructed[column_names[i]] = entry[i]
        constructed_full.append(constructed)

    return constructed_full


# get based on table and id
def get(table, id):
    response = construct_db_response("select * from " + table + " where " + table[:len(table)-1] + "_id = " + str(id), get_table_columns(table))

    if (len(response) > 0):
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

    if (len(response) > 0):
        return response
    else:
        return None


def update(table, id, params):
    #todo
    return


def create(table, params):
    #todo
    return


def delete(table, id):
    #todo
    return


def add_search_bar():
    return "<form action=\"/search\"><input placeholder=\"Search for a book...\"></input></form>"


@app.route("/")
def home():
    body = "<body>"
    body += "<h1>Welcome to Bare Bones Book Reviews!</h1>"
    body += add_search_bar()
    body += "</body>"
    return body


@app.route("/search/<string:query>")
def search(query):
    body = "<body>"
    body += add_search_bar()

    books = construct_db_response("select * from books where name like \"%" + query + "%\"", get_table_columns("books"))
    
    if (len(books) > 0):
        for book in books:
            body += "<h2><a href=\"/book/" + str(book["book_id"]) + "\">" + book["name"] + "</a></h2>"
    else:
        body += "<h1>No search results!</h1>"

    body += "</body>"
    return body


@app.route("/test")
def test():
    return


@app.route("/book/<int:book_id>")
def book(book_id):
    body = "<body>"

    # construct book
    book = get("books", book_id)
    genres = read("genres", {"book_id": book_id})

    if (book == None):
        return "<h1>Book not found!</h1>"

    body += "<h1>" + book["name"] + "</h1>"
    body += "<h3>" + "Written by " + book["author"] + ", " + str(book["year"]) + "</h3>"
    if (genres != None):
        genre_array = []
        for genre in genres:
            genre_array.append(genre["genre"])
        body += "<div>" + ", ".join(genre_array) + "</div><br>"
    body += "<a href=http://" + book["url"] + " target=_blank>Buy it here for " + str(book["price"]) + "!</a>" # open in new tab
    # todo add average rating here

    # construct reviews
    # todo add an add review button here
    reviews = read("reviews", {"book_id": book_id})

    if (reviews != None):
        body += "<br><br>"
        for review in reviews:
            body += "<h4>" + review["title"] + " - " + str(review["rating"]) + "*</h4>"
            body += "<div>Written by " + review["reviewer"] + " on " + review["date"] + "</div>"
            body += "<details><summary>Review</summary>" + review["description"] + "</details>"

    body += "</body>"
    return body


@app.route("/create/<string:table>")
def create_object(table):
    body = "<body>"
    
    columns = get_table_columns(table + "s")
    
    if (len(columns) == 0):
        body += "<h1>" + table + " not found in DB!</h1></body>"
        return body



    body += "</body>"
    return body

