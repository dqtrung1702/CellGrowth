from flask import Flask
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://10.14.119.41:27017/test"
dept = PyMongo(app)
data = [
    {
        "Name": "New",
        "Type": "DEPT",
        "Code": "NEW"
    },
    {
        "Name": "Change Manager",
        "Type": "DEPT",
        "Code": "CM"
    },
    {
        "Name": "Change Parent Department",
        "Type": "DEPT",
        "Code": "CP"
    }
]
dept.db.action.insert_many(data)