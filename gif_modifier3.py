# -*- coding: utf-8 -*-
# remove some frames from gif

from PIL import Image, ImageSequence
import imageio

def remove_frame(gif, save_path):
    new_frames = []
    img = Image.open(gif)
    i = 0
    for frame in ImageSequence.Iterator(img):
        
        #f = frame.copy().convert("RGBA")
        #frames.append(Image.alpha_composite(mask, f))
        #new_frames.append(frame.convert("P",palette=Image.ADAPTIVE))
        #if i % 2 == 0:
        new_frames.append(frame.convert("P",palette=Image.ADAPTIVE))


        #i = i + 1
    imageio.mimsave(save_path, new_frames[::2])
    #img.save(save_path, save_all=True, format="gif", append_images=new_frames, loop=0, transparency=255, disposal=0, duration = 50)

gif = r"C:\Downloads\HCG_Animated\AXSS\002_1_3.gif"
save_path = r"C:\Downloads\HCG_Animated\AXSS\trial.gif"

remove_frame(gif, save_path)

print("Done")