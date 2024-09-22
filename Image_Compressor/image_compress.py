# -*- coding: utf-8 -*-

from PIL import Image
import os 

dir = r"C:\Users\simon\Practice\Image_Compressor\input"

output_dir = r"C:\Users\simon\Practice\Image_Compressor\output"
list_dir = os.listdir(dir)

for file in list_dir:
    
    file_path = os.path.join(dir, file)
    print(file_path)
    
    new_file = os.path.splitext(file)[0] + ".jpg"
    output_path = os.path.join(output_dir, new_file)
    
    image = Image.open(file_path)
    rgb_im = image.convert('RGB')

    rgb_im.save(output_path)
