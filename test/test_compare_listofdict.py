l1 = [{'b':2},{'a':1} ] 
l2 = [{'b':2}, {'a':1}] 
l3 = [ {'a':1},{'b':2,'c':3}] 
pairs = zip(l1, l2)
pairs2 = zip(l1, l3)

print(any(x != y for x, y in pairs)) # False là không lệch
print(any(x != y for x, y in pairs2)) # True là có lệch
#=> chỉ compare được list cùng thứ tự

# for i in l3:
#     if i == {'c':3,'b':2}:
#         print(i)
#         print({'c':3,'b':2})
#         break