from flask import Flask, redirect, request, url_for, render_template
import model
import re

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

LOGIN_SESSION = {
    'username': None
}

books_data = list()

def data_in_page(page_number):
    global books_data

    uplimit = page_number * 25
    lowerlimit = uplimit - 25 

    return books_data[lowerlimit:uplimit]

@app.route('/')
def homepage(username):
    global books_data

    books_data_x = mydb.getTableData('book', ['sku', 'title', 'author', 'price', 'score'])
    books_data_y = []

    for book in books_data_x:
        data = {
            'sku': book[0],
            'title': book[1],
            'author': book[2],
            'price': book[3],
            'review_score': book[4],
        }
        books_data_y.append(data)

    books_data = books_data_y.copy()

    return redirect(url_for('pagination', page_number=1, username=username))

@app.route('/page=<page_number>')
def pagination(page_number, username=None):
    data = data_in_page(int(page_number))

    if books_data:
        max_page = len(books_data) // 25
    else:
        return redirect('/')

    return render_template('homepage.html', book_data=data, page_number=int(page_number), max_page=max_page)

@app.route('/<user>')
def homepage_user(user, sort_value=1):
    global books_data

    if LOGIN_SESSION['username'] is None:
        return redirect(url_for('homepage'))
    else:
        book_option = ['order_price_ascending', 'order_price_descending', 'order_title_ascending', 'order_title_descending']
        books_data_x = mydb.getTableData(book_option[sort_value - 1], ['sku', 'title', 'author', 'price', 'score'])
        books_data_y = []

        for book in books_data_x:
            data = {
                'sku': book[0],
                'title': book[1],
                'author': book[2],
                'price': book[3],
                'review_score': book[4],
            }
            books_data_y.append(data)

        books_data = books_data_y.copy()

        return redirect(url_for('pagination_user', user=user, page_number=1))

@app.route('/<user>/page=<page_number>')
def pagination_user(user, page_number):
    data = data_in_page(int(page_number))

    if books_data:
        max_page = len(books_data) // 25
    else:
        return redirect('/')

    return render_template('homepage_user.html', book_data=data, page_number=int(page_number), max_page=max_page, username=user)

@app.route('/sort', methods=['POST'])
def user_sort_page(user):
    if request.method == 'POST':
        req_data = request.get_json()
        sort_value = req_data['option']

        print(sort_value)

        return {'yes': True}

@app.route('/login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        passwd = request.form.get('password')

        info = mydb.searchInTable('user', ['username'], (username, ))
        if info:
            info = info[0]
            if passwd == info[-1]:
                LOGIN_SESSION['username'] = username
                return redirect(url_for('homepage_user', user=username))
            else:
                error_message = "Tên đăng nhập hoặc mật khẩu không đúng!"
                return render_template('homepage.html', message=error_message, login_process=1)
        else:
            error_message = "Tên đăng nhập hoặc mật khẩu không đúng!"
            return render_template('homepage.html', message=error_message, login_process=1)

@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        passwd = request.form.get('password')
        email = request.form.get('email')
        repasswd = request.form.get('repassword')

        if passwd == repasswd:

            info = mydb.searchInTable('user', ['username'], (username,))

            if info is None:
                mydb.insertTable('user', [(username, email, passwd)])
                LOGIN_SESSION['username'] = username
                return redirect(url_for('homepage_user', user=username))
            else:
                message_signup = 'Người dùng đã tồn tại!'
                return render_template('homepage.html', message_signup=message_signup)
        else:
            message_signup = 'Mật khẩu không trùng khớp!'
            return render_template('homepage.html', message_signup=message_signup)

@app.route('/logout')
def logout():
    LOGIN_SESSION['username'] = None
    return redirect(url_for('homepage'))

@app.route('/<sku>')
def product_page(sku):
    pass

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5055)