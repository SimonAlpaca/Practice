# -*- coding: utf-8 -*-

# In[map function]

def convert_km_mile(km):
    mile = km / 1.61
    mile = "%2.2f mile" %mile                           # same format as print
    return mile

def market_value(price, quantity):
    return price*quantity

def map_show():
    global list1
    
    list1 = [1,5,3,2]
    list_mile = list(map(convert_km_mile,list1))        # put the whole list into definition
    print(list_mile)
    
    list2 = [10001, 10002, 10003]                       # convert the whole list from int to str
    
    list_2str = list(map(str, list2))
    
    print(list_2str)
    
    list3 = [3.52, 1.25, 15.66]
    list4 = [50000, 100000, 10000]
    list_marketvalue = list(map(market_value, list3, list4))
    
    print(list(map(int, list_marketvalue)))
    
print("***Map***")    
map_show()

# In[reduce fuction]

def sum_convert_km_mile(x,y):
    mile = x + y / 1.61     
    return mile

def check_all_true(x,y):
    if x > 1 and y > 1:
        return True
    else:
        return False

def reduce_show():
    import functools
    list1.insert(0,0)                                   # needs to insert 0 into first data, otherwise it will be 1 + 5/1.61
    print("%2.2f" %functools.reduce(sum_convert_km_mile, list1))  # reduce gets a cumulative number
    
    list2 = [1, 4, 5, 7]
    print("Are all values > 1? : %s" %functools.reduce(check_all_true, list2))  # check if all values are true
    
print("***Reduce***")
reduce_show()

# In[filter function]

def not_empty(s):                                   # return false if "s" or "s.strip()" is false; None is false in s
    return s and s.strip()                          # strip to remove space before and after string

def filter_list(s):
    if s in ["A", "B"]:
        return False
    else:
        return True
    
def filter_show():
    list3 = ["A", " ","B  ", " C", "D", "", None]
    print("Before: ", list3)
    
    list3 = list(filter(not_empty, list3))              # filter to remove values if return False
    print("After filtering empty: ", list3)
    
    list3 = list(map(not_empty, list3))                 # filter to apply definition to each value
    print("After map: ", list3)

    list3 = list(filter(filter_list, list3))
    print("After filtering A and B: ", list3)
    
print("***Filter***")
filter_show()

# In[sorted function]

def power(x):
    return x*x

def take_second(x):
    return x[1]                                # return the 2nd value of the list

def sorted_show():
    list4 = [-1, 5, 8,-20, 12]
    print(sorted(list4))
    print(sorted(list4,reverse=True))             # decending order
    print(sorted(list4, key = abs))               # sort according to abs as a def
    print(sorted(list4, key = power))             # sort according to the def
    
    list5 = [(3,1),(2,2),(5,0)]
    print(sorted(list5))                           # sort using the 1st value
    print(sorted(list5, key = take_second))        # sort according to the def
    
    list6 = ["bob", "Zoe", "pete"]
    print(sorted(list6))                           # sort according to upper and lower                   
    print(sorted(list6,key = str.lower))           # sort ignoring upper and lower

print("***Sorted***")
sorted_show()

# In[test speed of reduce]

import functools
import time

def reduce_alltrue(x, y):
    if x and y:
        return True
    
    else:
        return False

def loop_alltrue(list):
    check_true = True
    for i in list:
        if check_true:
            if i:
                check_true = True
            else:
                check_true = False
    return check_true

print("***Test Speed of Reduce and Loop***")
list_1 = [True] * 1000000
list_1.append(False)

print("***Reduce***")
timer_start = time.perf_counter()

reduce_check = functools.reduce(reduce_alltrue, list_1)

timer_end = time.perf_counter()
print(reduce_check)
print(timer_end - timer_start)

print("***Loop***")
timer_start_2 = time.perf_counter()

loop_check = loop_alltrue(list_1)

timer_end_2 = time.perf_counter()
print(loop_check)
print(timer_end_2 - timer_start_2)