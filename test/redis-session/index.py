import redis
from flask import Flask, session

app = Flask(__name__)

app.secret_key = 'CAIS-CUR-DDAUJ'

# Configure Redis for storing the session data on the server-side
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://10.14.119.41:6379')

@app.route('/')
def hello():
    if 'code' in session:
      print(session['code'])
    session['code'] = 'my-code'

    return 'Hello'


if __name__ == '__main__':
    app.run()