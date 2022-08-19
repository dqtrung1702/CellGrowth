#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from config import Config
from models.database import person
from flask_cors import CORS
from modules.PersonBasic import route_basic
from modules.PersonPhone import route_phone
from modules.PersonEmail import route_email
from modules.PersonName import route_name
from flask_session import Session
app = Flask(__name__) # khởi tạo app
CORS(app)
app.config.from_object(Config) # đưa các thông tin từ config vào app
Session(app) # khởi tạo Flask-Session object sau khi app đã có config
person.init_app(app)

app.register_blueprint(route_basic)
app.register_blueprint(route_phone)
app.register_blueprint(route_email)
app.register_blueprint(route_name)

@app.route('/')
def index():
    return 'The Person services that provides information of the people.'

if __name__ == '__main__':    
   app.run(Config.PERSON_IP, Config.PERSON_PORT, debug=Config.PERSON_DEBUG_MODE)
