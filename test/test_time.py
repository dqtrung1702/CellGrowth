from datetime import datetime 
from datetime import timedelta 
from dateutil import tz
import pytz
import time

print(time.tzname)
print(datetime.now())
print(datetime.utcnow())




dt_utc = datetime.utcnow()
dt_utc = dt_utc.replace(tzinfo=pytz.UTC)  
local_zone = tz.tzlocal()
dt_local = dt_utc.astimezone(local_zone)
print('dt_local',dt_local)
dt_utc2 = dt_local.astimezone(pytz.utc)
print(dt_utc2)


print(datetime.strftime(dt_utc2,'%d/%m/%Y %H:%M:%S'))
print(datetime.strptime('20/08/2021 23:59:59','%d/%m/%Y %H:%M:%S'))
print(datetime.now()- timedelta(days=1))
# print(datetime.strptime("222/2/222", "%d/%m/%Y"))
try:
    res = datetime.strptime("202/08/2021", "%d/%m/%Y")
except ValueError as e:
    res = e
print(res)
