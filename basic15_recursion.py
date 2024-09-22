# -*- coding: utf-8 -*-

import sys

# In[Recursion Error]
# Recursion: a function calling self to form a loop
def recursive_func(i):
    i = i + 1
    print(i)
    try:
        recursive_func(i)
    
    except RecursionError as e:      # cause error if the recursion limit is reached
        print("RecursionError : ", e)
        
# set recursion limit to 3200. The effect is applied to intepreter and affects all module
# the limit can't be set higher as it will cause stack overflow
sys.setrecursionlimit(3200)          
print("Recursion Limit : ", sys.getrecursionlimit())

recursive_func(0) 