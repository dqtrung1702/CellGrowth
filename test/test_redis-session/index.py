import os
import redis
from flask import Flask, session
from flask_session import Session

app = Flask(__name__)

app.secret_key = os.getenv('TEST_SESSION_SECRET', 'BAD_SECRET_KEY')

# Configure Redis for storing the session data on the server-side
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_NAME'] = os.getenv('TEST_SESSION_COOKIE', 'test_session')
redis_url = (
    os.getenv('TEST_REDIS_URL')
    or os.getenv('REDIS_URL')
    or 'rediss://:change-me@localhost:6380/15'
)
app.config['SESSION_REDIS'] = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
Session(app)


@app.route('/')
def hello():
    if 'code' in session:
        print(session['code'])
    session['code'] = 'my-code'
    return 'Hello'


if __name__ == '__main__':
    app.run()
