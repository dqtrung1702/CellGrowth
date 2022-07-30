import redis
from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'GENERATE_A_SECRET_THEN_PLACE_HERE'

@app.route('/')
def hello():
    if 'code' in session:
      print(session['code'])
    session['code'] = 'my-code'

    return 'Hello'

if __name__ == '__main__':
    app.run()