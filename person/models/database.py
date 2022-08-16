from flask_pymongo import PyMongo
person = PyMongo()
from datetime import date
from dateutil import tz
import pytz
local_zone = tz.tzlocal()

class transf:    
    def __init__(self, list):
        self.list = list
    def json_str(self):
        '''truyền vào list chứa date trả ra list tương ứng nhưng date được format thành str'''
        result = []
        for row in self.list:
            line = {}
            for key,val in row.items():
                value = val.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%Y-%m-%d,%H:%M:%S') if isinstance(val, date) else str(val,'utf-8') if isinstance(val, bytes) else val                
                line.update({key:value}) 
            result.append(line)
        return result
class transf2:    
    def __init__(self, dict):
        self.dict = dict
    def json_str(self):
        '''truyền vào dict chứa date trả ra dict tương ứng nhưng date được format thành str'''
        result = {}
        for key,val in dict.items():
            value = val.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%Y-%m-%d,%H:%M:%S') if isinstance(val, date) else str(val,'utf-8') if isinstance(val, bytes) else val                
            result.update({key:value})
        return result