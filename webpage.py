from flask import Flask, render_template, request
import sqlite3 as sql
# if this ends up being bigger should probably use a mysql connection

# TODO:
# - Add ability to create new book entry
# - Add ability to create new genre entries per book
# - Add ability to create new review entry per book
# - Add delete to every page
# - Generic date formatter? Treat this like an extra

app = Flask(__name__)
connection_string = "./final_project_db.db"

# I think it's fine to keep this dumb, handling can be done higher up
def sql_call(query):
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


# update given table with id and params
def update(table, id, params):
    # potentially update this to drop the table_id from params if present, do later shrug
    update_statement = "update " + table + " set "
    set_array = []
    
    for i in params:
        set_array.append(i + " = " + str(params[i]))
    
    update_statement += ", ".join(set_array)
    update_statement += " where " + table[:len(table)-1] + "_id = " + str(id)
    return sql_call(update_statement)


# create object based on given table and params
def create(table, params):
    columns = get_table_columns(table)
    insert_statement = "insert into " + table + "(" + ", ".join(params.keys()) + ") values (" + ", ".join(params.values()) + ")"
    return sql_call(insert_statement)


# delete single row from table with the given id (danger!)
def delete(table, id):
    delete_statement = "delete from " + table + " where " + table[:len(table)-1] + "_id = " + str(id)
    return sql_call(delete_statement)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():
    books = construct_db_response("select * from books where name like \"%" + request.form["query"] + "%\"", get_table_columns("books"))
    return render_template("search.html", books=books)


@app.route("/book/<int:book_id>")
def book(book_id):
    # maybe refactor this to send a json rather than a bunch of params
    book = get("books", book_id)
    if book is None:
        return render_template("book.html", book=book)
    genres = read("genres", {"book_id": book_id})
    reviews = read("reviews", {"book_id": book_id})
    avg_rating_call = sql_call("select avg(rating) from reviews where book_id = " + str(book_id))
    
    if len(avg_rating_call) > 0:
        # lol this sux
        avg = avg_rating_call[0]
        avg_rating = avg[0]
        return render_template("book.html", book=book, genres=genres, reviews=reviews, avg_rating=avg_rating)

    return render_template("book.html", book=book, genres=genres, reviews=reviews)


@app.route("/create_book", methods=["GET", "POST"])
def create_book():
    #if request.method == "POST":
    #    name = request.form["name"]
    #    price = request.form["price"]
    #    author = request.form["author"]
    #    year = request.form["year"]
    #    url = request.form["url"]
    #    created = create("books", {
    #        "name": name,
    #        "price": price,
    #        "author": author,
    #        "year": year,
    #        "url": url,
    #    })
    #    return created
    #else:
        return render_template("create_book.html")


@app.route("/create_review", methods=["GET", "POST"])
def create_review():
    return render_template("create_review.html")


@app.route("/create_genre", methods=["GET", "POST"])
def create_genre():
    return render_template("create_genre.html")

