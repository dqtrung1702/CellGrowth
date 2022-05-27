from __future__ import print_function
import json

from types import SimpleNamespace as Namespace

data = '{"name": "John Smith", "hometown": {"name": "New York", "id": 123}}'

x = json.loads(data, object_hook=lambda d: Namespace(**d))

# print (x.name, x.hometown.name, x.hometown.id)
print(x)