#!/usr/bin/env python
# encoding: utf-8
from flask import Flask
from config import Config
from models.database import dept
from flask_cors import CORS
from modules.Department import route_dept
from modules.Action import route_action
from flask_session import Session
app = Flask(__name__) # khởi tạo app
CORS(app)
app.config.from_object(Config) # đưa các thông tin từ config vào app
Session(app) # khởi tạo Flask-Session object sau khi app đã có config
dept.init_app(app)


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

app.register_blueprint(route_dept)
app.register_blueprint(route_action)

@app.route('/')
def index():
    return 'The Department services that provides descriptions of the nodes on organization tree.'

if __name__ == '__main__':    
   app.run(Config.DEPT_IP, Config.DEPT_PORT, debug=Config.DEPT_DEBUG_MODE)
