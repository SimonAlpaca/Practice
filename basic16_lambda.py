# -*- coding: utf-8 -*-

# Lambda is a kind of anonymous function which no name is assigned to it.
# It is for reducing number of def.
# It is created when the line is executed and die afterwards, while def is created from the start and die after the program ends.
# It saves memory in theory while CPU usage is similar.
# https://discuss.python.org/t/what-is-the-purpose-of-lambda-expressions/12415/7

def lambda1():
    
    list1 = [1,2,3,4]
    
    x = lambda a : a + 10
    print(x(5))
    
    print(list(map(lambda a : a + 10, list1)))
    
    #######
    
    def y(a):
        return a + 10
    
    print(y(5))
    
    print(list(map(y, list1)))
    
    
def lambda2():
    
    x = lambda a, b : a * b
    print(x(5, 6))
    
    #######
    
    def y(a,b):
        return a * b
    
    print(y(5,6))
    
def lambda3():
    
    def myfunc(n): 
        return lambda a : a * n
    
    mydoubler = myfunc(2)
    mytripler = myfunc(3)
    
    print(mydoubler(11))
    print(mytripler(11))
    
    #######
        
    def mydoubler(n):
        return n * 2
    
    def mytripler(n):
        return n * 3
    
    print(mydoubler(11))
    print(mytripler(11))

def lambda4():
    
    list1 = [1,2,3,4,5]
    
    x = lambda a: True if a % 2 == 0 else False
    
    print(x(5))
    print(list(map(lambda a: True if a % 2 == 0 else False, list1)))
    
    #######
    
    def x(a):
        if a % 2 == 0:
            return True
        else:
            return False
    
    print(x(5))
    print(list(map(x, list1)))
    
def lambda5():
    
    list1 = ["Apple", "Orange", "Banana"]
    
    x = lambda n: [print(i) for i in n]
    
    x(list1)
    
    #######
    
    def x(n):
        for i in n:
            print(i)
    
    x(list1)
    
    #######
    
    [print(i) for i in list1]      # not lambda but another way of anonymous function
    
lambda1()
lambda2()
lambda3()
lambda4()
lambda5()
