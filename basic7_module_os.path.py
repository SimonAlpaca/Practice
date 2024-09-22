# -*- coding: utf-8 -*-

import os                                                    # os.path module

thisdir = os.path.dirname(__file__)                          # get the directory
                                                             # __file__ means this file
filename = "basic1.py"

fullfilepath = os.path.join(thisdir,filename)                 # use join to create full path

print(fullfilepath)

print(os.path.abspath(__file__))                             # get the path of this file

if os.path.exists(filename):                             # check whether the file exists
    print("The file exists")
    
if os.path.isdir(thisdir):                                   # check whether it is a directory
    print("It is a directory")

if os.path.isfile(filename):                                 # check whether it is a file
    print("It is a file")    

dir = "testdir"
if not os.path.exists(dir):
    os.mkdir(dir)                                            # check whether there is a directory, create if not
else:
    print("The directory has already been created")
