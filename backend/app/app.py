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

author = set()
category = set()

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
    global author
    global category

    books_data_x = mydb.getTableData('book', ['sku', 'title', 'author', 'price', 'score', 'category'])
    books_data_y = []

    for book in books_data_x:
        data = {
            'sku': book[0],
            'title': book[1],
            'author': book[2],
            'price': book[3],
            'review_score': book[4],
            'cover': COVER[random.randint(0, len(COVER) - 1)],
            'category': book[-1]
        }
        author_x = data['author'].strip().split(',')

        for a in author_x:
            if a in "                   ":
                author_x.remove(a)
        

        author.update(author_x)
        category.add(data['category'])

        books_data_y.append(data)

    books_data = books_data_y.copy()
    full_books_data = books_data_y.copy()

    return redirect(url_for('pagination', page_number=1))

"""Hiển thị phân trang"""
@app.route('/page=<page_number>')
def pagination(page_number):
    if LOGIN_SESSION['username']:
        username = LOGIN_SESSION['username']
    else:
        username = None
    data = data_in_page(int(page_number))
    print(data)
    if books_data:
        max_page = len(books_data) // 25
    else:
        max_page = 1

    if LOGIN_SESSION['username']:
        username = LOGIN_SESSION['username']
    else:
        username = None

    return render_template(
        'homepage.html',
        username=username, 
        book_data=data, 
        page_number=int(page_number), 
        max_page=max_page, 
        genre=category, 
        author=author
    )

"""Định hướng trang sản phẩm chi tiết"""
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

    if value == 1:
        books_data = sorted(books_data, key=lambda x: x['price'])
    elif value == 2:
        books_data = sorted(books_data, key=lambda x: x['price'], reverse=True)
    elif value == 3:
        books_data = sorted(books_data, key=lambda x: x['title'])
    elif value == 4:
        books_data = sorted(books_data, key=lambda x: x['title'], reverse=True)

    print(books_data[:5])

    return jsonify({
        'status': 'Everything okay!',
        'redirectURL': url_for('pagination', page_number=1),
    })

@app.route('/filter', methods=['POST'])
def filter():
    global books_data

    if request.method == 'POST':
        min_price = request.form.get('min-price')
        max_price = request.form.get('max-price')
        
        min_price = float(min_price) if min_price else 0
        max_price = float(max_price) if max_price else 0

        genre = request.form.get('category')
        author = request.form.get('author')
        review_score = request.form.get('review')

        review_score = int(review_score) if review_score else 0

        print({
            1: min_price,
            2: max_price,
            3: genre,
            4: author,
            5: review_score,
        })

        books_data = []
        for book in full_books_data:
            check = True
            if (max_price != 0 or min_price != 0) and (max_price >= min_price) and (min_price >= 0):
                if min_price <= float(book['price']) <= max_price:
                    check = True
                else:
                    continue

            if genre != 'all':
                if genre in book['category']:
                    check = True
                else:
                    continue

            if author != 'all':
                if author in book['author']:
                    check = True
                else:
                    continue
            
            if review_score != 0:
                score = 3 if book['review_score'] == 5 else (2 if book['review_score'] >= 4 else (1 if book['review_score'] >= 3 else -1))
                if score == review_score:
                    check = True
                else:
                    continue
            if check:
                books_data.append(book)

        print('Filter Function: ')
        print(books_data[:5])
        return redirect(url_for('pagination', page_number=1))

        

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)