
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING, HASHED, TEXT, GEOSPHERE
# Create a connection to the MongoDB server
con = MongoClient('mongodb://root:pass12345@10.14.119.41:27018/test?authSource=admin');
# Database object
db = con.test;
# Collection object
coll = db.department;
# Index object
# coll.drop_index("Code_Idx");
# coll.drop_index("ParentId_Idx");
# coll.drop_index("ManageId_Idx");
coll.create_index([('Code', ASCENDING ),('EFFDT', DESCENDING ),('Status')],unique = True, name='Code_Idx');
# coll.create_index([('ParentId', ASCENDING )], name='ParentId_Idx');
# coll.create_index([('ManagerId', DESCENDING )], name='ManageId_Idx');