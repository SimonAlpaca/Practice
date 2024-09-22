#list
#dictionary
#turple
#set
#array

# In[list]
def list_():
    list_test = [1,2,3,4,"Total"]   #list allows value with different type
    print("List : ")
    print(list_test)
    list_test.insert(2,2.5)   #insert value into list
    print(list_test)
    print()
    
    list_test_None = [None] * 10     # create a list with 10 None value
    print(list_test_None)
    print()
    
    list_test100 = list(range(100))  # create a list with 0 - 99
    print(list_test100[10:20])       # get the list from 11th to 20th
    print(list_test100[10:20:2])     # get the list from 11th to 20th step 2
    print(list_test100[::10])        # get all items step 10

# In[dictionary]
def dict_():
    dict_test = {"Apple":10, "Orange":15, "Banana":8}  #dict allows inputing keys with each value. list is a dict without keys and replaced by index number
    print("Dictionary : ")
    print(dict_test)
    print(dict_test["Orange"])   
         
    print(dict_test.get("Mango",20)) #.get to get mango's value. if no mango, return 20   
    dict_test["Strawberry"] = 20   #add new key with value
    dict_test["Apple"] = 25       #the key is unique and will replace the old one
    print(dict_test)
    
    list_keys = list(dict_test.keys())      #convert the keys into new list
    list_values = list(dict_test.values())  #convert the values into new list
    
    for i in range(len(list_keys)):         #for all values in list
        print("The price of %s is %d" %(list_keys[i],list_values[i])) #must declare variables after %
    print(sum(list_values))
    print()
    
    new_dict = {}                    # create dictionary from lists
    for i in range(len(list_keys)):
        new_dict[list_keys[i]] = list_values[i]
    
    print(new_dict)
    print()

# In[tuple]
def tuple_():
    tuple_test = (1,2,3,4)      #turple doesn't allow modification of data. and it runs faster
    print("Tuple : ")
    print(tuple_test)
    print(tuple_test[2])
    print()

# In[set]
def set_():
    set_test = set("Apple")    #set only allows unique value
    print("Set : ")
    print(set_test)
    list_test2 = ["Apple", "Orange", "Banana"]
    list_test3 = ["Apple", "Pineapple"]
    set_test2 = set(list_test2)
    set_test3 = set(list_test3)
    
    print(set_test2|set_test3)    #union of the 2 sets
    print(set_test2 & set_test3)  #intersection of the 2 sets
    print(set_test2-set_test3)    #difference of the 2 sets
    print()

# In[array]
def array_():
    import numpy as np               # import numpy
    list_test4 = [1,2,3,4,5]         # create a list
    array_test = np.array(list_test4) # convert to array
    print("Array : ")
    print(list_test4)
    print(array_test+1)              # array allows direct calculation
    
    array_test2 = np.array([6,7,8,9,10])
    print((array_test+1)*array_test2)   #multiply two arrays directly
    
    array_test3 = np.array([[1, 2, 3],[5,10,15]]) #array allows rows and columns
    print(array_test3)
    print(array_test3[1,2])      #rows first and columns
    
    array_test4 = np.array([1,2,3,4,5,6,7,8,9,10,11,12])     # create array with 1 row
    array_test5 = np.reshape(array_test4,(-1,3))    # reshape array with 3 columns; -1 means automatically assigned
    print(array_test5)

# In[]
list_()
dict_()
tuple_()
set_()
array_()