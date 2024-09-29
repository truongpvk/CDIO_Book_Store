from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thay đổi secret key cho bảo mật

# Tạm thời lưu trữ người dùng (thay thế bằng cơ sở dữ liệu thực tế)
users = {}
purchase_counts = {}  # Giả định lưu số lượt mua của mỗi tài khoản

# Trang chính (trang login)
@app.route('/')
def home():
    return render_template('product_page.html')  # Tải trang sản phẩm

# Đăng nhập
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Kiểm tra đăng nhập
    if username in users and users[username] == password:
        session['username'] = username  # Lưu tên người dùng vào session
        flash("Đăng nhập thành công!", "success")
        return redirect(url_for('product_page_user'))  # Chuyển đến trang sản phẩm của người dùng
    else:
        flash("Tên đăng nhập hoặc mật khẩu không đúng hoặc chưa có tài khoản!", "error")
        return redirect(url_for('home'))  # Quay lại trang chính

# Đăng ký
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    repassword = request.form.get('repassword')
    
    # Kiểm tra đăng ký
    if password == repassword:
        if username not in users:
            users[username] = password  # Thêm người dùng vào danh sách
            purchase_counts[username] = 0  # Khởi tạo số lượt mua
            flash("Đăng ký thành công! Bạn có thể đăng nhập.", "success")
            return redirect(url_for('home'))  # Quay lại trang chính

        else:
            flash("Tài khoản đã tồn tại!", "error")
    else:
        flash("Mật khẩu không khớp!", "error")
    
    return redirect(url_for('home'))  # Quay lại trang chính

# Trang sản phẩm của người dùng
@app.route('/product_page_user')
def product_page_user():
    username = session.get('username')  # Lấy tên người dùng từ session
    if not username:  # Kiểm tra xem người dùng có đăng nhập không
        return redirect(url_for('home'))  # Nếu không, chuyển về trang chính

    purchase_count = purchase_counts.get(username, 0)  # Lấy số lượt mua
    return render_template('product_page_user.html', username=username, purchase_count=purchase_count)  # Truyền thông tin đến template

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)  # Xóa tên người dùng khỏi session
    flash("Bạn đã đăng xuất thành công!", "success")  # Thông báo đăng xuất
    return redirect(url_for('home'))  # Quay lại trang chính

@app.route('/register', methods=['POST'])
def register():
    # Xử lý đăng ký (kiểm tra thông tin, lưu vào cơ sở dữ liệu, v.v.)
    
    # Nếu đăng ký thành công
    flash('Đăng ký thành công', 'success')  # Thông báo thành công
    return redirect(url_for('product_page'))  # Chuyển hướng đến trang sản phẩm
if __name__ == '__main__':
    app.run(debug=True)
