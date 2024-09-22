# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 10:09:31 2022

@author: simon
"""

import numpy as np
import sys

import psutil

ob = np.ones((1024, 1024, 1024, 3), dtype=np.uint8) # create a 1024*1024*1024*3 array, which uses 3GB of memory

print(sys.getsizeof(ob) / (1024))   # get the size of the array, which is 3GB

print(psutil.Process().memory_info().rss / (1024))   # get the allocated memory used of this program


del ob      # delete object to release memory