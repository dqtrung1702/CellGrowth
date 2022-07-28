
from flask import Flask
from config import Config
from models.database import db
from flask_migrate import Migrate
from modules.Authentication import authentication
from modules.Set import route_set
from modules.BU import route_bu
from modules.User import route_user
from modules.Role import route_role
from modules.Permission import route_permission
from modules.ImportData import route_import
from flask_cors import CORS
# Mặc dù SOP(same origin policy) có hiệu quả trong việc ngăn chặn việc truy cập trái phép từ các domain khác nhau nhưng đồng thời nó cũng ngăn cản những tương tác hợp lệ giữa các server hoặc client đáng tin cậy. Ví dụ như api.example.com và image.example.com, hai domain này chắc chắn là không cùng origin rồi.
# CORS (Cross Origin Resource Sharing) là một tính năng mới được tích hợp trong HTML5, thêm vào các HTTP headers chỉ dẫn cho trình duyệt web về sử dụng và quản lý nội dung cross-domain, cho phép lấy dữ liệu từ một trang khác thông qua XMLHttpRequest

app = Flask(__name__) # khởi tạo app
CORS(app)
app.config.from_object(Config) # đưa các thông tin từ config vào app
db.init_app(app) # đưa các giá trị tham số từ app vào db
migrate = Migrate(app, db) # thực hiện migrate bảng bằng flask_migrate, chạy lần lượt các lệnh trong list [export FLASK_APP=main.py, flask db init, flask db migrate, flask db upgrade, flask db downgrade]

app.register_blueprint(authentication)
app.register_blueprint(route_set)
app.register_blueprint(route_bu)
app.register_blueprint(route_role)
app.register_blueprint(route_permission)
app.register_blueprint(route_user)
app.register_blueprint(route_import)



@app.route('/')
def index():
    return 'The User Authentication and Authorization(UAA) services provides role-based access control (RBAC) for both internal services and user-facing applications. Although the UAA can use an internal identity store (e.g. MySQL or PostgreSQL), typically an external identity provider (IdP) is used.'

if __name__ == '__main__':
    app.run(Config.UAA_IP, Config.UAA_PORT, debug=Config.UAA_DEBUG_MODE)
