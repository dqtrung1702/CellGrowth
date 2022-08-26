import pymongo
MONGO_URI = 'mongodb://root:pass12345@10.14.119.41:27018/test?authSource=admin'
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
