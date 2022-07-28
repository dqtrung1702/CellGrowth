#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from config import Config
from models.database import db
from flask_cors import CORS
from modules.Department import route_dept

app = Flask(__name__) # khởi tạo app
CORS(app)
app.config.from_object(Config) # đưa các thông tin từ config vào app

db.init_app(app)

app.register_blueprint(route_dept)

@app.route('/')
def index():
    return 'The Department services that provides descriptions of the nodes on organization tree.'

if __name__ == '__main__':    
   app.run(Config.DEPT_IP, Config.DEPT_PORT, debug=Config.DEPT_DEBUG_MODE)
