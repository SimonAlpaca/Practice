# -*- coding: utf-8 -*-

import os
def nat_sort(file):
    file_name = os.path.splitext(file)[0]             # ignore file ext
    file_name = file_name.lower()                     # ignore upper character
    print(file_name)
    file_name_list = list(file_name)
    file_name_list.insert(0, "A")
    print(file_name_list)

    i = 0
    while True:
        if i == len(file_name_list) - 1:
            break
        
        if file_name_list[i].isnumeric() and file_name_list[i+1].isnumeric():
            file_name_list[i] = file_name_list[i] + file_name_list[i+1]     # merge numbers
            del file_name_list[i+1]

        elif not file_name_list[i].isnumeric() and not file_name_list[i+1].isnumeric():
            file_name_list[i] = file_name_list[i] + file_name_list[i+1]     # merge string
            del file_name_list[i+1]
        
        else:
            i = i + 1
    
    for j in range(len(file_name_list)):
        try:
            file_name_list[j] = int(file_name_list[j])        # change numbers in string to integer
        
        except ValueError:
            pass
    
    print(file_name_list)
    
    return file_name_list[:]                                  # return whole list. it can sort one by one
    
file = ["abc3124.jpg", "2123Abc3353c11.jpg", "abc10.jpg", "ABC2.jpg"]

print(sorted(file,key = nat_sort))