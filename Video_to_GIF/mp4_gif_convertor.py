# -*- coding: utf-8 -*-

# Import Required Module
import cv2 
import os 
from PIL import Image
import glob
import imageio

def convert_video_into_images(video_path):
    global duration
    
    # Read the video from specified path 
    camera = cv2.VideoCapture(video_path) 
    
    fps = camera.get(cv2.CAP_PROP_FPS) # get frames per second
    duration = 1/fps
    start_frame = int(start_time*fps)
    end_frame = int(end_time*fps)
    
    # set current frame to zero 
    current_frame = 0

    # Infinite loop
    while(True): 
        # reading each frame 
        ret,frame = camera.read() 
        
        # stop at end time
        if current_frame >= end_frame:
            break
        
        if ret: 
            if current_frame >= start_frame:    # start at start time
    
                file_name = 'frame' + str('{0:03}'.format(current_frame)) + '.png'
               
                # contrast and brightness modification
                # alpha = 1.15 # Contrast control (1.0-3.0)
                # beta = -15 # Brightness control (0-100)
                # frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
                
                # writing the extracted images 
                cv2.imwrite(file_name, frame) 
    
            # Increase the current frame value 
            current_frame += 1
        else: 
            break

    camera.release() 
    cv2.destroyAllWindows() 

 
def images_to_gif():
    # Frame List
    kwargs_write = {'fps':5.0, 'quantizer':'nq'}  # to improve image quality
    frames = []

    images = glob.glob("*.png")

    for image in images:
        new_frame = Image.open(image)
        
        # crop image
        left = 0
        top = 0
        right = 800
        bottom = 600
        crop_frame = new_frame.crop((left, top, right, bottom))
        
        frames.append(crop_frame)
        
    # Save into a GIF file that loops forever
    to_file = str('{0:03}'.format(j)) + ".gif"
    to_path = os.path.join(todir, to_file)
    
    #frames[0].save(to_path, format='GIF', append_images=frames[1:], save_all=True, duration = 40, loop=0)
    imageio.mimsave(to_path, frames, 'GIF-FI', **kwargs_write, duration=duration) # better image
    
def delete_all_images():
    # Iterate through all images
    for i in os.listdir():
        if ".png" in i:
            # remove file
            os.remove(i)

j = 0

# modify single file
todir = r"C:\Users\simon\Practice\Video_to_GIF\gif_output"
fullpathname = r"D:\Downloads\Anime_Comic\Anime\mami1.wmv"
start_time = 396.8
end_time = 404

convert_video_into_images(fullpathname)
images_to_gif()
delete_all_images()

print("Done")

'''
# modify all files in the folder
global j

filedir = r"D:\Downloads\Games\(同人アニメ) [140206][RJ126529][家庭菜園] 白黒つけ魔性 -桃色動画館-\bw4\omake\mpeg4_movie\000_joint.mp4"
file_walk = os.walk(filedir)

todir = r"C:\Downloads"
j = 0
for root,dir,files in file_walk:
    dir.sort()
            
    for file in files:
        j = j + 1
        fullpathname = os.path.join(root,file)
        convert_video_into_images(fullpathname)
        images_to_gif()
        delete_all_images()
        '''