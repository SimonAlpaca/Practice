# -*- coding: utf-8 -*-

from pygifsicle import gifsicle
import os

def optimizer(input_path, output_path):

    gifsicle(
        sources=input_path,
        destination=output_path,
        optimize=False,
        colors=256,
        options=["--optimize=3", "--lossy=0"]
    )
    
    
dir_input = r"C:\Users\simon\Practice\Gif_Optimizer\original"
dir_output = r"C:\Users\simon\Practice\Gif_Optimizer\optimized"

list_input = os.listdir(dir_input)

for i in range(len(list_input)):
    
    file_name = list_input[i]
    file_ext = os.path.splitext(file_name)[1]
    if file_ext.lower() == ".gif":
        
        input_path = os.path.join(dir_input, file_name)
        output_path = os.path.join(dir_output, file_name)
        
        
        optimizer(input_path, output_path)
        print(input_path)
        print(output_path)
        
        print("Done: %d" % i)