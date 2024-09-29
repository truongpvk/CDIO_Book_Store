import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder=os.path.join(
    os.path.dirname(__file__), 'templates'))

# Cấu hình cơ sở dữ liệu
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/saleshopdb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

# Khởi tạo các đối tượng
db = SQLAlchemy(app)
login_manager = LoginManager(app)
# Chuyển hướng đến trang chủ nếu không đăng nhập
login_manager.login_view = 'homepage'


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def homepage():
    # Trang chủ sẽ hiển thị biểu mẫu đăng ký và đăng nhập
    return render_template('homepage.html')


@app.route('/homepage_user')
@login_required
def homepage_user():
    return render_template('homepage_user.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    repassword = request.form['repassword']

    # Kiểm tra xem mật khẩu có khớp không
    if password != repassword:
        flash('Mật khẩu không khớp. Vui lòng thử lại.', 'danger')
        return redirect(url_for('homepage'))

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        flash('Tên người dùng hoặc email đã tồn tại. Vui lòng chọn cái khác.', 'danger')
        return redirect(url_for('homepage'))

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash('Đăng ký thành công! Bạn có thể đăng nhập.', 'success')
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # login_user(user)
        flash('Đăng nhập thành công!', 'success')
        # Chuyển hướng tới homepage_user.html
        return redirect(url_for('homepage_user'))
    else:
        flash('Tên người dùng hoặc mật khẩu không hợp lệ.', 'danger')

    return redirect(url_for('homepage'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất thành công.')
    return redirect(url_for('homepage'))


@app.route('/test-db')
def test_db():
    try:
        # Kiểm tra xem có thể truy vấn User không
        db.session.query(User).first()
        return "Kết nối cơ sở dữ liệu thành công!"
    except Exception as e:
        return f"Kết nối thất bại: {e}"


@app.route('/test-template')
def test_template():
    return f"Templates are located at: {os.path.abspath('templates')}"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tạo bảng nếu chưa tồn tại
    app.run(debug=True)
