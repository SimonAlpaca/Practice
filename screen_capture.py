# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
from PIL import Image
import mss
import os
import threading


def write_png(screenshot, number):
    file_name = r"C:\Users\simon\Practice\SimonAlpaca Snipping Tool\temp\temp_%s.png"
    mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_name %str(number).rjust(7, "0"))


top = 200
left = 500
width = 800
height = 600
fps = 30

output = "video.avi"
monitor_1 = {"top": top, "left": left, "width": width, "height": height}

# Define the codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output, fourcc, fps, (width, height))
pic_frame = []
number = 0

# temp file
# fp = tempfile.TemporaryFile()
# while True:
#     try:
#         time_start = time.perf_counter()
        
#         with mss.mss() as mss_instance:
#             screenshot = mss_instance.grab(monitor_1)
        
#         # pic_frame.append(screenshot)
#         img_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_name %number)
#         # img_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
        
#         # write temp file
#         # fp.write(img_bytes)
#         # fp.write(b"^o^")            # separator
        
#         time_spent = time.perf_counter() - time_start
#         print(time_spent)
#         time.sleep(max(1/fps - time_spent, 0))
        
#         number = number + 1
        
#     except KeyboardInterrupt:
#         print("break")
#         break

# # fp.seek(0)
# # pic_frame = fp.read().split(b"^o^")
# # print(len(pic_frame))

# dir = r"C:\Users\simon\Practice\SimonAlpaca Snipping Tool\temp"
# pic_frame = os.listdir(dir)

# # try:
# for frame in pic_frame:
#     png_path = os.path.join(dir, frame)
#     frame = Image.open(png_path)
#     # frame = Image.open(io.BytesIO(frame))
#     # frame = PIL.Image.frombytes("RGB", screenshot.size, frame, "raw", "BGRX")  # Convert to PIL.Image
#     # img_np = np.array(frame)
#     # image = cv2.cvtColor(np.array(img_np), cv2.COLOR_RGB2BGR)
#     # image = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#     # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
#     # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
#     img_np = np.array(frame)
#     out.write(img_np)
        
# except Exception as e:
#     print(e)
#     # print(pic_frame)

# finally:
# fp.close()   # delete temp file


while True:
    try:
        time_start = time.perf_counter()
        
        with mss.mss() as mss_instance:
            screenshot = mss_instance.grab(monitor_1)
        # time_start2 = time.perf_counter()
        
        globals()["process_%s" %number] = threading.Thread(target = write_png, args=(screenshot, number))
        globals()["process_%s" %number].start()
        
        # time_spent2 = time.perf_counter() - time_start2
        time_spent = time.perf_counter() - time_start
        print(time_spent)
        time.sleep(max(1/fps - time_spent, 0))
        
        number = number + 1
        
    except KeyboardInterrupt:
        print("break")
        print("total frame: ", number)
        break

for i in range(number):
     globals()["process_%s" %number].join(0.5)

dir = r"C:\Users\simon\Practice\SimonAlpaca Snipping Tool\temp"
pic_frame = os.listdir(dir)

for frame in pic_frame:
    print(frame)
    png_path = os.path.join(dir, frame)
    frame = Image.open(png_path)

    frame = np.array(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    out.write(frame)
    os.remove(png_path)
    
out.release()
cv2.destroyAllWindows()
    