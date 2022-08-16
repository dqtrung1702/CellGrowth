import pymongo
MONGO_URI = 'mongodb://10.14.119.40:27017/test'
person = pymongo.MongoClient(MONGO_URI).test

data = [
    {
        "Name": "Mobile",
        "Code": "MOBILE"
    },
    {
        "Name": "Home",
        "Code": "HOME"
    },
    {
        "Name": "Work",
        "Code": "WORK"
    }
]
person.db.phonetype.insert_many(data)
