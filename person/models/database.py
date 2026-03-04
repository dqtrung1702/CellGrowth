from flask_pymongo import PyMongo
person = PyMongo()
from datetime import date
from dateutil import tz
import pytz
from bson import json_util
local_zone = tz.tzlocal()

class transf:    
    def __init__(self, obj):
        self.obj = obj
    def jsonflobject(self):
        '''truyền vào list chứa date trả ra list tương ứng nhưng date được format thành str'''
        result = []
        for row in self.obj:
            line = {}
            for key,val in row.items():
                if isinstance(val, date):
                    value = val.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%d/%m/%Y,%H:%M:%S')  
                elif isinstance(val, bytes):
                    value = str(val,'utf-8')
                elif isinstance(val, list):
                    value = transf(val).jsonflobject()
                elif isinstance(val, dict):
                    value = transf(val).jsonfdobject()
                else:
                    value = val
                line.update({key:value}) 
            result.append(line)
        return result
    def jsonfdobject(self):
        '''truyền vào dict chứa date trả ra dict tương ứng nhưng date được format thành str'''
        result = {}
        for key,val in self.obj.items():
            if isinstance(val, date):
                value = val.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%d/%m/%Y,%H:%M:%S')  
            elif isinstance(val, bytes):
                value = str(val,'utf-8')
            elif isinstance(val, list):
                value = transf(val).jsonflobject()
            elif isinstance(val, dict):
                value = transf(val).jsonfdobject()
            else:
                value = val
            result.update({key:value})
        return result
    def jsonfobject(self):
        if isinstance(self.obj, date):
            result = self.obj.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%d/%m/%Y,%H:%M:%S')  
        elif isinstance(self.obj, bytes):
            result = str(self.obj,'utf-8')
        elif isinstance(self.obj, list):
            result = transf(self.obj).jsonflobject()
        elif isinstance(self.obj, dict):
            result = transf(self.obj).jsonfdobject()
        else:
            result = self.obj
        return result


class transf2:
    """
    Lightweight converter used by some routes to return JSON-serializable data.
    """
    def __init__(self, obj):
        self.obj = obj

    def json_str(self):
        return json_util.loads(json_util.dumps(self.obj))
