from flask import Flask
from config import Config
from models.database import db
from modules.Authentication import authentication

app = Flask(__name__) # khởi tạo app
app.config.from_object(Config) # đưa các thông tin từ config vào app

app.register_blueprint(authentication)

@app.route('/')
def index():
    return 'The User Authentication and Authorization(UAA) services provides role-based access control (RBAC) for both internal services and user-facing applications. Although the UAA can use an internal identity store (e.g. MySQL or PostgreSQL), typically an external identity provider (IdP) is used.'

if __name__ == '__main__':
    app.run(Config.UAA_IP, Config.UAA_PORT,Config.UAA_DEBUG_MODE)
