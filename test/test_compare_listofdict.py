l1 = [{'b':2},{'a':1} ] 
l2 = [{'b':2}, {'a':1}] 
 
pairs = zip(l1, l2)


print(any(x != y for x, y in pairs))