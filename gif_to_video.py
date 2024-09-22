# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 20:57:41 2022

@author: simon
"""
import os
import moviepy.editor as mp

path = r"C:\Downloads\[seismic] Kuma Magi [Puella Magi Madoka Magica][animated]"

list_dir = os.listdir(path)

for file in list_dir:
    file_ext = os.path.splitext(file)[1]
    if file_ext == ".gif":
        old_path = os.path.join(path, file)
        new_name = os.path.splitext(file)[0] + ".mp4"
        new_path = os.path.join(path, new_name)
        print(new_name)
        clip = mp.VideoFileClip(old_path)
        clip.write_videofile(new_path, codec='libx264')