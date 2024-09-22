# -*- coding: utf-8 -*-
import os
import glob
import shutil

glob_path = "C:\\ProgramData\\Anaconda3\\Practice\\testdir\\"
to_dir = "C:\\ProgramData\\Anaconda3\\Practice"

#glob to search all files under one directory given criteria
files = glob.glob(glob_path + "*.txt")+glob.glob(glob_path+ "*\\*.txt") +glob.glob(glob_path+ "*\\*\\*.txt") 
i = 0

pre_file_dir = ""
for file in files:
    i = i + 1
    file_dir, file_name = os.path.split(file)
    print(file_name)
    if file_dir == pre_file_dir:                        # diff way to separate folder
        i = i -1                                        
    file_rename = str(i).rjust(2,"0") + "_" + file_name # rjust to add 0 in front of single number
    to_path = to_dir + "\\" + file_rename
    shutil.copy(file, to_path)                # copy and rename file
    pre_file_dir = file_dir

