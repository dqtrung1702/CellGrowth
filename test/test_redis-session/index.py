import redis
from flask import Flask, session
from flask_session import Session
app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY'

# Configure Redis for storing the session data on the server-side
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://10.14.119.41:6379')
Session(app)
@app.route('/')
def hello():
    if 'code' in session:
      print(session['code'])
    session['code'] = 'my-code'

    return 'Hello'


if __name__ == '__main__':
    app.run()