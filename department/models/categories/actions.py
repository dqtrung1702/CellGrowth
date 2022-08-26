from flask import Flask
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://root:pass12345@10.14.119.41:27018/test?authSource=admin"
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