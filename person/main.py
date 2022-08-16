#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from config import Config
from models.database import person
from flask_cors import CORS
from modules.Basic import route_basic

app = Flask(__name__) # khởi tạo app
CORS(app)
app.config.from_object(Config) # đưa các thông tin từ config vào app

person.init_app(app)

app.register_blueprint(route_basic)

@app.route('/')
def index():
    return 'The Department services that provides descriptions of the nodes on organization tree.'

if __name__ == '__main__':    
   app.run(Config.PERSON_IP, Config.PERSON_PORT, debug=Config.PERSON_DEBUG_MODE)
