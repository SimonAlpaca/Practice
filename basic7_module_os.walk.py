# -*- coding: utf-8 -*-

import os
import codecs

file_path = r"C:\Downloads" # add r in front of file path, otherwise use "\\"

file_tree = os.walk(file_path)

def remove_empty_folder():
    for path,_,_ in file_tree:
        print(path)
        print(len(os.listdir(path)))
        if len(os.listdir(path)) == 0:
            os.rmdir(path)       # remove empty folder

def print_all_dirname():
    for root, dir, files in file_tree:
        dir.sort()
        for dirname in dir:
            print(os.path.join(root,dirname))
   
def print_all_filename():
    for root, dir, files in file_tree:
        dir.sort()
        for file in files:
            print(os.path.join(root,file))

def rename_file():
    os.rename("C:\\ProgramData\\Anaconda3\\Practice\\test66.txt", "C:\\ProgramData\\Anaconda3\\Practice\\test6.txt")

def create_txt():
    file_name = "readme.txt"
    create_file = open(os.path.join(file_path, file_name), "a+",  encoding = "utf-8")  #add encoding to avoid unicode error
    
    dir_list = os.listdir(file_path)
    for r in dir_list:
        full_path = os.path.join(file_path,r)
        if os.path.isdir(full_path):
            print(r)
            create_file.write(r + "\n")
    create_file.close

def create_txt_codec():
    dir_list = os.listdir(file_path)
    print(len(dir_list))
    create_file = codecs.open("readme.txt", "a+", encoding = "utf-8")    #codecs for creating utf-8 txt

    for r in dir_list:
        full_path = os.path.join(file_path,r)
        if os.path.isdir(full_path):
            print(len(r), r)
            create_file.write(r + "\n")
            create_file.close

#create_txt_codec()
#create_txt()
remove_empty_folder()

"""
open reference
"r" - read (default)
"w" - write (overwrite)
"a" - write (append)
"x" - create (error if already exist)
"b" - binary mode
"t" - text mode (default)
"+" - read and write (append)    
"""