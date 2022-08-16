from flask import Flask
app = Flask(__name__)

from config import Config
app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

from datetime import date
from werkzeug.wrappers import Response
import json
from bson import json_util

@app.route('/get-user', methods=['GET','POST'])
def get_user():
    if True:
        sql = '''select * from uaa."RoleDefine" ud limit 1;'''
        record = db.engine.execute(sql).mappings().all()
        result = []
        for row in record:
            line = {}
            for key,val in row.items():
                value = val.strftime('%d/%m/%Y,%H:%M:%S') if isinstance(val, date) else str(val,'utf-8') if isinstance(val, bytes) else val
                line.update({key:value}) 
            result.append(line)
        if result:
            print(type(result))
            res = json.dumps({"data": result},default=json_util.default).encode('utf-8')
    return Response(res, mimetype='application/json', status=200)

@app.route('/')
def index():
    return 'This is testing service'

if __name__ == '__main__':
    app.run('0.0.0.0', '8081', debug=True)