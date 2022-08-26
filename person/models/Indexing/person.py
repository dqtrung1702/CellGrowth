
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING, HASHED, TEXT, GEOSPHERE
# Create a connection to the MongoDB server
con = MongoClient('mongodb://root:pass12345@10.14.119.41:27018/test?authSource=admin');
# Database object
db = con.test;
# Collection object
coll = db.person;
coll.create_index([('Code', ASCENDING )], unique = True, name='Code_Idx');