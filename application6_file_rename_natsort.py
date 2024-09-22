# -*- coding: utf-8 -*-
'''
rename files by natural sorting of files like what windows do
Intger:
[1,10,100,2,...] -> [1,2,...,10,...,100]

Lower:
[A,B,C,a] -> [A,a,B,C]
    
'''
import os

# In[Modification]
def modify_name(path):
    
    list_dir = os.listdir(path)                   # list of files in the folder
    
    #list_dir = sorted(list_dir, key = sort_path_integer)  # sort by integer
    list_dir = sorted(list_dir, key = sort_path_lower)  # sort by lower
    
    list_length_digit = len(str(len(list_dir)))
    
    i = 0
    for file in list_dir:
        i = i + 1
        file_rename = str(i).rjust(list_length_digit,"0") + "_" + file 
        
        old_path = os.path.join(path, file)
        new_path = os.path.join(path, file_rename)

        os.rename(old_path, new_path)


def sort_path_integer(file):
    return int(os.path.splitext(file)[0])         # sort files with sorted by interger

def sort_path_lower(file):                        # sort files with sorted by ignoring capital letter
    return file.lower()

# In[Reverse the modification]
def reverse_modify_name(path):
    list_dir = os.listdir(path)
    
    list_length_digit = len(str(len(list_dir)))
    
    for file in list_dir:
        file_rename = file[list_length_digit + 1 :]
        
        old_path = os.path.join(path, file)
        new_path = os.path.join(path, file_rename)

        os.rename(old_path, new_path)

# In[Main]
path = r'C:\Downloads\[2022-9-30] 爆机少女喵小吉 - 天道'
modify_name(path)
#reverse_modify_name(path)