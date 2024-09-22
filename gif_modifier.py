# -*- coding: utf-8 -*-

from PIL import Image, ImageTk, ImageSequence
def write_gif3():
    frames = []
    img = Image.open(gif)
    #mask = Image.new("RGBA", img.size, (255, 255, 255, 0))
    
    for frame in ImageSequence.Iterator(img):
        
        #f = frame.copy().convert("RGBA")
        #frames.append(Image.alpha_composite(mask, f))
        frames.append(frame.convert("P",palette=Image.ADAPTIVE))

    #img = Image.new("RGBA", frame.size, (255, 255, 255, 0))
    img = Image.new("P", img.size)
    img.save(save_path, save_all=True, append_images=frames, loop=0, transparency=255, disposal=0)

gif = r"C:\Downloads\[NEKO WORKs] Neko Para Vol. 4 Neko to Patissier no Noel [GIF + MP4 + WebM]\GIF\neko4_h02c1a.gif"
save_path = r"C:\Downloads\[NEKO WORKs] Neko Para Vol. 4 Neko to Patissier no Noel [GIF + MP4 + WebM]\001.gif"

write_gif3()