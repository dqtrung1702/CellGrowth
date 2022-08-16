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
                if isinstance(val, date):
                    value = val.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%d/%m/%Y,%H:%M:%S')  
                elif isinstance(val, bytes):
                    value = str(val,'utf-8')
                elif isinstance(val, list):
                    value = transf(val).json_str()
                elif isinstance(val, dict):
                    value = transf2(val).json_str()
                else:
                    value = val
                line.update({key:value}) 
                result.append(line)
        return result
class transf2:    
    def __init__(self, dict):
        self.dict = dict
    def json_str(self):
        '''truyền vào dict chứa date trả ra dict tương ứng nhưng date được format thành str'''
        result = {}
        for key,val in self.dict.items():
            if isinstance(val, date):
                value = val.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%d/%m/%Y,%H:%M:%S')  
            elif isinstance(val, bytes):
                value = str(val,'utf-8')
            elif isinstance(val, list):
                value = transf(val)
            elif isinstance(val, dict):
                value = transf2(val)
            else:
                value = val
            result.update({key:value})
        return result