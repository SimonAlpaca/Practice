# -*- coding: utf-8 -*-


import cv2
import sys
from PIL import Image, ImageTk, ImageSequence, ImageFile

path = r"C:\Downloads\[Soft Circle Courreges] Natsuiro Shimai\mpg\01_01.mpg"
output_path = r"C:\Downloads\[Soft Circle Courreges] Natsuiro Shimai\mpg\output.avi"

vidcap = cv2.VideoCapture(path)
success,image = vidcap.read()
count = 0

while success:
    cv2.imwrite(r"C:\Downloads\[Soft Circle Courreges] Natsuiro Shimai\mpg\frame%d.jpg" % count, image)     # save frame as JPEG file      
    success,image = vidcap.read()
    print('Read a new frame: ', success)
    #cv2.imshow('frame', image)
    count += 1