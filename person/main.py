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
from modules.PersonAddress import route_address
from flask_session import Session
app = Flask(__name__) # khởi tạo app
CORS(app)
app.config.from_object(Config) # đưa các thông tin từ config vào app
Session(app) # khởi tạo Flask-Session object sau khi app đã có config
person.init_app(app)


def _ensure_redis_alive():
    redis_client = app.config.get("SESSION_REDIS")
    if not redis_client:
        raise SystemExit("SESSION_REDIS is not configured")
    try:
        redis_client.ping()
    except Exception as exc:  # pragma: no cover - defensive
        print("REDIS_HEALTHCHECK_FAIL", exc)
        raise SystemExit(1)


_ensure_redis_alive()

app.register_blueprint(route_basic)
app.register_blueprint(route_phone)
app.register_blueprint(route_email)
app.register_blueprint(route_name)
app.register_blueprint(route_address)

@app.route('/')
def index():
    return 'The Person services that provides information of the people.'

if __name__ == '__main__':    
   app.run(Config.PERSON_IP, Config.PERSON_PORT, debug=Config.PERSON_DEBUG_MODE)
