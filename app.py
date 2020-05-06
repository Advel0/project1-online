import os

import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask import Flask, render_template, request, redirect, jsonify, session, url_for


engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind = engine))

app = Flask(__name__)
app.secret_key = 'lol'

@app.route("/")
def index():
    if 'user_id' not in session:
        return render_template('index.html')

    return search()

@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method=='GET':
        if 'user_id' not in session:
            return 'Ay shalunishka!'
        return render_template('search_page.html', id=session['user_id'])
    username = request.form.get('username')
    password = request.form.get('password')
    user = db.execute("SELECT * FROM users WHERE username=:name AND password=:password",{'name':username, 'password':password}).fetchone()
    if user:
        session['user_id'] = user.id
        id = user.id
        return render_template('search_page.html', id=id)

    return 'TRY AGAIN'

@app.route('/finded-books/<int:id>', methods=['POST'])
def find_book(id):
    books=[]
    request_ = request.form.get('book_name')
    books_from_db = db.execute("SELECT * FROM books WHERE title LIKE :request OR author LIKE :request OR isbn LIKE :request;", {'request': '%'+request_+'%'}).fetchall()
    for book in books_from_db:
        books.append(book)
    return render_template('finded-books.html', books=books, id=id)

@app.route('/finded-books/<int:book_id>/<int:id>')
def book(book_id, id):
    average_mark = db.execute("SELECT AVG(mark) FROM marks WHERE book_id=:book_id;", {"book_id": book_id}).fetchone()
    book = db.execute("SELECT * FROM books WHERE id=:id;", {'id':book_id}).fetchone()
    reviews = db.execute("SELECT mark,username,text FROM reviews JOIN marks ON reviews.book_id=marks.book_id JOIN users ON reviews.user_id=users.id WHERE reviews.book_id=:book_id;", {'book_id':book_id})
    if average_mark.avg:
        average_mark = round(average_mark.avg,2)
    else:
        average_mark = 'Noone marked this book yet'
    info = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "O2u7Kug97EzDAdbpNr5syg", "isbns": book.isbn}).json()
    return render_template('book.html', book=book, reviews=reviews, id=id, average_mark=average_mark, info=info)

@app.route('/none/<int:book_id>/<int:id>', methods=['POST'])
def create_comment(book_id, id):
    comment_exist = db.execute("SELECT * FROM reviews WHERE user_id=:user_id AND book_id=:book_id;", {'user_id':id, 'book_id':book_id}).fetchone()
    if comment_exist:
        return 'Comment already exist'
    text = request.form.get('cont')
    db.execute("INSERT INTO reviews(book_id, user_id, text) VALUES(:book_id, :user_id, :text);", {'book_id':book_id, 'user_id':id, 'text':text})
    mark = request.form.get('mark')
    db.execute("INSERT INTO marks(user_id, book_id, mark) VALUES(:user_id,:book_id,:mark);", {"user_id":id, "book_id":book_id, "mark":mark})
    db.commit()
    return 'Comment Created'

@app.route('/create-account')
def create_account():
    return render_template('create_account.html')

@app.route('/create-account/smth', methods=['POST'])
def apply_created_account():
    try:
        username = request.form.get('new_username')
        password = request.form.get('new_user_password')
        db.execute("INSERT INTO users(username, password) VALUES(:username, :password);", {'username': username, 'password':password})
        db.commit()
    except:
        return 'Account with similar urename is already exist'
    return render_template('creating_account_result.html')

@app.route('/finded-books/mark_is_sent/<int:id>/<int:book_id>', methods=['POST'])
def set_mark(id, book_id):

    return str(mark)

@app.route('/api/<string:isbn>')
def get_info(isbn):
    book = db.execute('SELECT * FROM books WHERE isbn=:isbn', {'isbn':isbn}).fetchone()
    if book:
        book_info = jsonify(
                    {
                    'isbn':book.isbn,
                    'title':book.title,
                    'author':book.author,
                    'year':book.year,
                    }
        )
        return book_info
    return '404'

@app.route('/quit')
def quit_account():
    if 'user_id' in session:
        session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
