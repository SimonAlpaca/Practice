# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 18:55:14 2023

@author: simon
"""

import moviepy.editor as mp
import os

input_folder = r"C:\Users\simon\Practice\GIF_to_Video\input"

output_folder = r"C:\Users\simon\Practice\GIF_to_Video\output"

for file in os.listdir(input_folder):
    
    file_path = os.path.join(input_folder, file)
    
    new_name = file[:-4] + ".mp4"
    
    print(new_name)
    
    output_path = os.path.join(output_folder, new_name)
    
    clip = mp.VideoFileClip(file_path)
    clip.write_videofile(output_path)