from flask import Flask, redirect, request, url_for, render_template, jsonify
import model
import re
import random
import os

app = Flask(__name__)
# app.secret_key = '123456'
mydb = model.DatabaseConnection()

def is_valid_email(email):
    # Mẫu regex để kiểm tra email hợp lệ
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # Sử dụng hàm match để kiểm tra email có khớp với regex không
    if re.match(email_regex, email):
        return True
    else:
        return False

PAGE_SESSION = {
    'current': 0,
    'sku': None,
}

LOGIN_SESSION = {
    'username': None
}

COVER = []

cover_path = './static/resources'
files = os.listdir(cover_path)

for f in files:
    COVER.append(f)

full_books_data = list()
books_data = list()

def data_in_page(page_number):
    global books_data

    uplimit = page_number * 25
    lowerlimit = uplimit - 25 

    if uplimit > len(books_data):
        uplimit = len(books_data) - 1

    return books_data[lowerlimit:uplimit]

@app.route('/')
def homepage():
    global books_data
    global full_books_data

    books_data_x = mydb.getTableData('book', ['sku', 'title', 'author', 'price', 'score'])
    books_data_y = []

    for book in books_data_x:
        data = {
            'sku': book[0],
            'title': book[1],
            'author': book[2],
            'price': book[3],
            'review_score': book[4],
            'cover': COVER[random.randint(0, len(COVER) - 1)]
        }
        books_data_y.append(data)

    books_data = books_data_y.copy()
    full_books_data = books_data_y.copy()

    return redirect(url_for('pagination', page_number=1))

@app.route('/page=<page_number>')
def pagination(page_number):
    if LOGIN_SESSION['username']:
        username = LOGIN_SESSION['username']
    else:
        username = None
    data = data_in_page(int(page_number))

    if books_data:
        max_page = len(books_data) // 25
    else:
        max_page = 1

    if LOGIN_SESSION['username']:
        username = LOGIN_SESSION['username']
    else:
        username = None

    return render_template('homepage.html',username=username, book_data=data, page_number=int(page_number), max_page=max_page)

@app.route('/<sku>')
def product_page(sku):
    global PAGE_SESSION
    PAGE_SESSION['current'] = 1
    PAGE_SESSION['sku'] = sku

    if LOGIN_SESSION['username']:
        username = LOGIN_SESSION['username']
    else:
        username = None

    return render_template('product_page.html', username=username)

@app.route('/login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        if PAGE_SESSION['current'] == 0:
            redirURL = '/'
        else:
            redirURL = url_for('product_page', sku=PAGE_SESSION['sku'])

        username = request.form.get('username')
        passwd = request.form.get('password')

        info = mydb.searchInTable('user', ['username'], (username, ))
        if info:
            info = info[0]
            if passwd == info[-1]:
                LOGIN_SESSION['username'] = username
                return redirect(redirURL)
            else:
                return redirect(redirURL)
        else:
            return redirect(redirURL)

@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        if PAGE_SESSION['current'] == 0:
            redirURL = '/'
        else:
            redirURL = url_for('product_page', sku=PAGE_SESSION['sku'])

        username = request.form.get('username')
        passwd = request.form.get('password')
        email = request.form.get('email')
        repasswd = request.form.get('repassword')

        if passwd == repasswd:

            info = mydb.searchInTable('user', ['username'], (username,))

            if info is None:
                mydb.insertTable('user', [(username, email, passwd)])
                LOGIN_SESSION['username'] = username
                return redirect(redirURL)
            else:
                return redirect(redirURL)

        else:
            return redirect(redirURL)        


@app.route('/logout')
def logout():
    global LOGIN_SESSION

    if PAGE_SESSION['current'] == 0:
        redirURL = '/'
    else:
        redirURL = url_for('product_page', sku=PAGE_SESSION['sku'])

    if LOGIN_SESSION['username']:

        LOGIN_SESSION['username'] = None
        return redirect(redirURL)
    else:
        return redirect(redirURL)

@app.route('/search=<content>', methods=['POST'])
def search(content: str):
    global books_data
    search_value = content.lower()

    search_book_data = [book for book in full_books_data if search_value in book['title'].lower()]
    books_data = search_book_data.copy()

    return jsonify({
        'status': 'Everything okay!',
        'redirectURL': url_for('pagination', page_number=1),
    })

@app.route('/sort=<value>', methods=['POST'])
def sort(value):
    global books_data
    value = int(value)

    view_options = ['order_price_ascending', 'order_price_descending', 'order_title_ascending', 'order_title_descending']

    books_data_x = mydb.getTableData(view_options[value - 1], ['sku', 'title', 'author', 'price', 'score'])
    books_data_y = []

    print(books_data[:5])

    for book in books_data_x:
        data = {
            'sku': book[0],
            'title': book[1],
            'author': book[2],
            'price': book[3],
            'review_score': book[4],
            'cover': COVER[random.randint(0, len(COVER) - 1)]
        }
        books_data_y.append(data)

    books_data = books_data_y.copy()

    print(books_data[:5])

    return jsonify({
        'status': 'Everything okay!',
        'redirectURL': url_for('pagination', page_number=1),
    })
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5055)