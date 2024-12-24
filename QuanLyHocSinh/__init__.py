from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.secret_key = 'abcd'  # Đặt chuỗi bí mật tại đây
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/studentmng?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app=app)


# Khởi tạo LoginManager


app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Địa chỉ SMTP của Gmail
app.config['MAIL_PORT'] = 465  # Cổng SMTP cho Gmail
app.config['MAIL_USE_SSL'] = True  # Sử dụng SSL
app.config['MAIL_USERNAME'] = 'testsender1710@gmail.com'  # Thay bằng email của bạn
app.config['MAIL_PASSWORD'] = 'eebavhhoewwggdxm'
app.config['MAIL_DEFAULT_SENDER'] = 'testsender1710@gmail.com'  # Địa chỉ email người gửi