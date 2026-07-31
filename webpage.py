from flask import Flask, render_template, request
from datetime import datetime
import sqlite3 as sql
# if this ends up being bigger should probably use a mysql connection

# TODO:
# Extras, to go above and beyond or to develop later
# - Generic date formatter? Treat this like an extra
# - Restrict resubmission of forms to create multiple of one object
# - Confirm layer for deleting objects
# - Combine create and edit, if {{table}}_id is given edit, else create
# - Research why all values after space aren't filled into the text boxes in edit
# - Safeguard deletion of nonexistent id
# - Delete all linked items when an object is deleted, like reviews and genres when deleting a book

app = Flask(__name__)
connection_string = "./final_project_db.db"

# I think it's fine to keep this dumb, handling can be done higher up
def sql_call(query):
    con = sql.connect(connection_string)
    cur = con.cursor()

    result = cur.execute(query)
    con.commit()
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
    
    values = []
    for i in params:
        if i["needs_escape"]:
            values.append(i["column"] + " = '" + str(i["value"]) + "'")
        else:
            values.append(i["column"] + " = " + str(i["value"]))
    
    update_statement += ", ".join(values)
    update_statement += " where " + table[:len(table)-1] + "_id = " + str(id)
    sql_call(update_statement)


# create object based on given table and params
def create(table, params):
    # need id, no autoincrement in sqlite that I'm aware of, so we'll manually calculate it here
    count_result = sql_call("select max(" + table[:len(table)-1] + "_id) from " + table)
    new_id = count_result[0][0] + 1

    columns = get_table_columns(table)

    # construct insert with escaping
    values = []
    for i in params:
        if i["needs_escape"]:
            values.append("'" + i["value"] + "'")
        else:
            values.append(i["value"])

    insert_statement = "insert into " + table + " values (" + str(new_id) + ", " + ", ".join(values) + ")"
    sql_call(insert_statement)


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
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        author = request.form["author"]
        year = request.form["year"]
        url = request.form["url"]
        # kinda sucks but gotta do it
        create("books", [
            dict(
                value=name,
                needs_escape=True
            ),
            dict(
                value=price,
                needs_escape=False
            ),
            dict(
                value=author,
                needs_escape=True
            ),
            dict(
                value=year,
                needs_escape=False
            ),
            dict(
                value=url,
                needs_escape=True
            ),
        ])
        return render_template("home.html", message="Book created successfully!")
    else:
        return render_template("create_book.html")


@app.route("/edit_book/<string:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        author = request.form["author"]
        year = request.form["year"]
        url = request.form["url"]
        update("books", book_id, [
            dict(
                column="name",
                value=name,
                needs_escape=True
            ),
            dict(
                column="price",
                value=price,
                needs_escape=False
            ),
            dict(
                column="author",
                value=author,
                needs_escape=True
            ),
            dict(
                column="year",
                value=year,
                needs_escape=False
            ),
            dict(
                column="url",
                value=url,
                needs_escape=True
            ),
        ])
        return book(book_id)
    else:
        _book = get("books", book_id)
        return render_template("edit_book.html", book=_book)


@app.route("/delete_book/<string:book_id>", methods=["GET", "POST"])
def delete_book(book_id):
    delete("books", book_id)
    return render_template("home.html")


@app.route("/create_review/<string:book_id>", methods=["GET", "POST"])
def create_review(book_id):
    if request.method == "POST":
        title = request.form["title"]
        name = request.form["name"]
        rating = request.form["rating"]
        description = request.form["description"]
        # kinda sucks but gotta do it
        create("reviews", [
            dict(
                value=book_id,
                needs_escape=False
            ),
            dict(
                value=title,
                needs_escape=True
            ),
            dict(
                value=name,
                needs_escape=True
            ),
            dict(
                value=rating,
                needs_escape=False
            ),
            dict(
                value=description,
                needs_escape=True
            ),
            dict(
                value=datetime.today().strftime('%d-%m-%Y'),
                needs_escape=True
            ),
        ])
        return book(book_id)
    else:
        return render_template("create_review.html")


@app.route("/edit_review/<string:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    _review = get("reviews", review_id)
    if request.method == "POST":
        title = request.form["title"]
        name = request.form["name"]
        rating = request.form["rating"]
        description = request.form["description"]
        # kinda sucks but gotta do it
        update("reviews", review_id, [
            dict(
                column="title",
                value=title,
                needs_escape=True
            ),
            dict(
                column="reviewer",
                value=name,
                needs_escape=True
            ),
            dict(
                column="rating",
                value=rating,
                needs_escape=False
            ),
            dict(
                column="description",
                value=description,
                needs_escape=True
            ),
            dict(
                column="date",
                value=datetime.today().strftime('%d-%m-%Y'),
                needs_escape=True
            ),
        ])
        return book(_review["book_id"])
    else:
        return render_template("edit_review.html", review=_review)


@app.route("/delete_review/<string:review_id>", methods=["GET", "POST"])
def delete_review(review_id):
    review = get("reviews", review_id)
    book_id = review["book_id"]
    delete("reviews", review_id)
    return book(book_id)


@app.route("/create_genre/<string:book_id>", methods=["GET", "POST"])
def create_genre(book_id):
    if request.method == "POST":
        genre = request.form["genre"]
        # kinda sucks but gotta do it
        create("genres", [
            dict(
                value=genre,
                needs_escape=True
            ),
            dict(
                value=book_id,
                needs_escape=False
            ),
        ])
        return book(book_id)
    else:
        return render_template("create_genre.html")


@app.route("/edit_genre/<string:genre_id>", methods=["GET", "POST"])
def edit_genre(genre_id):
    _genre = get("genres", genre_id)
    if request.method == "POST":
        genre = request.form["genre"]
        # kinda sucks but gotta do it
        update("genres", genre_id, [
            dict(
                column="genre",
                value=genre,
                needs_escape=True
            ),
        ])
        return book(_genre["book_id"])
    else:
        return render_template("edit_genre.html", genre=_genre)


@app.route("/delete_genre/<string:genre_id>", methods=["GET", "POST"])
def delete_genre(genre_id):
    genre = get("genres", genre_id)
    book_id = genre["book_id"]
    delete("genres", genre_id)
    return book(book_id)

