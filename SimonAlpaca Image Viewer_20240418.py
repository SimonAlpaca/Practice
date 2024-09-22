# -*- coding: utf-8 -*-
# author: SimonAlpaca
# project v1.0 started on 25/8/2021, finished on 3/10/2021

import os
import sys
import traceback
from PIL import Image, ImageTk, ImageSequence, ImageFile, ImageEnhance
import imageio
import cv2
import imagesize
import pandas as pd
import numpy as np
import time
import requests
from bs4 import BeautifulSoup
import configparser
import logging
import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk, filedialog
from ctypes import windll
from win32api import GetMonitorInfo, MonitorFromPoint
import threading
import gc
import random
#import psutil
import io

# In[Logging]

def logging_create():

    exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
    logging_path = os.path.join(exe_dir, "err_handling.log")
    logging.basicConfig(level = logging.DEBUG, handlers=[logging.FileHandler(logging_path, 'w', 'utf-8')])
    
def exception_override(self, *args):
    
    err = traceback.format_exception(*args)
    
    ignore_err = False
    
    for err_line in err:
        if "Exception: IGNORE" in err_line:        # to ignore bug (no use for now)
            ignore_err = True

    if not ignore_err:
        for err_line in err:
            print(err_line)
            logging.info(err_line)
            
def logging_shutdown():
    
    logging.shutdown()

# In[Storage]

class Storage:
    
    '''
    Lists:
    window.stor.ListStor 
    fulllevel.stor.ListStor
    fulllevel.manga.ListStor
    
        File:
        .ListStor[window.fileindex] #Img or Ani 
            
            Img:
            .ListStor[window.fileindex][Image]
            
            Ani:
            .ListStor[window.fileindex]{"gif_duration" : [gif_duration of each frame], "is_cached" : True / False, "img" : [Image of each gif frame]}
    
    window.stor.ListPhotoStor
    fulllevel.stor.ListPhotoStor
    
        File:
        Ani:
        .ListPhotoStor[window.fileindex][PhotoImage]
    
    Lists:
    window.storage_size
    # 1 storage_size = 1 image with size of full screen
        
        window.storage_size{"window" : [size of each file], "fulllevel": [size of each file], "manga": [size of each file], "window.PhotoStor": 2x[size of each file], "fulllevel.PhotoStor": 2x[size of each file]}
        
    
    '''
    def __init__(self, name):
        print("class Storage _init_: %s " %name)
        logging.info("class Storage _init_: %s " %name)
        
        self.ListStor = []       # window.stor.ListStor or fulllevel.stor.ListStor or fulllevel.manga.ListStor
        self.ListPhotoStor = []   # window.stor.ListPhotoStor or fulllevel.stor.ListPhotoStor
        self.backend_run = False
        self.backend_run_photoimage = False
        self.pause_backend = False
        self.stop_backend = False
        self.last_index = None
        self.name = name
        
        self.FORWARD_STORAGE = 40
        self.BACKWARD_STORAGE = 5
        self.FORWARD_PHOTOIMAGE_STORAGE = 3
        self.BACKWARD_PHOTOIMAGE_STORAGE = 0
        self.MAX_STORAGE_SIZE = 1200
        
    def write_storage(self, fileindex, resize_img):
        
        total_storage_size = window.cal_storage_size()
        if total_storage_size > self.MAX_STORAGE_SIZE:     # stop adding storage if exceeding storage cap
            return None
        
        if not settinglevel.is_storage:                                 # stop storage if setting false
            return None
        
        self.ListStor[fileindex] = resize_img         # write one file when open
        
        self.last_index = fileindex        # get last file index
        
        total_storage_size = window.cal_storage_size()
        print("storage size : ", total_storage_size)
        logging.info("storage size : %s", total_storage_size)
        
        if total_storage_size > 500:
            self.clear_cache()
        
        # update listbox
        listlevel.cached_listbox(self.name, fileindex, True)
        
        print("Cached: ", self.name, " - ", fileindex)
        logging.info("Cached: %s - %s", self.name, fileindex)
        
    def write_ani_storage(self, fileindex, **kwargs):
        
        total_storage_size = window.cal_storage_size()
        if total_storage_size > self.MAX_STORAGE_SIZE:    # stop adding storage if exceeding storage cap
            return None
        
        if not settinglevel.is_storage:                                 # stop storage if setting false
            return None
        
        self.ListStor[fileindex] = {}
        self.ListStor[fileindex]["gif_duration"] = kwargs["gif_duration"]
        self.ListStor[fileindex]["img"] = kwargs["img"]
        self.ListStor[fileindex]["is_cached"] = kwargs["is_cached"]
            
        # update listbox
        listlevel.cached_listbox(self.name, fileindex, True)
        
        # check storage only in last step
        self.last_index = fileindex        # get last file index
        
        total_storage_size = window.cal_storage_size()
        print("storage size : ", total_storage_size)
        logging.info("storage size : %s", total_storage_size)
        
        if total_storage_size > 500:
            self.clear_cache()

    def backend_storage(self, fileindex):
        
        if not settinglevel.is_storage:        # stop storage if setting false
            return None
        
        if window.is_web_mode:                # stop storage if web mode
            return None
        
        # timer_start = time.perf_counter()
        
        try:
            gc.disable()                                   # garbage collection in thread may cause instability
            self.backend_run = True                        # running thread
            storage_range = min(self.FORWARD_STORAGE + 1, len(window.fullfilelist))
            print("start backend_storage:", self.name)
            logging.info("start backend_storage: %s", self.name)

            total_storage_size = window.cal_storage_size()
            #print("storage size : ", total_storage_size)
            # logging.info("storage size : %s", total_storage_size)
            
            if total_storage_size > 500:
                self.clear_cache()
            
            #print(psutil.Process().memory_info().rss / (1024*1024))
            
            for i in range(storage_range):
                
                while self.pause_backend:
                    time.sleep(0.05)
                
                if self.stop_backend:
                     raise StopIteration
                
                total_storage_size = window.cal_storage_size()
                # print("storage size : ", total_storage_size)
                # logging.info("storage size : %s", total_storage_size)
                
                if total_storage_size > self.MAX_STORAGE_SIZE:    # stop adding storage if exceeding storage cap
                    break
       
                if not settinglevel.is_storage:                         # stop storage if setting false
                    break
                
                if fileindex + i >= len(window.fullfilelist):
                    listindex = fileindex + i - len(window.fullfilelist)
                
                else:
                    listindex = fileindex + i
                
                if self.ListStor[listindex] is None:      # if not yet cached
                    
                    filepath = window.fullfilelist[listindex]
                    file_ext = os.path.splitext(filepath)[1].lower()
                    
                    if file_ext in window.supported_ani:
                        if not window.is_manga_mode:     # skip ani in manga mode
                            self.ani_storage(listindex)
                    
                    elif file_ext in window.supported_img:
                        self.img_storage(listindex)
                    
                    elif file_ext in window.supported_vid:
                        if not window.is_manga_mode:
                            self.vid_storage(listindex)
                        
                    else:
                        pass
                        
                    self.last_index = listindex        # get last file index
                    
                    # to check size of storage
                    # self.storage_size = self.storage_size + self.getSizeOfNestedList(self.ListStor[listindex])
                    # print(round(self.storage_size / (1024*1024),2))
                    
                    #print(window.storage_size)
                    total_storage_size = window.cal_storage_size()
                    print("storage size : ", total_storage_size)
                    logging.info("storage size : %s", total_storage_size)
                    
                    if total_storage_size > 500:
                        self.clear_cache()
                    
                    #print(psutil.Process().memory_info().rss / (1024*1024))

            print("Auto storage done: ", self.name)         # finish running loop
            logging.info("Auto storage done: %s", self.name)

            self.backend_run = False
            
        except StopIteration:                  # kill thread
            print("Auto storage stopped: ", self.name)
            logging.info("Auto storage stopped: %s", self.name)
            self.backend_run = False 
        
        # timer_end = time.perf_counter()
        # print(round(timer_end - timer_start,2))
        
        gc.enable()
        
    # def getSizeOfNestedList(self, listOfElem):
    #     ''' Get number of elements in a nested list'''
    #     count = 0
    #     # Iterate over the list
    #     for elem in listOfElem:
    #         # Check if type of element is list
    #         if isinstance(elem, (list, tuple, np.ndarray)):  
    #             #print("list")
    #             # Again call this function to get the size of this element
    #             count = count + self.getSizeOfNestedList(elem)
    #         else:
    #             count = count + sys.getsizeof(elem)
                
    #     return count
    
    def img_storage(self, listindex):
        
        try:
            while self.pause_backend:
                time.sleep(0.05)
            
            if self.stop_backend:
                 raise StopIteration
            
            pic_path = window.fullfilelist[listindex]
            
            img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            
            while self.pause_backend:
                time.sleep(0.05)
            
            if self.stop_backend:
                raise StopIteration
            
            try:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            except:                              # fail for .ico files
                print("Cache Failed: ", self.name , " - ", listindex)    
                return None                      # exit function
    
            if img is not None:
    
                img_h, img_w = img.shape[:2]
                
                if window.is_full_mode:
                    if not window.is_manga_mode:
                        if window.full_w > 1 and window.full_h  > 1:  
                            if not window.is_photoalbum_mode:
                                # simple full mode and slide mode
                                if settinglevel.is_original:
                                    resize_scale = 1
                                    
                                else:
                                    resize_scale = min(window.full_w / img_w, window.full_h  / img_h)   # calculate the resize ratio, maintaining height-width scale

                            else:
                                # photoalbum mode
                                photoalbum_zoom_factor = window.photoalbum_zoom_factor

                                if window.full_w / img_w >= window.full_h / img_h:                    # if the image is narrower than screen
                                    resize_scale = window.full_w / img_w * photoalbum_zoom_factor               # calculate the resize ratio, maintaining height-width scale

                                    w, h = int(img_w * resize_scale), int(img_h * resize_scale)
                                    
                                    if w < window.full_w and h < window.full_h:        # fit fullscreen size if the image is smaller than full screen
                                        resize_scale = min(window.full_w / img_w, window.full_h / img_h)
                                
                                else:  # if the image wider than screen
                                    resize_scale = window.full_h / img_h                    # calculate the resize ratio, maintaining height-width scale, zoom factor does not apply for this kind of pic
                    
                    else:  
                        # manga mode
                        resize_scale = window.full_w / img_w * settinglevel.manga_resize               # calculate the resize ratio, maintaining height-width scale  
                        
                else:  
                    # window mode
                    try:
                        pic_w, pic_h = window.pic_canvas.winfo_width(), window.pic_canvas.winfo_height()  # get canvas width and height
            
                    except:
                        pass 
                    
                    if pic_w > 1 and pic_h > 1:
                
                        if settinglevel.is_original:
                            resize_scale = 1
                
                        else:
                            resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
                            #resize_scale = min(resize_scale, 1)            # avoid bigger than original

                pics_screen_ratio = (img_w / window.full_w) * (img_h / window.full_h) * (resize_scale**2)  # the ratio of image size after resize to the fullscreen size
                total_screen = pics_screen_ratio                                      # pic_ratio muliplies the number of frame
                
                window.storage_size[self.name][listindex] = total_screen
            
                w, h = int(img_w * resize_scale), int(img_h * resize_scale)
                w_h = (w, h)
                
                while self.pause_backend:
                    time.sleep(0.05)
                
                if self.stop_backend:
                     raise StopIteration
                
                try:
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                
                except OSError:                              # fix OSError: image file is truncated
                    print("OSError: image file is truncated")
                    logging.info("OSError: image file is truncated")               
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                
                if not window.is_manga_mode:
                    # not manga mode
                    self.ListStor[listindex] = resize_img    # cache
                    print("Cached: ", self.name , " - ", listindex)
                    logging.info("Cached: %s - %s", self.name, listindex)
                    
                else:
                    # manga mode
                    self.ListStor[listindex] = [resize_img]    # cache
                    print("Cached: ", self.name , " - ", listindex)
                    logging.info("Cached: %s - %s", self.name, listindex)                    
                    self.ListStor[listindex].append(h)         # store image height
                    
                # update listbox
                listlevel.cached_listbox(self.name, listindex, True)
                    
                del img
                del resize_img
                
        except StopIteration:                  # kill thread
            print("Auto storage stopped: ", self.name)
            logging.info("Auto storage stopped: %s", self.name)
            self.backend_run = False 
            
            try:
                del img
                del resize_img
            
            except:
                pass
            
    def ani_storage(self, listindex):
        
        try:
            cv_gif = []                             # create list to store frames of gif
            pic_path = window.fullfilelist[listindex]
            
            if len(pic_path) > 255:
                exception_pathtoolong()
            
            pil_gif = Image.open(pic_path)
    
            img_w, img_h = pil_gif.size
            
            gif_duration = []
            
            iter = ImageSequence.Iterator(pil_gif) 
            count_frame = 0
            for frame in iter:
                try:
                    frame_duration = frame.info['duration']
                    # if frame_duration == 0:     
                    #     frame_duration = 40
                    gif_duration.append(frame_duration / 1000)
                    count_frame = count_frame + 1
                    
                except:
                    gif_duration.append(40 / 1000)   # set to 40 if can't find duration

            # print("gif: ", gif_duration)
            #print(count_frame)
            
            # del pil_gif
            
            while self.pause_backend:
                time.sleep(0.05)
            
            if self.stop_backend:
                  raise StopIteration
                 
            if settinglevel.is_original:
                resize_scale = 1

            else:
                if window.is_full_mode:
                    if window.full_w > 1 and window.full_h  > 1:
                        resize_scale = min(window.full_w / img_w, window.full_h  / img_h)   # calculate the resize ratio, maintaining height-width scale
    
                else:
                    pic_w, pic_h = window.pic_canvas.winfo_width(), window.pic_canvas.winfo_height()
                    resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
            pics_screen_ratio = (img_w / window.full_w) * (img_h / window.full_h) * (resize_scale**2)  # the ratio of image size after resize to the fullscreen size
            total_screen = pics_screen_ratio * count_frame                # pic_ratio muliplies the number of frame
            
            window.storage_size[self.name][listindex] = total_screen
            
            w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            w_h = (w, h)
            
            try:
                cv_gif = imageio.mimread(pic_path, memtest=False)
            
                if self.stop_backend:
                    raise StopIteration
                
                resize_img = []
                for img in cv_gif:
                    img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                    resize_img.append(img)
                    
                    while self.pause_backend:
                        time.sleep(0.05)
                    
                    if self.stop_backend:
                          raise StopIteration
                          
            except ValueError:     # for opening .webp file
                resize_img = []
                i = 0
                try:
                    while True:
                        frame = pil_gif.copy()
                        
                        resize_frame = frame.resize((w,h))
                        
                        buf = io.BytesIO()
                        resize_frame.save(buf, format='PNG')
                        byte_im = buf.getvalue()
                        img = np.asarray(bytearray(byte_im), dtype="uint8")
                        
                        img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        
                        resize_img.append(img)
                        
                        pil_gif.seek(i)
                        i = i + 1
                        
                except EOFError:
                    del resize_img[-1]
                
                # gif_len = len(gif_frame) - 1
                
            del img
            del cv_gif
            
            self.ListStor[listindex] = {}
            self.ListStor[listindex]["gif_duration"] = gif_duration
            self.ListStor[listindex]["img"] = resize_img
            self.ListStor[listindex]["is_cached"] = True
            
            # update listbox
            listlevel.cached_listbox(self.name, listindex, True)
                
            print("Cached: ", self.name , " - ", listindex, " (Ani)")
            logging.info("Cached: %s - %s (Ani)", self.name , listindex)
            
        except StopIteration:                  # kill thread
            print("Auto storage stopped: ", self.name)
            logging.info("Auto storage stopped: %s ", self.name)
            self.backend_run = False 
            
            img = None
            cv_gif = None
            
            try:
                del img
                del cv_gif
            
            except:
                pass
    
    def vid_storage(self, listindex):
        
        try:
            pic_path = window.fullfilelist[listindex]
            
            if len(pic_path) > 255:
                exception_pathtoolong()
            
            vidcap = cv2.VideoCapture(pic_path)
            
            img_w = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
            img_h = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)

            MAX_FRAME = 500
            gif_len = min(MAX_FRAME, int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)))

            gif_duration = []

            fps = vidcap.get(cv2.CAP_PROP_FPS)    

            gif_duration = [round(1/fps, 6)] * (gif_len + 1) # convert frame per second to gif duration
            
            if self.stop_backend:
                raise StopIteration
        
            if settinglevel.is_original:
                    resize_scale = 1
            
            else:
                if window.is_full_mode:
                    if window.full_w > 1 and window.full_h  > 1:
                        resize_scale = min(window.full_w / img_w, window.full_h  / img_h)   # calculate the resize ratio, maintaining height-width scale
    
                else:
                    pic_w, pic_h = window.pic_canvas.winfo_width(), window.pic_canvas.winfo_height()
                    resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale

            w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            w_h = (w, h)
            
            i = 0   
            success = True
            resize_img = []
            while success:
                success,image = vidcap.read()
                #print('Read a new frame: ', success, i)
                
                if success:
                    image = cv2.resize(image, w_h, interpolation = cv2.INTER_AREA)
                    image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                    resize_img.append(image)
                    
                    i = i + 1
                    if i >= MAX_FRAME:
                        break                             # end loop if reaching max frame
                    
                    while self.pause_backend:
                        time.sleep(0.05)
                    
                    if self.stop_backend:
                         raise StopIteration
                             
            del image
            del vidcap

            self.ListStor[listindex] = {}
            self.ListStor[listindex]["gif_duration"] = gif_duration
            self.ListStor[listindex]["img"] = resize_img
            self.ListStor[listindex]["is_cached"] = True
            
            # update storage size
            pics_screen_ratio = (img_w / window.full_w) * (img_h / window.full_h) * (resize_scale**2)  # the ratio of image size after resize to the fullscreen size
            total_screen = pics_screen_ratio * gif_len                                        # pic_ratio muliplies the number of frame
            
            window.storage_size[self.name][listindex] = total_screen
            
            # update listbox
            listlevel.cached_listbox(self.name, listindex, True)
                
            print("Cached: ", self.name , " - ", listindex, " (Vid)")
            logging.info("Cached: %s - %s (Vid)", self.name , listindex)
            
        except StopIteration:                  # kill thread
            print("Auto storage stopped: ", self.name)
            logging.info("Auto storage stopped: %s ", self.name)
            self.backend_run = False 
            
            image = None
            vidcap = None
            
            try:
                del image
                del vidcap
            
            except:
                pass    

    def clear_cache(self):
        print("Clear Cache Process")
        logging.info("Clear Cache Process")
        
        current_fileindex = window.fileindex
                
        if not window.is_full_mode:             # window mode
            if sum(window.storage_size["fulllevel"]) > 0:
                    fulllevel.stor.stop_storage(True)

        else:
            if not window.is_manga_mode:        # full mode
                if sum(window.storage_size["window"]) > 0:
                        window.stor.stop_storage(True)
            
            else:                               # manga mode
                if sum(window.storage_size["window"]) > 0:
                        window.stor.stop_storage(True)
                       
                if sum(window.storage_size["fulllevel"]) > 0:
                        fulllevel.stor.stop_storage(True)
        
        total_storage_size = window.cal_storage_size()
        # print("storage size : ", total_storage_size)
        
        start_point = int(round(len(window.fullfilelist) / 2, 0) + window.fileindex)
        if start_point >= len(window.fullfilelist):
            start_point = start_point - len(window.fullfilelist)
        
        if len(window.fullfilelist) > self.BACKWARD_STORAGE * 2 + 1:    # can't support small list with big vid
            # print("back to front delete")
            i = 0
            if total_storage_size > 700:
                while True:
                    current_point = start_point + i
                    
                    if total_storage_size < 700:
                        break
                    
                    if current_fileindex != window.fileindex:      # break if forward / backward / select list
                        break
                    
                    if current_point == window.fileindex:
                        break
                    
                    if self.ListStor[current_point] is not None:
                        self.clear_one_storage(current_point)
                        total_storage_size = window.cal_storage_size()
                    
                    if window.fileindex >= self.BACKWARD_STORAGE:
                        if window.fileindex - current_point - 1 == self.BACKWARD_STORAGE:
                            break
                    
                    else:
                        if window.fileindex - (current_point) + len(window.fullfilelist) - 1 == self.BACKWARD_STORAGE:
                            break
                    
                    if current_point == len(window.fullfilelist) - 1:
                        i = i - len(window.fullfilelist) + 1     # back to zero
                        
                    else:
                        i = i + 1
            
        if len(window.fullfilelist) > self.FORWARD_STORAGE * 2 + 1:   # can't support small list with big vid
            # print("front to back delete")
            i = 0
            if total_storage_size >= self.MAX_STORAGE_SIZE:
                while True:
                    current_point = start_point + i
                    # print(current_point)
                    
                    if total_storage_size < self.MAX_STORAGE_SIZE:
                        break
                    
                    if current_fileindex != window.fileindex:      # break if forward / backward / select list
                        break
                    
                    if current_point == window.fileindex:
                        break
                    
                    if self.ListStor[current_point] is not None:
                        self.clear_one_storage(current_point)
                        total_storage_size = window.cal_storage_size()
                    
                    if window.fileindex <= len(window.fullfilelist) - self.FORWARD_STORAGE:
                        if current_point - window.fileindex == self.FORWARD_STORAGE:
                            break
                    
                    else:
                        if len(window.fullfilelist) - window.fileindex + current_point == self.FORWARD_STORAGE:
                            break
                     
                    if current_point == 0:
                        i = len(window.fullfilelist) - 1 - start_point     # back to last element
                    
                    else:
                        i = i - 1
                
        # print("garbage collected: ", gc.collect())     # garbage collection        
        # logging.info("garbage collected: %s", gc.collect())     # garbage collection  
            
        # print("Clear Cache Process Complete")
        # logging.info("Clear Cache Process Complete")
            
    def clear_one_storage(self, fileindex):
        
        self.ListStor[fileindex] = None
        self.ListPhotoStor[fileindex] = None
        
        # update listbox
        listlevel.cached_listbox(self.name, fileindex, False)
        
        print("Cache Cleared: %s - %s" %(self.name, fileindex))
        logging.info("Cache Cleared: %s - %s" %(self.name, fileindex))
        
        window.storage_size[self.name][fileindex] = 0
    
        total_storage_size = window.cal_storage_size()
        print("storage size : ", total_storage_size)
        logging.info("storage size : %s", total_storage_size)

    def stop_storage(self, is_delete):
        
        self.pause_backend = False
        self.stop_backend = True
        
        if self.backend_run:
            try:
                self.thread_storage.join(1)
                self.thread_storage_photoimage.join(1)
            
            except AttributeError:
                print("stop_storage after event resize")
                
            except RuntimeError:
                print("RuntimeError: cannot join current thread - ", self.name)
                
            print("thread stopped")
            logging.info("thread stopped")
            
        if is_delete:
            self.create_reset_storage()

            print("Cache Cleared All: ", self.name)
            logging.info("Cache Cleared All: %s", self.name)
            print("garbage collected: ", gc.collect())     # garbage collection        
            logging.info("garbage collected: %s", gc.collect())     # garbage collection  
            
        self.stop_backend = False

    def create_reset_storage(self):
        
        window.storage_size[self.name] = [0] * len(window.fullfilelist)
        
        # update listbox
        listlevel.reset_cached_listbox(self.name)
        
        self.ListStor = [None] * len(window.fullfilelist)
        self.ListPhotoStor = [None] * len(window.fullfilelist)
        self.last_index = None
    
    def clear_photoimage_storage(self, fileindex):
        
        self.ListPhotoStor[fileindex] = None
    
    def backend_photoimage_storage(self, fileindex):
        
        if not settinglevel.is_storage:                                 # stop storage if setting false
            return None
        
        # timer_start = time.perf_counter()
        
        try:
            gc.disable()                                   # garbage collection in thread may cause instability
            self.backend_run_photoimage = True                        # running thread
            storage_range = min(self.FORWARD_PHOTOIMAGE_STORAGE + 1, len(window.fullfilelist))
            print("start backend_photoimage_storage :", self.name)
            logging.info("start backend_photoimage_storage: %s", self.name)
            
            for i in range(storage_range):
                
                while self.pause_backend:
                    time.sleep(0.05)
                
                if self.stop_backend:
                     raise StopIteration
                
                # total_storage_size = window.cal_storage_size()
                # print("storage size : ", total_storage_size)
                # logging.info("storage size : %s", total_storage_size)
                
                # if total_storage_size > self.MAX_STORAGE_SIZE:    # stop adding storage if exceeding storage cap
                #     break
       
                if not settinglevel.is_storage:                         # stop storage if setting false
                    break
                
                if fileindex + i + 1>= len(window.fullfilelist):
                    listindex = fileindex + i + 1 - len(window.fullfilelist)
                
                else:
                    listindex = fileindex + i + 1                    # +1 to skip the current pic
                
                if self.ListPhotoStor[listindex] is None:      # if not yet cached
                    
                    filepath = window.fullfilelist[listindex]
                    file_ext = os.path.splitext(filepath)[1].lower()
                    
                    if file_ext in (window.supported_ani | window.supported_vid):
                        self.photoimage_storage(listindex)

            print("Auto Photoimage storage done: ", self.name)         # finish running loop
            logging.info("Auto Photoimage storage done: %s", self.name)

            self.backend_run_photoimage = False
            
        except StopIteration:                  # kill thread
            print("Auto Photoimage storage stopped: ", self.name)
            logging.info("Auto Photoimage storage stopped: %s", self.name)
            self.backend_run_photoimage = False 
        
        # timer_end = time.perf_counter()
        # print(round(timer_end - timer_start,2))
        
        gc.enable()
    
    def photoimage_storage(self, listindex):
        print("photoimage_storage")
        
        resize_img = []
        pic_frame = []
        wait_sec = 0
        
        while self.ListStor[listindex] is None and wait_sec < 5:   # wait 5 sec until ListStor has data
            time.sleep(0.1)
            wait_sec = wait_sec + 0.1
            
            if self.stop_backend:
                return None
            
            if window.fileindex >= listindex:             # skip storage if forwarded
                return None
            
        if self.ListStor[listindex] is not None and self.ListPhotoStor[listindex] is None:
            resize_img = self.ListStor[listindex]["img"]
            
            if len(resize_img) > 300:             # max 300 frame per file for photoimage storage
                return None
            
            for i in resize_img:
                pic = ImageTk.PhotoImage(image = Image.fromarray(i))
                pic_frame.append(pic)
                
                if self.stop_backend:
                     return None
                 
                if window.fileindex >= listindex:             # skip storage if forwarded
                     return None
            
            self.ListPhotoStor[listindex] = {}
            self.ListPhotoStor[listindex]["img"] = pic_frame
            self.ListPhotoStor[listindex]["is_cached"] = True
            
            print("Cached (PhotoImage): ", self.name , " - ", listindex, " (Vid)")
            logging.info("Cached (PhotoImage): %s - %s (Vid)", self.name , listindex)
            
        else:
            return None
    
# In[GUI]

class WindowGUI(tk.Frame):
    
    def __init__(self, parent, name):
        print("class WindowGUI _init_")
        logging.info("class WindowGUI _init_")
        
        super().__init__()
        
        self.name = name
        self.parent = parent
        self.stor = Storage("window")
        self.rotate_degree = 0
        self.full_w, self.full_h = self.winfo_screenwidth(), self.winfo_screenheight()  # get screen width and screen height
        self.offsetx = 0
        self.offsety = 0
        self.gif_speed2 = 1
        self.gif_speed3 = 1
        self.fullfilelist = []
        self.fileindex = 0
        self.window_focus = True
        self.event_resize_no = 0
        self.event_zoom_ongoing = False
        self.storage_size = {}
        self.event_resize_stopstorage = False

        self.is_full_mode = False
        self.is_stop_ani = True
        self.zoom_factor = 1
        self.photoalbum_zoom_factor = 1
        self.is_web_mode = False
        self.is_slide_check = False
        self.is_photoalbum_mode = False
        self.is_manga_mode = False
        self.is_auto_manga = False
        self.is_timer_pause = False
        self.hide = False
        self.hide_gif_con = False
        self.next_enhance = True
        self.brightness = 1
        self.contrast = 1
        self.sharpness = 1
        self.color = 1
        self.img_IE = None
        self.list_with_img = False
        self.dataframe_list = None
        self.dataframe_stop = False
        self.random_button_process = 0
        self.is_filter_con_created = False
        self.filter = False
        self.is_web_created = False
        self.apply_to_all = True
        
        # Supported format
        self.supported_img = [".jpg", ".jpeg", ".png", ".bmp", ".jfif", ".ico"]
        self.supported_ani = [".gif", ".webp"]
        self.supported_vid = [".mpg", ".wmv", ".mp4", ".avi", ".mkv", ".webm"]      # ogg can't open;
        self.supported_list = [".list", ".txt"]
    
        self.supported_img = set(self.supported_img)      # create set
        self.supported_ani = set(self.supported_ani)
        self.supported_vid = set(self.supported_vid)
        self.supported_list = set(self.supported_list)
        
        self.gif_con = tk.Toplevel(self.parent)
        
    def window_create(self):
        print("window_create")
        logging.info("window_create")
        
        # Window
        self.parent.overrideredirect(True)                                  
        self.parent.geometry('800x600+300+150')                                 # window size  
        self.parent.resizable(width=True,height=True)                   # disallow window resize
        self.parent.title("SimonAlpaca Picture Viewer")                  # title
        self.parent.withdraw()
 
        # Top Frame
        self.top_frame = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.top_frame.pack(pady=1, side = tk.TOP, fill = "both")
        self.quit_button = ttk.Button(self.top_frame, text= "\u03A7", width=2, style='primary.TButton', command = self.quit)
        self.quit_button.pack(side =tk.RIGHT, padx = 5)
        
        self.max_button = ttk.Button(self.top_frame, text= "\u2587", width=2, style='primary.TButton', command = self.window_zoomed)
        self.max_button.pack(side =tk.RIGHT, padx = 5)
        
        self.min_button = ttk.Button(self.top_frame, text= "\u2012", width=2, style='primary.TButton', command = self.window_hide)
        self.min_button.pack(side =tk.RIGHT, padx = 5)
        
        self.anticlock_button = ttk.Button(self.top_frame, text= "\u2937", width=1, style='primary.TButton', command = self.anticlockwise)
        self.anticlock_button.pack(side =tk.LEFT, padx = 10)
        
        self.clock_button = ttk.Button(self.top_frame, text= "\u2936", width=1, style='primary.TButton', command = self.clockwise)
        self.clock_button.pack(side =tk.LEFT, padx = 5)
        
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)               # when close in taskbar
        
        # Program icon
        try:                                                   
            exe_dir = os.path.split(sys.argv[0])[0]            # sys.argv[0] is the exe path
            self.ico_path = os.path.join(exe_dir, "Alpaca_ico.ico")
            self.parent.iconbitmap(self.ico_path)                   # must be parent otherwise can't show program in taskbar   
        
        except:
            print("failed to import ico")
            logging.info("failed to import ico")
        
        # Window Drag
        self.top_frame.bind('<Button-1>', self.window_predrag)
        self.top_frame.bind('<B1-Motion>', self.window_drag)
        self.top_frame.bind('<ButtonRelease-1>', self.drag_release)

        # Canvas
        self.pic_canvas = tk.Canvas()
        self.pic_canvas.configure(background='black')
        self.pic_canvas.pack(side=tk.TOP, fill="both", expand=True, pady = 0, padx =10)
        self.pic_canvas.configure(scrollregion = self.pic_canvas.bbox("all"))
     
        # Bottom Button
        self.buttondown_frame = ttk.Frame(self.parent, style='Warning.TFrame')             # add frame first
        self.buttondown_frame.pack(pady=5, side = tk.BOTTOM)
        
        self.check_button = ttk.Checkbutton(self.buttondown_frame, text="Include Subfolder                                   ", var=settinglevel.parent_check, style = "warning.Roundtoggle.Toolbutton")
        self.check_button.pack(padx = 5, side= tk.RIGHT) 
        
        self.go_button = ttk.Button(self.buttondown_frame, text= "GO", width=12, style='primary.TButton', command= self.go)
        self.go_button.pack(side=tk.RIGHT,padx=10)              # padx means gap of x-axis
        
        self.listbox_button = ttk.Button(self.buttondown_frame, text= "Hide List", width=8, style='window.TButton', command=listlevel.hide_listbox) # destory to quit
        self.listbox_button.pack(side=tk.LEFT,padx=5)

        self.setting_button = ttk.Button(self.buttondown_frame, text= "Settings", width=8, style='window.TButton', command=settinglevel.setting_buttonclick) # destory to quit
        self.setting_button.pack(side=tk.LEFT,padx=5)
        
        self.enhancer_button = ttk.Button(self.buttondown_frame, text= "Enhance", width=8, style='window.TButton', command=settinglevel.enhancer_show) # destory to quit
        self.enhancer_button.pack(side=tk.LEFT,padx=5)
        
        # Error label
        self.error_frame = ttk.Frame(self.parent, style='Warning.TFrame')               
        self.error_frame.pack(pady=0, fill="y", side = tk.BOTTOM)
        self.error_label = tk.Label(self.error_frame, text = "", fg = "red", font = ("Arial", 10))
        self.error_label.pack()
        
        # Path
        self.folder_frame = ttk.Frame(self.parent, style='Warning.TFrame')           
        self.folder_frame.pack(pady=0, fill="y", side = tk.BOTTOM)               # pady means gap of y-axis, fill both means aligh to left and right
        self.folder_label = ttk.Label(self.folder_frame, text = "Folder Name : " ,style='fg.TLabel')
        self.folder_label.pack(side=tk.LEFT, padx = 5)
        self.reset_button = ttk.Button(self.folder_frame, text= "Reset", width=4.2, command=self.reset_entry, style='primary.Outline.TButton')
        self.reset_button.pack(side =tk.RIGHT, padx = 5)
        self.browse_var = tk.StringVar()
        self.browse_var.set("Browse File")
        self.browse_var.trace("w", self.browse_var_change)
        self.browse_menubutton = ttk.Menubutton(self.folder_frame, text='Browse', style='primary.Outline.TButton')
        self.browse_menubutton.pack(side=tk.RIGHT, padx = 2)
        menu = tk.Menu(self.browse_menubutton)
        menu.add_radiobutton(label="File", value="file", variable=self.browse_var)
        menu.add_radiobutton(label="List", value="list", variable=self.browse_var)
        menu.add_radiobutton(label="Directory", value="dir", variable=self.browse_var)
        self.browse_menubutton['menu'] = menu
        self.folder_entry = tk.Entry(self.folder_frame, width=120 , background='gray25')
        self.folder_entry.insert(1, settinglevel.default_path)
        self.folder_entry.pack(side=tk.LEFT)
    
        # Up Button
        self.buttonup_frame = ttk.Frame(self.parent,style='inputbg.TFrame')
        self.buttonup_frame.pack(fill = "y", side = tk.BOTTOM, pady = 5)
        self.backward_button = ttk.Button(self.buttonup_frame, text= u"\u2B98", width=3, command=self.backward, style='second.TButton')
        self.backward_button.pack(side =tk.LEFT, padx = 20)
        self.full_button = ttk.Button(self.buttonup_frame, text= u"\u25a3", width=4, command=fulllevel.enter_full, style='second.TButton')
        self.full_button.pack(side =tk.LEFT, padx = 20)
        self.forward_button = ttk.Button(self.buttonup_frame, text= u"\u2B9A", width=3, command=self.forward, style='second.TButton')
        self.forward_button.pack(side =tk.LEFT, padx = 20)
        
        # gripper for resizing
        self.grip = ttk.Sizegrip(self.parent)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.bind("<B1-Motion>", self.window_resize)
        
        self.check_width = [self.parent.winfo_width(), self.parent.winfo_width()]
        self.check_height = [self.parent.winfo_height(), self.parent.winfo_height()]
        
        self.parent.bind("<Configure>", self.event_resize)           # trigger event, after loading GUI
        self.parent.bind("<MouseWheel>", self.event_zoom)            # trigger zoom event
        self.parent.bind("<Up>", self.gif_speedup)
        self.parent.bind("<Down>", self.gif_speeddown)
        self.parent.bind("<Right>", self.forward)
        self.parent.bind("<Left>", self.backward)
        self.parent.bind("<p>", self.gif_pause)
        self.parent.bind("<FocusIn>", self.event_focusin)
        
        self.parent.bind("<Tab>", settinglevel.enhancer_click)
        self.parent.bind("<q>", self.brightness_increase)
        self.parent.bind("<w>", self.brightness_decrease)
        self.parent.bind("<e>", self.contrast_increase)
        self.parent.bind("<r>", self.contrast_decrease)
        self.parent.bind("<t>", self.sharpness_increase)
        self.parent.bind("<y>", self.sharpness_decrease)
        self.parent.bind("<u>", self.color_increase)
        self.parent.bind("<i>", self.color_decrease)
        
        self.anticlock_button.config(state=tk.DISABLED)
        self.clock_button.config(state=tk.DISABLED)
 
        #self.after(1, self.set_appwindow)    # put window in taskbar
        self.set_appwindow()

        self.gif_con_create()
        
        filepath = str(self.folder_entry.get())
            
        if filepath != "":
            if os.path.splitext(filepath)[1] in self.supported_list:
                self.dataframe_reset()
                self.after(10, self.import_list, filepath)
            
            else:
                self.after(10, self.go)
    
    def browse_var_change(self, *args):
        
        browse_var =  self.browse_var.get()
        # print(browse_var)
        
        if browse_var == "file":
            self.browse_file()
        
        elif browse_var == "list":
            self.browse_list()
        
        elif browse_var == "dir":
            self.browse_directory()
    
    def browse_file(self):
        print("browse_file")
        logging.info("browse_file")
        
        file_name = filedialog.askopenfilename(filetypes = (("Image file", list(self.supported_img) + list(self.supported_ani) + list(self.supported_vid)),))
        
        if file_name == "":     # cancel
            return None
        
        file_name = os.path.split(file_name)[0] + "\\" + os.path.split(file_name)[1]   # due to diff format of sys.argv[1] and browse file path
        browsefilelist = []
        browsefilelist.append(file_name)
        self.folder_entry.insert(1, str(file_name)) 
        
        if len(window.fullfilelist) > 0:
            self.append_filelist(browsefilelist)
        
        else:
            self.reset_entry()
            self.dataframe_reset()
            
            self.go(browsefilelist)

                    
    def browse_list(self):
        print("browse_list")
        logging.info("browse_list")

        file_name = filedialog.askopenfilename(filetypes = (("List file", list(self.supported_list)),))
        
        if file_name == "":        # cancel
            return None
        
        file_name = os.path.split(file_name)[0] + "\\" + os.path.split(file_name)[1]   # due to diff format of sys.argv[1] and browse file path
    
        self.import_list(file_name)
        
    def browse_directory(self):
        print("browse_directory")
        logging.info("browse_directory")
        
        dir_name = filedialog.askdirectory()
        
        if dir_name == "":     # cancel
            return None
    
        browsefilelist = self.generate_list(dir_name)
        
        if len(browsefilelist) > 0:
            if len(window.fullfilelist) > 0:
                self.append_filelist(browsefilelist)
            
            else:
                self.reset_entry()
                self.dataframe_reset()
                
                self.go(browsefilelist)
        
        else:
            exception_dirnosupportedfile()
        
    def append_filelist(self, add_filelist):
        print("append_filelist")
        logging.info("append_filelist")   
        
        listlevel.rad_button.config(state=tk.DISABLED)
        listlevel.filter_button.config(state=tk.DISABLED)
        self.dataframe_reset(True)
        
        i = 0
        for path in add_filelist:
            i = i + 1
            window.fullfilelist.append(path)
            
            filename = os.path.split(path)
            listlevel.listbox1.insert(tk.END, filename[1])                      # put file name in listbox
        
        print("Import %i items" %i)
        logging.info("Import %i items" %i)
        
        for path in add_filelist:
            file_ext = os.path.splitext(path)[1].lower()
            
            if file_ext in window.supported_img:         # find out list without img to deactivate photo album mode and manga mode
                window.list_with_img = True
                break
        
        if window.dataframe_list is None and not window.is_web_mode:
            window.thread_dataframe_create = threading.Thread(target = window.dataframe_create)
            window.thread_dataframe_create.start()
        
        window.clear_all_cache()
        
        window.parent.update()
        
    def window_predrag(self, event):
        
        self.drag = False
        
        if settinglevel.window_state == "zoomed":      # changed to window normal if zoomed
            self.window_normal()
            
        print("drag_window")    
        logging.info("drag_window")
        
        self.offsetx = event.x
        self.offsety = event.y
        
    def window_drag(self, event):
        # print("drag_window_motion")
        # logging.info("drag_window_motion")
        
        time.sleep(0.005)                             # limit the frequency
        self.drag_x = self.parent.winfo_x() + event.x - self.offsetx
        self.drag_y = self.parent.winfo_y() + event.y - self.offsety
    
        # self.parent.geometry('+{x}+{y}'.format(x=x,y=y))    # disable updating geometry to avoid crash
        
        self.drag = True
        
        self.is_stop_ani = True
        self.pic_canvas.delete("all")
        
    def drag_release(self, event):
        print("drag_release")
        logging.info("drag_release")
        
        if self.drag:
            self.drag = False
            self.is_stop_ani = False
            
            self.parent.geometry('+{x}+{y}'.format(x=self.drag_x,y=self.drag_y))
            
            if len(window.fullfilelist) > 0:
                filepath = window.fullfilelist[window.fileindex]
                file_ext = os.path.splitext(filepath)[1].lower()      # separate file name and extension
        
                if file_ext in window.supported_img:                 # show in window mode
                    window.ShowIMG(filepath)
                
                elif file_ext in (window.supported_ani | window.supported_vid):
                    window.ShowANI(filepath)
    
    def reset_entry(self):
        print("reset_entry")
        logging.info("reset_entry")
        
        self.is_stop_ani = True
        self.pic_canvas.delete("all")
        
        self.folder_entry.delete(0, "end")
            
        self.fullfilelist = []
        self.dataframe_stop = True
        listlevel.listbox1.delete(0, "end")
        listlevel.listbox2.delete(0, "end")
        listlevel.listbox3.delete(0, "end")
        listlevel.listbox4.delete(0, "end")
        listlevel.listbox5.delete(0, "end")
        
        try:
            self.clear_all_cache()
        
        except:    # force run as there will be FileNotFoundError
            print("failed to clear all cache (probably manga)")
            logging.info("failed to clear all cache (probably manga")
        
        self.anticlock_button.config(state=tk.DISABLED)
        self.clock_button.config(state=tk.DISABLED)
        listlevel.rad_button.config(state=tk.DISABLED)
        listlevel.filter_button.config(state=tk.DISABLED)

        self.error_label.config(text = "")

        self.gif_con.attributes('-topmost', False)
        self.gif_con.withdraw()
        
        if self.is_web_mode:
            self.quit_web_mode()
        
            try:
                while window.thread_batch_download.is_alive():
                    window.update()
                    time.sleep(0.02)
            
            except:
                print("thread_back_download ended")
                logging.info("thread_back_download ended")
            
            else:
                print("thread_back_download ended")
                logging.info("thread_back_download ended")
            
    def set_appwindow(self):
        print("set_appwindow")
        logging.info("set_appwindow")
        
        GWL_EXSTYLE=-20                                       # for showing program in taskbar
        WS_EX_APPWINDOW=0x00040000
        WS_EX_TOOLWINDOW=0x00000080
        
        hwnd = windll.user32.GetParent(self.parent.winfo_id())
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        
        # re-assert the new window style
        self.parent.wm_withdraw()
        self.after(1, self.show_appwindow)
    
    def show_appwindow(self):
        print("show_appwindow")
        logging.info("show_appwindow")
        
        self.parent.state("zoomed")                    # fix bug of "can't bring to back before dragging the window"
        self.parent.state("normal")

        try:
            GetMonitorInfo(MonitorFromPoint((int(settinglevel.window_x),0)))    # error if multiple screen last time and single screen this time
        
        except:
            if int(settinglevel.window_x) > window.full_w:
                settinglevel.window_x = 300     # default window x
                
            elif int(settinglevel.window_x) < 0:
                settinglevel.window_x = 300     # default window x
        
        if settinglevel.window_state == "normal":
            self.parent.geometry('%dx%d+%d+%d' %(int(settinglevel.window_width), int(settinglevel.window_height), int(settinglevel.window_x), int(settinglevel.window_y))) # re adjust window size
        
        else:
            self.max_button.config(text = "\u2583", command = self.window_normal)

            window_mid_pt = int(int(settinglevel.window_x) + int(settinglevel.window_width) / 2)   # find the mid point of parent to match window's behaviour
        
            try:
                monitor_info = GetMonitorInfo(MonitorFromPoint((window_mid_pt,0)))   # to get the current monitor based on x,y
            
            except:
                monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))                       # error if x,y not existent
                
            # monitor_area = monitor_info.get("Monitor")
            work_area = monitor_info.get("Work")                            # work area is the area without taskbar
            # print("The taskbar height is {}.".format(monitor_area[3]-work_area[3]))
            # print(monitor_area)
            # print(work_area)
            
            width = work_area[2] - work_area[0]
            height = work_area[3] - work_area[1]
            x = work_area[0]
            y = work_area[1]
            
            self.parent.geometry("%dx%d+%d+%d" %(width, height, x, y)) 
            
        self.parent.wm_deiconify()
        self.parent.attributes('-topmost', True)
        # self.parent.geometry('%dx%d+%d+%d' %(int(settinglevel.window_width), int(settinglevel.window_height), int(settinglevel.window_x), int(settinglevel.window_y))) # re adjust window size
        self.parent.update()
        
        time.sleep(0.05)                          # perform better after sleep
        self.parent.attributes('-topmost', False)      # force window to the front but not always
    
    def gif_con_create(self):
        print("gif_con_create")
        logging.info("gif_con_create")
        
        # Controller in gif
        s = ttk.Style()
        s.configure('my.TButton', font=('Arial', 15))
        
        self.gif_con.resizable(False,False)
        self.gif_con.overrideredirect(1)
        self.gif_con.geometry("180x40+%d+%d" % (int(settinglevel.gif_con_x), int(settinglevel.gif_con_y)))
                              
        self.gif_speeddown_button = ttk.Button(self.gif_con, text= u"\u2bec", width=2, style='my.TButton', command = self.gif_speeddown)
        self.gif_speeddown_button.pack(side =tk.LEFT, padx = 5)
        
        self.gif_speedup_button = ttk.Button(self.gif_con, text= u"\u2bee", width=2, style='my.TButton', command = self.gif_speedup)
        self.gif_speedup_button.pack(side =tk.LEFT, padx = 5)
        
        self.gif_pause_button = ttk.Button(self.gif_con, text= "\u23ef", width=2, style='my.TButton', command = self.gif_pause)
        self.gif_pause_button.pack(side =tk.RIGHT, padx = 5)
        
        self.gif_con.attributes('-topmost', False)
        self.gif_con.withdraw()
        
        # Gif Controller Drag
        self.gif_con_offsetx = 0
        self.gif_con_offsety = 0
        self.gif_con.bind('<Button-1>', self.gif_con_predrag)
        self.gif_con.bind('<B1-Motion>', self.gif_con_drag)
    
    def gif_con_predrag(self, event):
        print("drag_gif_con")    
        logging.info("drag_gif_con")
        
        self.gif_con_offsetx = event.x
        self.gif_con_offsety = event.y
        
    def gif_con_drag(self, event):
        
        x = self.gif_con.winfo_x() + event.x - self.gif_con_offsetx
        y = self.gif_con.winfo_y() + event.y - self.gif_con_offsety
    
        self.gif_con.geometry('+{x}+{y}'.format(x=x,y=y))

# In[Control Storage]

    def clear_all_cache(self):
        print("clear_all_cache")    
        logging.info("clear_all_cache")
        
        window.stor.stop_storage(True)
        fulllevel.stor.stop_storage(True)
        
        try:
            fulllevel.photoalbum.stop_storage(True)
        
        except:
            pass
        
        try:
            fulllevel.manga.stop_storage(True)
        
        except:
            pass
            # print("failed to stop manga cache")
            # logging.info("failed to stop manga cache")
        
        self.reset_storage_size()
    
    def reset_storage_size(self):
        
        window.storage_size = {}                   
        window.storage_size["window"] = [0] * len(window.fullfilelist)
        window.storage_size["fulllevel"] = [0] * len(window.fullfilelist)
        window.storage_size["photoalbum"] = [0] * len(window.fullfilelist)
        window.storage_size["manga"] = [0] * len(window.fullfilelist)
    
    def cal_storage_size(self):
        
        size_values = list(window.storage_size.values())
        total_storage_size = 0
        for i in range(len(size_values)):
            total_storage_size = total_storage_size + sum(size_values[i])

        return round(total_storage_size, 2)

# In[Go Button]
    
    def go(self, direct_list = None):
        print("go")
        logging.info("go")
        
        window.is_full_mode = False
        window.is_web_mode = False
        window.is_stop_ani = True
        window.is_gif_pause = False
        window.zoom_factor = 1
        window.list_with_img = False
        
        #timer_start = time.perf_counter()
        
        window.origX = window.pic_canvas.xview()[0]                # original canvas position for zoom and move
        window.origY = window.pic_canvas.yview()[0]

        fulllevel.origX = window.pic_canvas.xview()[0]                # original canvas position for zoom and move
        fulllevel.origY = window.pic_canvas.yview()[0]
        
        window.full_button.config(state=tk.DISABLED)            # to fix the bug when enter_full too fast before fully downloading 1st pic
        
        window.pic_canvas.bind('<ButtonPress-1>', window.move_from)
        window.pic_canvas.bind('<B1-Motion>', window.move_to)
        
        filepath = str(window.folder_entry.get())
        
        if len(window.fullfilelist) > 0:                        # reset entry if a full file list already exists
            window.reset_entry()
        
        if direct_list is not None:                             # from .list or from filter/random
            window.fullfilelist = direct_list
        
        else:
            if filepath[:4] == "http":                          # from web download
                window.fullfilelist = self.enter_web_mode(filepath)
                
            else:                                               # os.listdir or os.walk
                window.fullfilelist = self.generate_list(filepath)
                self.dataframe_reset()
        
        if len(window.fullfilelist) == 0:
            if direct_list == None:
                exception_dirnosupportedfile()
                
            else:
                window.error_label.config(text = "No supported file in the list")
                return None
        
        if window.dataframe_list is None and not window.is_web_mode:
            # window.dataframe_create()
            window.thread_dataframe_create = threading.Thread(target = window.dataframe_create)
            window.thread_dataframe_create.start()

        self.reset_storage_size()
        window.stor.create_reset_storage()
        fulllevel.stor.create_reset_storage()

        for path in window.fullfilelist:
            filename = os.path.split(path)
            listlevel.listbox1.insert(tk.END, filename[1])                      # put file name in listbox

        for path in window.fullfilelist:
            file_ext = os.path.splitext(path)[1].lower()
            
            if file_ext in window.supported_img:         # find out list without img to deactivate photo album mode and manga mode
                window.list_with_img = True
                break

        window.parent.update()

        try:
            window.fileindex = window.fullfilelist.index(filepath)                 # 0 if filepath is dir
        
        except:
            window.fileindex = 0

        filepath = window.fullfilelist[window.fileindex]
            
        file_ext = os.path.splitext(filepath)[1].lower()      # separate file name and extension
        
        window.folder_entry.delete(0,"end")
        window.folder_entry.insert(1, filepath)             # replace folder entry
        
        len_fullfilelist = len(window.fullfilelist)
        print("Import %i items" %len_fullfilelist)
        logging.info("Import %i items" %len_fullfilelist)
        
        file_name = os.path.split(filepath)[1]

        #time_diff = time.perf_counter() - timer_start
        window.stor.stop_backend = False
        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
        window.stor.thread_storage.start()
        
        if window.check_photoimage(window.fileindex):
            window.stor.thread_storage_photoimage = threading.Thread(target = window.stor.backend_photoimage_storage, args = (window.fileindex,))
            window.stor.thread_storage_photoimage.start()
        
        if window.is_web_mode:   # download next 20 pages
            window.thread_batch_download = threading.Thread(target = window.batch_download, args = (self.next_path, self.url_cookies, self.web_output_folder, 1, 20))
            window.thread_batch_download.start()
            
        listlevel.listbox1.delete(window.fileindex)
        listlevel.listbox1.insert(window.fileindex, u"\u25B6 " + file_name)
        listlevel.listbox1.see(window.fileindex)
        listlevel.listbox2.see(window.fileindex)
        listlevel.listbox3.see(window.fileindex)
        listlevel.listbox4.see(window.fileindex)
        listlevel.listbox5.see(window.fileindex)
        
        window.full_button.config(state=tk.NORMAL)
        
        #print(time_diff)
        #time2 = time.perf_counter()
        #print("time diff: ", time2-time1)
        
        if file_ext in window.supported_img:                 # show in window mode
            window.ShowIMG(filepath)
        
        elif file_ext in (window.supported_ani | window.supported_vid):
            # window.ShowANI(filepath)
            window.after(10, window.ShowANI, filepath)       # avoid process stuck in ShowANI in direct list go
    
    def generate_list(self, filepath):
        print("generate_list")
        logging.info("generate_list")
        
        #time1 = time.perf_counter()
        
        window.is_parent = settinglevel.parent_check.get()
        if not os.path.isdir(filepath):              # handle dir path
            filesplit = os.path.split(filepath)           # separate dir path and file name
        
        else:
            filesplit = [filepath, ""]
        
        generate_file_list = []
        
        if filepath == "":
            exception_emptypath()
        
        if not os.path.exists(filepath):         # check whether the dir exists
            exception_dirnotfound()
            
        if not os.access(filepath, os.R_OK):     # check whether the dir has read permission
            exception_dirnopermission()
        
        if not window.is_parent:                      # exclude sub folder
            filelist = os.listdir(filesplit[0])  
            
            if settinglevel.is_natsort:
                try:
                    filelist = sorted(filelist,key = self.nat_sort)
                    print("Nat Sort Successful")
                    logging.info("Nat Sort Successful")
                    
                except TypeError as e:
                    print("TypeError in Nat Sort: ", e)
                    logging.info("TypeError in Nat Sort")
                    filelist.sort()
                    
            else: 
                 filelist.sort()
                 
            for filename in filelist:
                
                fullpathname = os.path.join(filesplit[0], filename)
                file_ext = os.path.splitext(fullpathname)[1].lower()
                
                if file_ext in (window.supported_img | window.supported_ani | window.supported_vid):  #filter not support format
                    generate_file_list.append(fullpathname)    # full path in list
  
                #else:
                    #print("Not Supported : ", filename)
                    #logging.info("Not Supported : %s", filename)
        
        else:                                        # include sub folder
            file_walk = os.walk(filesplit[0])
            
            timeout_start = time.time()
            timeout = 20
            
            for root,dir,files in file_walk:
                dir.sort()        # dir can't be in nat sort as the sorted function doesn't work for dir in os.walk
                # dir = sorted(dir,key = self.nat_sort)
                if settinglevel.is_natsort:
                    try:
                        files = sorted(files,key = self.nat_sort)
                        print("Nat Sort Successful")
                        logging.info("Nat Sort Successful")
                        
                    except TypeError:
                        print("TypeError in Nat Sort")
                        logging.info("TypeError in Nat Sort")
                        files.sort()
                else:
                    files.sort()

                for file in files:
                    
                    if time.time() > timeout_start + timeout:       # timeout if the dir too large
                        exception_dirtoolarge()
                     
                    fullpathname = os.path.join(root,file)
                    file_ext = os.path.splitext(fullpathname)[1].lower()
                    
                    if file_ext in (window.supported_img | window.supported_ani | window.supported_vid):    #filter not support format
                        generate_file_list.append(fullpathname)
                    
                    #else:
                     #   if len(file_ext) > 0:
                      #      print("Not Supported : ", file)
                       #     logging.info("Not Supported : %s", file)
        
        return generate_file_list
    
    def nat_sort(self, file):
        
        file_ext = os.path.splitext(file)[1].lower()
        
        if not file_ext in (self.supported_img | self.supported_ani | self.supported_vid) and file_ext != "":
            return ["ZZZ"]                                # return a list with any string 
        
        file_name = os.path.splitext(file)[0]             # ignore file ext
        file_name = file_name.lower()                     # ignore upper character

        file_name_list = list(file_name)
        symbols = r"!@#$%^&*()_+={}|<>?[]\"'~`-/"
        symbols_list = list(symbols)

        if file_name_list[0] in symbols_list:
            file_name_list.insert(0, "A")                 # give priority to symbol, only for first character
        
        else:
            file_name_list.insert(0, "B")                     # add first element to prevent TypeError
    
        i = 0
        while True:
            if i == len(file_name_list) - 1:
                break
            
            if file_name_list[i].isnumeric() and file_name_list[i+1].isnumeric():
                file_name_list[i] = file_name_list[i] + file_name_list[i+1]     # merge numbers
                del file_name_list[i+1]
    
            elif not file_name_list[i].isnumeric() and not file_name_list[i+1].isnumeric():
                file_name_list[i] = file_name_list[i] + file_name_list[i+1]     # merge string
                del file_name_list[i+1]
            
            else:
                i = i + 1
        
        for j in range(len(file_name_list)):
            try:
                file_name_list[j] = int(file_name_list[j])        # change numbers in string to integer
            
            except ValueError:
                pass
        
        # if file_ext == "":
        #     print(file_name_list[:])
        
        return file_name_list[:]                                  # return whole list. it can sort one by one
    
    def import_list(self, list_path):
        print("import_list")
        logging.info("import_list")
        
        importfilelist = []
        
        importfilelist = self.import_files(list_path, importfilelist)
        
        unique_importfilelist = []
        
        for file in importfilelist:
           if file not in unique_importfilelist:   # drop duplicates within a list
               unique_importfilelist.append(file) 
        
        if len(unique_importfilelist) == 0:
            exception_dirnosupportedfile_list()                 # raise error if can't import from list

        else:
            # window.go(unique_importfilelist)
            if len(window.fullfilelist) > 0:
                self.append_filelist(unique_importfilelist)
            
            else:
                self.reset_entry()
                self.dataframe_reset()
                
                self.go(unique_importfilelist)
        
    def import_files(self, file_path, importfilelist):
        print("import_files")
        logging.info("import_files")
        
        with open(file_path, encoding="utf-8") as list_imported:
            lines = list_imported.read().splitlines()
            
            for line in lines:
                line = line.replace("\\", chr(92))              # replace \\ with \
                file_ext = os.path.splitext(line)[1].lower()
                
                # import files
                if file_ext in (self.supported_img | self.supported_ani | self.supported_vid):
                    importfilelist.append(line)
                    
                # import list of list
                elif file_ext in self.supported_list:
                    importfilelist = self.import_files(line, importfilelist)  # recursion to solve list inside list
                
                # import directory with search
                else:          
                    if os.path.isdir(line):            # check if valid directory
                        importfilelist = self.import_directory(line, importfilelist)
                    
                    else:
                        find_txt = line.find("*")             # * for search in directory
    
                        if find_txt >= 0:                     # return the position of *, -1 if no result
                            folder_path = os.path.split(line)[0]
                            search_file = os.path.split(line)[1].replace("*", "")
    
                            if os.path.isdir(folder_path):
                                    importfilelist = self.import_directory(folder_path, importfilelist, search_file)
                    
                if file_ext in window.supported_img and not window.list_with_img:         # find out list without img to deactivate photo album mode and manga mode
                    window.list_with_img = True
        
        return importfilelist
    
    def import_directory(self, folder_path, importfilelist, search_file=None):
        print("import_directory")
        logging.info("import_directory")
        
        filelist = os.listdir(folder_path)
        if settinglevel.is_natsort:
            try:
                filelist = sorted(filelist,key = self.nat_sort)
                print("Nat Sort Successful")
                logging.info("Nat Sort Successful")
                
            except TypeError as e:
                print("TypeError in Nat Sort: ", e)
                logging.info("TypeError in Nat Sort")
                filelist.sort()
                
        else: 
             filelist.sort()
        
        for file in filelist:
            if search_file == None:
                file_ext = os.path.splitext(file)[1].lower()
            
                if file_ext in (self.supported_img | self.supported_ani | self.supported_vid):
                    file_path = os.path.join(folder_path, file)
                    importfilelist.append(file_path)
            
            else:
                file_ext = os.path.splitext(file)[1].lower()
            
                if file_ext in (self.supported_img | self.supported_ani | self.supported_vid):
                    find_txt = file.find(search_file)
                    
                    if find_txt >= 0:
                        file_path = os.path.join(folder_path, file)
                        importfilelist.append(file_path)
        
        return importfilelist
    
# In[DataFrame]
    
    def dataframe_create(self):
        print("dataframe_create")
        logging.info("dataframe_create")
        
        # create array
        df = pd.DataFrame(window.fullfilelist)
        df.columns = ["Full_Path"]
        df = df.drop_duplicates()
        df = df.reset_index(drop=True)
        
        window.dataframe_stop = False
        
        window.dataframe_list = df
        
        window.thread_dataframe_create_filter = threading.Thread(target = window.dataframe_create_filter)
        window.thread_dataframe_create_filter.start()
        
        window.thread_dataframe_create_random = threading.Thread(target = window.dataframe_create_random)
        window.thread_dataframe_create_random.start()
        
        window.thread_dataframe_create_filter.join()
        window.thread_dataframe_create_random.join()
        
        listlevel.rad_button.config(state=tk.NORMAL)
        listlevel.filter_button.config(state=tk.NORMAL)
        
    def dataframe_create_random(self):
        print("dataframe_create_random: start")
        logging.info("dataframe_create_random: start")
        
        # create array
        df = window.dataframe_list
 
        pre_file_folder = ""
        pre_file_name_list = []
        list_id = -1
        group_index = -1
        group_id = -1
        list_id_list = []
        group_index_list = []
        group_id_list = []
        
        for filepath in df["Full_Path"]:
            if self.dataframe_stop:
                print("dataframe_create_filter: stopped")
                logging.info("dataframe_create_filter: stopped")
                
                return None
            
            file_folder = os.path.split(filepath)[0]
            file_name = os.path.split(filepath)[1]
                
            # file name check
            file_name_noext = os.path.splitext(file_name)[0]
            file_ext = os.path.splitext(file_name)[1].lower()

            file_name_list = list(file_name_noext)
        
            i = 0
            while True:
                if i == len(file_name_list) - 1:
                    break
                
                if file_name_list[i].isnumeric() and file_name_list[i+1].isnumeric():
                    file_name_list[i] = file_name_list[i] + file_name_list[i+1]     # merge numbers
                    del file_name_list[i+1]
        
                elif not file_name_list[i].isnumeric() and not file_name_list[i+1].isnumeric():
                    file_name_list[i] = file_name_list[i] + file_name_list[i+1]     # merge string
                    del file_name_list[i+1]
                
                else:
                    i = i + 1
            
            for j in range(len(file_name_list)):
                try:
                    file_name_list[j] = int(file_name_list[j])        # change numbers in string to integer
                
                except ValueError:
                    pass
            
            # print(file_name_list)
            
            # add list_id
            list_id = list_id + 1
            list_id_list.append(list_id)
            
            file_name_diff = []
            try:
                for i in range(len(file_name_list)):
                    if file_name_list[i] != pre_file_name_list[i]:
                        file_name_diff.append(file_name_list[i])
            
            except:
                file_name_diff.append(file_name_list[i])
            
            if len(pre_file_name_list) > len(file_name_list):
                file_name_diff.append("_LONGER")          # avoid int for the below isinstance(file_name_diff[0], int)
            
            # print(file_name_diff)
            
            # comparison and add group index and group id
            if file_folder == pre_file_folder:     
                if len(file_name_diff) == 1:
                    if isinstance(file_name_diff[0], int):
                        group_index_list.append(group_index)
                        group_id = group_id + 1
                        group_id_list.append(group_id)
                    
                    else:
                        group_index = group_index + 1
                        group_index_list.append(group_index)
                        group_id = 0
                        group_id_list.append(group_id)
                
                elif len(file_name_diff) <=2 and "(enhanced)" in file_folder:   # hard coded to tackle random number in enhanced file names
                    if isinstance(file_name_diff[0], int):    
                        group_index_list.append(group_index)
                        group_id = group_id + 1
                        group_id_list.append(group_id)
                    
                    else:
                        group_index = group_index + 1
                        group_index_list.append(group_index)
                        group_id = 0
                        group_id_list.append(group_id)
                
                else:
                    group_index = group_index + 1
                    group_index_list.append(group_index)
                    group_id = 0
                    group_id_list.append(group_id)
                
            else:
                group_index = group_index + 1
                group_index_list.append(group_index)
                group_id = 0
                group_id_list.append(group_id)
                
            pre_file_folder = file_folder
            pre_file_name_list = file_name_list
            
        df.insert(loc=len(df.columns), column="List_ID", value=list_id_list)
        df.insert(loc=len(df.columns), column="Group_Index", value=group_index_list)
        df.insert(loc=len(df.columns), column="Group_ID", value=group_id_list)
    
        # save_path = r"C:\Users\simon\Practice\dataframe_list_export.csv"
        # df.to_csv(save_path, index=False)
        
        print("dataframe_create_random: done")
        logging.info("dataframe_create_random: done")
    
    def dataframe_create_filter(self):
        print("dataframe_create_filter: start")
        logging.info("dataframe_create_filter: start")
        
        # create array
        df = window.dataframe_list
        
        wh_list = []
        ext_list = []
        
        for filepath in df["Full_Path"]:
            if self.dataframe_stop:
                print("dataframe_create_filter: stopped")
                logging.info("dataframe_create_filter: stopped")
                
                return None
            
            file_name = os.path.split(filepath)[1]
            file_ext = os.path.splitext(file_name)[1].lower()

            # ext check
            if file_ext in window.supported_img:
                ext_type = "img"
                ext_list.append(ext_type)
            
            elif file_ext in (window.supported_ani | window.supported_vid):
                ext_type = "ani"
                ext_list.append(ext_type)
            
            else:
                ext_type = ""
                ext_list.append(ext_type)
                
            # width height check
            if file_ext in (window.supported_img | window.supported_ani):
                # img = Image.open(filepath)
                # img_w, img_h = img.size
                
                img_w, img_h = imagesize.get(filepath)   # module imagesize is the fastest way to get image size. tested myself
                
                if img_h > img_w:
                    wh_type = "h>w"
                    wh_list.append(wh_type)
                
                else:
                    wh_type = "w>h"
                    wh_list.append(wh_type)
            
            elif file_ext in window.supported_vid:
                vidcap = cv2.VideoCapture(filepath)
                success = True
                while success:
                    success,img = vidcap.read()
                    if success:          # get the first frame
                        break
            
                img_h, img_w = img.shape[:2]
                
                if img_h > img_w:
                    wh_type = "h>w"
                    wh_list.append(wh_type)
                
                else:
                    wh_type = "w>h"
                    wh_list.append(wh_type)
                    
            else:
                wh_type = ""
                wh_list.append(wh_type)
            
        df.insert(loc=len(df.columns), column="File_ext", value=ext_list)
        df.insert(loc=len(df.columns), column="Pic_WidthHeight", value=wh_list)
    
        # save_path = r"C:\Users\simon\Practice\dataframe_list_export.csv"
        # df.to_csv(save_path, index=False)
        
        print("dataframe_create_filter: done")
        logging.info("dataframe_create_filter: done")
        
    def filelist_to_go(self, direct_list):
        print("filelist_to_go")
        logging.info("filelist_to_go")
        
        if window.is_full_mode and not window.is_stop_ani:     # for ANI in full mode
            self.thread_stopani_interrpution = False
            thread_stopani = threading.Thread(target = self.thread_stopani)
            thread_stopani.start()
            
            window.go(direct_list)
            
            self.thread_stopani_interrpution = True
            thread_stopani.join()
            
            fulllevel.enter_full()
            
            if window.is_slide_check:
                self.thread_stopani_interrpution = False
                thread_stopani = threading.Thread(target = self.thread_stopani)
                thread_stopani.start()
                
                fulllevel.quit_slide()
                
                self.thread_stopani_interrpution = True
                thread_stopani.join()
                
                fulllevel.start_slide()
            
        elif window.is_full_mode:
            if window.is_photoalbum_mode:          # photo album mode
                window.go(direct_list)
                fulllevel.enter_full()
                
                window.stor.stop_storage(True)
                fulllevel.stor.stop_storage(True)
                fulllevel.photoalbum.stop_storage(True)
                del fulllevel.photoalbum
                
                print("start photoalbum thread")
                logging.info("start photoalbum thread")
                fulllevel.photoalbum = Storage("photoalbum")   
                fulllevel.photoalbum.create_reset_storage()
                fulllevel.photoalbum.thread_storage = threading.Thread(target = fulllevel.photoalbum.backend_storage, args = (window.fileindex,))
                
                fulllevel.photoalbum.stop_backend = False
                fulllevel.photoalbum.thread_storage.start()
                
                listlevel.listbox1.see(self.fileindex)
                listlevel.listbox2.see(self.fileindex)
                listlevel.listbox3.see(self.fileindex)
                listlevel.listbox4.see(self.fileindex)
                listlevel.listbox5.see(self.fileindex)
            
            else:
                if window.is_slide_check:          # slide mode
                    window.go(direct_list)
                    fulllevel.enter_full()
                    fulllevel.quit_slide()
                    fulllevel.start_slide()
                
                else:                          # simple full or manga mode
                    if window.is_manga_mode:
                        fulllevel.quit_manga()
                    
                    window.go(direct_list)
                    fulllevel.enter_full()
        
        else:                                   # window mode
            window.go(direct_list)
            
    def dataframe_reset(self, append=False):
        print("dataframe_reset")
        logging.info("dataframe_reset")
        
        self.dataframe_stop = True
        
        if self.random_button_process != 0:
            if append:        # reset list before append list
                self.random_undo()
                
            self.random_button_process = 0   
            listlevel.rad_button.config(text = "Random List")
            
        window.dataframe_list = None

    def thread_stopani(self):
        print("thread_stopani")
        logging.info("thread_stopani")
        
        # for stopping ani otherwise it will stuck in ShowANI and can't process further
        
        while not self.thread_stopani_interrpution:
            window.is_stop_ani = True
            time.sleep(0.01)
        
        print("thread_stopani_interrpution")
        logging.info("thread_stopani_interrpution")

# In[Random Button]
    def random_button(self):
        # 0: no random
        # 1: random (list)
        # 2: random (group)
        
        listlevel.rad_button.config(state=tk.DISABLED)
        listlevel.filter_button.config(state=tk.DISABLED)
        
        window.update()
        
        self.random_button_process = self.random_button_process + 1

        if self.random_button_process > 2:
            self.random_button_process = 0
        
        print("random_button - %i" %self.random_button_process)
        logging.info("random_button - %i" %self.random_button_process)
        
        if window.dataframe_list is None:
            self.dataframe_create()
        
        if window.thread_dataframe_create_random.is_alive():
            window.thread_dataframe_create_random.join()
            
        if window.thread_dataframe_create_filter.is_alive():
            window.thread_dataframe_create_filter.join()
        
        if self.random_button_process == 0:
            self.random_undo()

            listlevel.rad_button.config(text = "Random List")
            listlevel.rad_button.config(state=tk.NORMAL)
                
        elif self.random_button_process == 1:   
            self.random_byfile()
            
            listlevel.rad_button.config(text = "Rad (Group)")
            listlevel.rad_button.config(state=tk.NORMAL)
                
        elif self.random_button_process == 2:
            self.random_bygroup()
            
            listlevel.rad_button.config(text = "Undo Rad")
            listlevel.rad_button.config(state=tk.NORMAL)
        
        listlevel.filter_button.config(state=tk.NORMAL)
        window.update()
        
    def random_byfile(self):
        print("random_byfile")
        logging.info("random_byfile")
   
        # random file list by List_ID
        df = window.dataframe_list

        random_number_list = df["List_ID"].tolist()
        random.shuffle(random_number_list)
        radfilelist = []
        dataframe_temp = []
        dataframe_temp = pd.DataFrame(dataframe_temp)
        
        for rad in random_number_list:
            # print(rad)
            rad_row = df.loc[(df["List_ID"].isin([rad]))]
            # print(rad_row)
            # rad_path = rad_row.iat[0,0]
            rad_row = rad_row.reset_index(drop=True)       # drop=True otherwise it will add a new column for new index
            rad_path = rad_row.at[0, "Full_Path"]
            
            radfilelist.append(rad_path)
            
            dataframe_temp = pd.concat([dataframe_temp, rad_row], ignore_index=True) # reset after concat otherwise it will add one more column
        
        window.dataframe_list = dataframe_temp

        # radfilelist = pd.DataFrame(radfilelist)
        # save_path = r"C:\Users\simon\Practice\dataframe_list_byfile_export.csv"
        # window.dataframe_list.to_csv(save_path, index=False)
        
        if window.filter:
            filter_wh_str = self.filter_wh.get()
            filter_imgani_str = self.filter_imgani.get()
            self.filter_process(filter_wh_str, filter_imgani_str)
            
        else:
            self.filelist_to_go(radfilelist)
            
    def random_bygroup(self):
        print("random_bygroup")
        logging.info("random_bygroup")
   
        # random file list by Group_Index and then sort by Group_ID
        
        df = window.dataframe_list
        
        temp_df = df["Group_Index"]
        temp_df = temp_df.drop_duplicates()
        random_number_list = temp_df.tolist()
        random.shuffle(random_number_list)
        
        radfilelist = []
        dataframe_temp = []
        dataframe_temp = pd.DataFrame(dataframe_temp)
        
        for rad in random_number_list:
            rad_group = df.loc[(df["Group_Index"].isin([rad]))]
            rad_group = rad_group.sort_values(by=["Group_ID"])
            rad_group = rad_group.reset_index(drop=True)     # drop=True otherwise it will add a new column for new index
            rad_group_rows = len(rad_group.index)
            
            dataframe_temp = pd.concat([dataframe_temp,rad_group], ignore_index=True)
            
            for i in range(rad_group_rows):
                # rad_path = rad_group.iat[i,0]
                rad_path = rad_group.at[i, "Full_Path"]
                radfilelist.append(rad_path)
        
        window.dataframe_list = dataframe_temp 
        
        # radfilelist = pd.DataFrame(radfilelist)
        # save_path = r"C:\Users\simon\Practice\dataframe_list_bygroup_export.csv"
        # window.dataframe_list.to_csv(save_path, index=False)
        
        if window.filter:
            filter_wh_str = self.filter_wh.get()
            filter_imgani_str = self.filter_imgani.get()
            self.filter_process(filter_wh_str, filter_imgani_str)
            
        else:
            self.filelist_to_go(radfilelist)
    
    def random_undo(self):
        print("random_undo")
        logging.info("random_undo")
   
        # back to normal; sort by List_ID
        df = window.dataframe_list

        random_number_list = df["List_ID"].tolist()
        random_number_list.sort()
        radfilelist = []
        dataframe_temp = []
        dataframe_temp = pd.DataFrame(dataframe_temp)
        
        for rad in random_number_list:
            rad_row = df.loc[(df["List_ID"].isin([rad]))]
            # rad_path = rad_row.iat[0,0]
            rad_row = rad_row.reset_index(drop=True)
            rad_path = rad_row.at[0,"Full_Path"]
            
            radfilelist.append(rad_path)
            
            dataframe_temp = pd.concat([dataframe_temp, rad_row], ignore_index=True)
            
        window.dataframe_list = dataframe_temp 
        
        # radfilelist = pd.DataFrame(radfilelist)
        # save_path = r"C:\Users\simon\Practice\dataframe_list_byfile_export.csv"
        # window.dataframe_list.to_csv(save_path, index=False)
        
        if window.filter:
            filter_wh_str = self.filter_wh.get()
            filter_imgani_str = self.filter_imgani.get()
            self.filter_process(filter_wh_str, filter_imgani_str)
            
        else:
            self.filelist_to_go(radfilelist)
            
# In[Filter Button]
        
    def filter_con_create(self):
        print("filter_con_create")
        logging.info("filter_con_create")
        
        # Controller in filter
        s = ttk.Style()
        s.configure('my.TButton', font=('Arial', 11))
        
        self.filter_con.resizable(False,False)
        self.filter_con.overrideredirect(1)
        self.filter_con.geometry("320x145+%d+%d" % (int(settinglevel.listbox_x), int(settinglevel.listbox_y)))
        
        self.wh_frame = ttk.Frame(self.filter_con, style='Warning.TFrame')           
        self.wh_frame.pack(pady=10, fill="y", side = tk.TOP)  
        
        self.imgani_frame = ttk.Frame(self.filter_con, style='Warning.TFrame')           
        self.imgani_frame.pack(pady=10, fill="y", side = tk.TOP)  
        
        self.button_frame = ttk.Frame(self.filter_con, style='Warning.TFrame')           
        self.button_frame.pack(pady=10, fill="y", side = tk.TOP)  
        
        self.wh_label = ttk.Label(self.wh_frame, text = " Width / Height Image :           " , style='fg.TLabel')
        self.wh_label.pack(pady=0, side= tk.LEFT)
        
        self.imgani_label = ttk.Label(self.imgani_frame, text = " Show Img / Ani :                    " , style='fg.TLabel')
        self.imgani_label.pack(pady=0, side= tk.LEFT)
        
        filter_wh_str = "No Filter"
        self.filter_wh = tk.StringVar()
        self.filter_wh.set(filter_wh_str)
        self.filter_wh_scroll = tk.OptionMenu(self.wh_frame, self.filter_wh, "No Filter", "Width > Height", "Height > Width")
        self.filter_wh_scroll["highlightthickness"] = 0
        self.filter_wh_scroll.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        filter_imgani_str = "No Filter"
        self.filter_imgani = tk.StringVar()
        self.filter_imgani.set(filter_imgani_str)
        self.filter_imgani_scroll = tk.OptionMenu(self.imgani_frame, self.filter_imgani, "No Filter", "Img Only", "Ani Only")
        self.filter_imgani_scroll["highlightthickness"] = 0
        self.filter_imgani_scroll.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.apply_filter_button = ttk.Button(self.button_frame, text= "Apply", style='my.TButton', width=15, command = self.filter_apply)
        self.apply_filter_button.pack(side =tk.LEFT, padx = 5)
        
        self.cancel_filter_button = ttk.Button(self.button_frame, text= "Cancel", style='my.TButton', width=15, command = self.filter_hide)
        self.cancel_filter_button.pack(side =tk.LEFT, padx = 5)
        
        self.filter_con.attributes('-topmost', False)
        self.filter_con.withdraw()
        
        # Gif Controller Drag
        self.filter_con_offsetx = 0
        self.filter_con_offsety = 0
        self.filter_con.bind('<Button-1>', self.filter_con_predrag)
        self.filter_con.bind('<B1-Motion>', self.filter_con_drag)
        
        self.is_filter_con_created = True
    
    def filter_con_predrag(self, event):
        print("drag_filter_con")    
        logging.info("drag_filter_con")
        
        self.filter_con_offsetx = event.x
        self.filter_con_offsety = event.y
        
    def filter_con_drag(self, event):
        
        x = self.filter_con.winfo_x() + event.x - self.filter_con_offsetx
        y = self.filter_con.winfo_y() + event.y - self.filter_con_offsety
    
        self.filter_con.geometry('+{x}+{y}'.format(x=x,y=y))
        
    def filter_show(self):                          
        print("filter_show")    
        logging.info("filter_show")
        
        listlevel.filter_button.config(text = "Hide", command=self.filter_hide)
        
        self.filter_con.attributes('-topmost', True)
        self.filter_con.deiconify()
        self.filter_con.focus_set()
        
    def filter_hide(self):                            # in windw and fullscreen mode
        print("filter_hide")
        logging.info("filter_hide")
        
        listlevel.filter_button.config(text = "Filter", command=self.filter_show)
        
        self.filter_con.attributes('-topmost', False)
        self.filter_con.withdraw()

    def filter_apply(self):
        print("filter_apply")
        logging.info("filter_apply")
        
        listlevel.rad_button.config(state=tk.DISABLED)
        listlevel.filter_button.config(state=tk.DISABLED)
        
        self.filter_hide()
        
        if window.dataframe_list is None:
            self.dataframe_create()
            
        if window.thread_dataframe_create_filter.is_alive():
            window.thread_dataframe_create_filter.join()
        
        filter_wh_str = self.filter_wh.get()
        filter_imgani_str = self.filter_imgani.get()
        
        if filter_wh_str == "No Filter" and filter_imgani_str == "No Filter":
            window.filter = False
        
        else:
            window.filter = True
        
        self.filter_process(filter_wh_str, filter_imgani_str)
        
        listlevel.rad_button.config(state=tk.NORMAL)
        listlevel.filter_button.config(state=tk.NORMAL)
        
    def filter_process(self, filter_wh_str, filter_imgani_str):
        print("filter_process")
        logging.info("filter_process")
   
        # filter by wh
        df = window.dataframe_list

        filterlist_wh = []
        filterlist_imgani = []
        filterlist_intersection = []
        df_rows = len(df.index)
            
        for i in range(df_rows):
            fil_row = df.loc[[i]]
            # fil_ext = fil_row.iat[0,4]
            # fil_wh = fil_row.iat[0,5]
            fil_row = fil_row.reset_index(drop=True)
            fil_ext = fil_row.at[0,"File_ext"]
            fil_wh = fil_row.at[0,"Pic_WidthHeight"]
            
            if filter_wh_str == "Width > Height":
                if fil_wh == "w>h":
                    # fil_path = fil_row.iat[0,0]
                    fil_path = fil_row.at[0, "Full_Path"]
                    filterlist_wh.append(fil_path)
            
            elif filter_wh_str == "Height > Width":
                if fil_wh == "h>w":
                    # fil_path = fil_row.iat[0,0]
                    fil_path = fil_row.at[0, "Full_Path"]
                    filterlist_wh.append(fil_path)
            
            else:
                # fil_path = fil_row.iat[0,0]
                fil_path = fil_row.at[0, "Full_Path"]
                filterlist_wh.append(fil_path)
            
            if filter_imgani_str == "Img Only":
                if fil_ext == "img":
                    # fil_path = fil_row.iat[0,0]
                    fil_path = fil_row.at[0, "Full_Path"]
                    filterlist_imgani.append(fil_path)
            
            elif filter_imgani_str == "Ani Only":
                if fil_ext == "ani":
                    # fil_path = fil_row.iat[0,0]
                    fil_path = fil_row.at[0, "Full_Path"]
                    filterlist_imgani.append(fil_path)
            
            else:
                # fil_path = fil_row.iat[0,0]
                fil_path = fil_row.at[0, "Full_Path"]
                filterlist_imgani.append(fil_path)
        
        filterlist_intersection =(set(filterlist_wh) & set(filterlist_imgani))  # & reters to intersection 
        filterlist_intersection = sorted(list(filterlist_intersection), key = filterlist_wh.index)    # sorted because it does not follow the order after intersection
        
        # get next available path if current path not in filtered list
        filepath = str(self.folder_entry.get())
        i = 0
        j = 0
        if len(window.fullfilelist) > 0:      # fix the problem when filter returned no result and then go back 
            while len(filterlist_intersection) > 0 and not filepath in filterlist_intersection:
                i = i + 1
                j = j + 1
                if i + window.fileindex == len(window.fullfilelist):
                    i = 0 - window.fileindex
                    
                filepath = window.fullfilelist[window.fileindex + i]
                
                if j > len(df.index):      # to avoid infinite loop
                    print("No next available path")
                    logging.info("No next available path")
                    break
                
            self.folder_entry.delete(0,"end")
            self.folder_entry.insert(1, filepath)             # replace folder entry
        
        # send out list 
        self.filelist_to_go(filterlist_intersection)
        
        # filterfilelist = pd.DataFrame(filterfilelist)
        # save_path = r"C:\Users\simon\Practice\dataframe_list_filter_export.csv"
        # window.dataframe_list_filter.to_csv(save_path, index=False)

# In[Webscraping]
    
    def create_web_mode(self):
        print("create_web_mode")
        logging.info("create_web_mode")
        
        self.web_popup = tk.Toplevel(self.parent)
        self.web_con = tk.Toplevel(self.parent)
        self.web_popup_create()
        self.web_con_create()
        
        self.is_web_created = True

    def enter_web_mode(self, http_path):
        print("enter_web_mode")
        logging.info("enter_web_mode")
        
        if not self.is_web_created:       # for first entry of web mode
            self.is_web_mode = False
            self.create_web_mode()
        
        self.reset_entry()
        
        self.is_web_mode = True
        self.popup_show = False
        self.apply_to_all = True
        self.downloaded_page = 0
        self.downloaded_page_list = []
        self.pause_download = False
        self.next_chapter_path = None
        self.skip_download = False
        self.web_fileindex = 0
        
        self.skip_chapter_button.config(state=tk.DISABLED)
        
        self.web_con_show()
        
        if http_path.find("exhentai.org") >= 0 or http_path.find("e-hentai.org") >= 0:
            self.web = "exhentai"    
            savefilepath = self.enter_exhentai_webscraping(http_path)
            return savefilepath
        
        elif http_path.find("hbmanga.com") >= 0:
            self.web = "baozimh"
            savefilepath = self.enter_baozimh_webscraping(http_path)
            return savefilepath
        
        elif http_path.find("cc.fun8.us") >= 0:
            self.web = "cartoonmad"
            savefilepath = self.enter_cartoonmad_webscraping(http_path)
            return savefilepath

    def quit_web_mode(self):
        print("quit_web_mode")
        logging.info("quit_web_mode")
        
        self.is_web_mode = False
        self.webcon_listbox.insert(0, "*** Quitting Web Mode ***")
        window.after(3000, self.web_con_hide)
        
        if len(window.fullfilelist) > 0:
            window.dataframe_create()
        
        if window.is_manga_mode:
            fulllevel.manga.thread_storage = threading.Thread(target = fulllevel.manga.backend_storage, args = (window.fileindex,))
            
            fulllevel.manga.stop_backend = False
            fulllevel.manga.thread_storage.start() 
            
    def web_con_create(self):
        print("web_con_create")
        logging.info("web_con_create")
        
        # Controller in web mode
        
        self.web_con.resizable(False,False)
        self.web_con.overrideredirect(1)
        self.web_con.geometry("300x270+%d+%d" % (int(settinglevel.webcon_x), int(settinglevel.webcon_y)))
        
        self.webcon1_frame = ttk.Frame(self.web_con, style='Warning.TFrame')           
        self.webcon1_frame.pack(pady=5, fill="y", side = tk.TOP)  
        
        self.webcon2_frame = ttk.Frame(self.web_con, style='Warning.TFrame')           
        self.webcon2_frame.pack(pady=5, fill="y", side = tk.TOP)  
        
        self.webcon3_frame = ttk.Frame(self.web_con, style='Warning.TFrame')           
        self.webcon3_frame.pack(pady=5, fill="y", side = tk.TOP)  
        
        self.webcon_scroll = ttk.Scrollbar(self.webcon1_frame, orient='vertical', style="Vertical.TScrollbar") 
        self.webcon_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.webcon_listbox = tk.Listbox(self.webcon1_frame, width = 38, height = 10, highlightthickness=2, font = ("Arial", 10), selectmode = tk.SINGLE, yscrollcommand = self.webcon_scroll.set)
        self.webcon_listbox.configure(background='black')
        self.webcon_listbox.pack(side=tk.LEFT)
        
        self.webcon_scroll.config(command = self.webcon_listbox.yview)
        
        self.pause_resume_button = ttk.Button(self.webcon2_frame, text= "Pause Download", width=15, command = self.web_pause_download)
        self.pause_resume_button.pack(side =tk.LEFT, padx = 5)

        self.download_all_button = ttk.Button(self.webcon2_frame, text= "Download All", width=15, command = self.download_all)
        self.download_all_button.pack(side =tk.LEFT, padx = 5)
        
        self.skip_chapter_button = ttk.Button(self.webcon3_frame, text= "Next Chapter", width=15, command = self.skip_chapter)
        self.skip_chapter_button.pack(side =tk.LEFT, padx = 5)
        
        self.web_con_hide()
        
        # Gif Controller Drag
        self.web_con_offsetx = 0
        self.web_con_offsety = 0
        self.webcon_listbox.bind('<Button-1>', self.web_con_predrag)
        self.webcon_listbox.bind('<B1-Motion>', self.web_con_drag)
        
    def web_con_predrag(self, event):
        print("web_con_predrag")    
        logging.info("web_con_predrag")
        
        self.web_con_offsetx = event.x
        self.web_con_offsety = event.y
        
    def web_con_drag(self, event):
        
        x = self.web_con.winfo_x() + event.x - self.web_con_offsetx
        y = self.web_con.winfo_y() + event.y - self.web_con_offsety
    
        self.web_con.geometry('+{x}+{y}'.format(x=x,y=y))
        
    def web_con_show(self):                          
        print("web_con_show")    
        logging.info("web_con_show")
         
        self.download_all_button.config(state=tk.NORMAL)
        self.pause_resume_button.config(text= "Pause Download", command = self.web_pause_download)
        self.web_con.attributes('-topmost', True)
        self.web_con.deiconify()
        self.web_con.focus_set()
        
    def web_con_hide(self):                            
        print("web_con_hide")
        logging.info("web_con_hide")
        
        if not self.is_web_mode:
            self.web_con.attributes('-topmost', False)
            self.web_con.withdraw()
        
    def download_all(self):
        
        self.download_all_button.config(state=tk.DISABLED)
        self.webcon_listbox.insert(0, "Will download remaining files")
        
        while window.thread_batch_download.is_alive() and window.is_web_mode:
            window.update()
            time.sleep(0.01)

        print("start downloading all remaining files")
        logging.info("start downloading all remaining files")
        self.webcon_listbox.insert(0, "start downloading all remaining files")
        
        window.thread_batch_download = threading.Thread(target = window.batch_download, args = (self.next_path, self.url_cookies, self.web_output_folder, self.fileindex, self.total_page))
        window.thread_batch_download.start()
    
    def web_pause_download(self):
        print("web_pause_download")
        logging.info("web_pause_download")
        
        self.pause_download = True
        self.webcon_listbox.insert(0, "Download Paused")
        
        self.pause_resume_button.config(text= "Resume Download", command = self.web_resume_download)
    
    def web_resume_download(self):
        print("web_resume_download")
        logging.info("web_resume_download")
        
        self.pause_download = False
        self.webcon_listbox.insert(0, "Download Resumed")
        
        self.pause_resume_button.config(text= "Pause Download", command = self.web_pause_download)
    
    def web_popup_create(self):
        print("web_popup_create")
        logging.info("web_popup_create")
        
        # Popup in web mode

        self.web_popup.resizable(False,False)
        self.web_popup.overrideredirect(1)
        self.web_popup.geometry("300x115+%d+%d" % (int(settinglevel.webpopup_x), int(settinglevel.webpopup_y)))
        
        self.web1_frame = ttk.Frame(self.web_popup, style='Warning.TFrame')           
        self.web1_frame.pack(pady=10, fill="y", side = tk.TOP)  
        
        self.web2_frame = ttk.Frame(self.web_popup, style='Warning.TFrame')           
        self.web2_frame.pack(pady=10, fill="y", side = tk.TOP)  
        
        self.web3_frame = ttk.Frame(self.web_popup, style='Warning.TFrame')           
        self.web3_frame.pack(pady=0, fill="y", side = tk.BOTTOM)  
        
        self.web1_label = ttk.Label(self.web1_frame, text = "Replace Existing File?             " , style='fg.TLabel')
        self.web1_label.pack(pady=0, side= tk.LEFT)
        
        self.replace_button = ttk.Button(self.web2_frame, text= "Replace", width=10, command = self.web_replace_button)
        self.replace_button.pack(side =tk.LEFT, padx = 5)

        self.replaceno_button = ttk.Button(self.web2_frame, text= "No Replace", width=10, command = self.web_replaceno_button)
        self.replaceno_button.pack(side =tk.LEFT, padx = 5)
        
        self.applyall_check = tk.BooleanVar()
        self.apply_to_all = True
        self.applyall_check.set(True)   
        
        self.applyall_button = ttk.Checkbutton(self.web3_frame, text="Apply to all?     ", var=self.applyall_check, style = "warning.Roundtoggle.Toolbutton")
        self.applyall_button.pack(pady=0, padx = 0, side= tk.LEFT)
        
        self.web_popup.attributes('-topmost', False)
        self.web_popup.withdraw()
        
        # Gif Controller Drag
        self.web_popup_offsetx = 0
        self.web_popup_offsety = 0
        self.web1_label.bind('<Button-1>', self.web_popup_predrag)
        self.web1_label.bind('<B1-Motion>', self.web_popup_drag)
    
    def web_popup_predrag(self, event):
        print("drag_web_popup")    
        logging.info("drag_web_popup")
        
        self.web_popup_offsetx = event.x
        self.web_popup_offsety = event.y
        
    def web_popup_drag(self, event):
        
        x = self.web_popup.winfo_x() + event.x - self.web_popup_offsetx
        y = self.web_popup.winfo_y() + event.y - self.web_popup_offsety
    
        self.web_popup.geometry('+{x}+{y}'.format(x=x,y=y))
    
    def web_replace_button(self):
        self.replace = True
        self.apply_to_all = self.applyall_check.get()

        self.web_popup_hide()
        
    def web_replaceno_button(self):
        self.replace = False
        self.apply_to_all = self.applyall_check.get()
            
        self.web_popup_hide()
    
    def web_popup_show(self, file_name):                          
        print("web_popup_show")    
        logging.info("web_popup_show")
        
        self.popup_show = True
        
        self.web1_label.config(text = " Replace Existing File %s?        "%(file_name))
        
        self.web_popup.attributes('-topmost', True)
        self.web_popup.deiconify()
        self.web_popup.focus_set()
        
    def web_popup_hide(self):                            # in windw and fullscreen mode
        print("web_popup_hide")
        logging.info("web_popup_hide")
        
        self.web_popup.attributes('-topmost', False)
        self.web_popup.withdraw()
        
        self.popup_show = False
    
    def get_html(self, input_url, url_cookies):
        # print("get_html")
        # logging.info("get_html")
        
        # add headers to pretend to be browser
        url_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/" "537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
        
        url_requests = requests.get(input_url, headers=url_headers,cookies=self.url_cookies)  #get with cookies
        
        if self.web == "cartoonmad":      
            url_requests.encoding = "big5"    # follow charset in the html_text 
        
        html_text = url_requests.text                      # html text
        # print(html_text)
        # self.write_print(html_text)
        
        return html_text
    
    def write_print(self, html_text):
        print("write_print")
        logging.info("write_print")
    
        output_path = os.path.join(to_dir,"exhentai.txt")
        output_file = open(output_path, "w", encoding ="utf-8")   # create txt
        output_file.flush()
    
        output_file.write(html_text)
        output_file.flush()
        output_file.close()

    def batch_download(self, next_path, url_cookies, to_dir, from_page, download_pages):
        
        def batch_download_exhentai(html_text):
            
            # Get the path of img
            bs = BeautifulSoup(html_text, "lxml")   
        
            imgs = bs.find_all('img', id="img")
            for img in imgs:
                # print(img)
                img_path = img["src"]
                # print(img_path)

            # Find next path
            paths = bs.find_all("a", id="next")
            
            next_path = paths[0]["href"]
            # print(next_path)
            file_ext = os.path.splitext(img_path)[1].lower()
            file_name = str(i).rjust(4, "0") + file_ext
            
            return img_path, file_name, file_ext, next_path
        
        def batch_download_baozimh(page_no):
            
            if page_no == len(self.baozimh_img_list):
                next_path = None
                # find out next chapter
            
            else:
                next_path = self.baozimh_img_list[page_no]
            
            img_path = self.baozimh_img_list[page_no - 1]
            
            file_ext = os.path.splitext(img_path)[1].lower()
            file_name = str(i).rjust(4, "0") + file_ext
            
            return img_path, file_name, file_ext, next_path
        
        def batch_download_cartoonmad(html_text, http_path):
            
            # Get the path of img
            bs = BeautifulSoup(html_text, "lxml")  
            
            imgs = bs.find_all('img')
            for img in imgs:
                # print(img)
                img_path = img["src"]
                
                if "cc.fun8.us" in img_path:
                    break
            
            img_path = "https:" + img_path

            # Find next path
            find_a = bs.find_all("a", class_="pages")
            
            for result in find_a:
                # print(result.text)
                if "下一頁" in result.text:
                    next_path = result["href"]
                    next_path = os.path.split(http_path)[0] + "/" + next_path
                    # print(next_path)
                    break
                
            file_ext = os.path.splitext(img_path)[1].lower()
            file_name = str(i).rjust(4, "0") + file_ext
            
            return img_path, file_name, file_ext, next_path
        
        # batch download
        to_page = from_page + download_pages
        
        batch_download_str = "batch_download - from %i to %i" %(from_page + 1, min(to_page, self.total_page))
        print(batch_download_str)
        logging.info(batch_download_str)
        self.webcon_listbox.insert(0, batch_download_str)
        
        timer = time.perf_counter()
        
        for i in range(from_page, to_page):
            # print(i)
            if self.downloaded_page == self.total_page:
                break
            
            if self.downloaded_page_list[i] == "Downloaded":
                i = i + 1
                continue
            
            while self.pause_download:
                time.sleep(0.1)    
                
                if not self.is_web_mode:
                    break
                
                if self.skip_download:
                    break
                
            if not self.is_web_mode:
                break

            if self.skip_download:
                print("break")
                break
            
            i = i + 1

            if self.web == "exhentai":
                html_text = self.get_html(next_path, self.url_cookies)
                img_path, file_name, file_ext, next_path = batch_download_exhentai(html_text)
            
            elif self.web == "baozimh":
                # img_path = next_path
                img_path, file_name, file_ext, next_path = batch_download_baozimh(i)
                
            elif self.web == "cartoonmad":
                html_text = self.get_html(next_path, self.url_cookies)
                img_path, file_name, file_ext, next_path = batch_download_cartoonmad(html_text, next_path)
                
            # Save img files            
            download_file_path = os.path.join(to_dir, file_name)

            if os.path.isfile(download_file_path):
                
                if not self.apply_to_all:
                    self.replace = False
                    self.web_popup_show(file_name)
    
                    while self.popup_show:
                        window.update()
                        time.sleep(0.1)
                    
                if self.replace:
                    img_data = requests.get(img_path).content
                    with open(download_file_path, 'wb') as handler:
                        handler.write(img_data)
    
                    time_spent = round(time.perf_counter()-timer,3)
                    
                    print("Downloaded - %i" %i)
                    print("Time spent : %f" %time_spent)
                    logging.info("Downloaded - %i" %i)
                    logging.info("Time spent : %f" %time_spent)
                    self.webcon_listbox.insert(0, "Downloaded - %i / %i" %(i, self.total_page))
                    self.webcon_listbox.insert(0, "Time spent : %.2f s" %time_spent)
            
            else:
                img_data = requests.get(img_path).content
                with open(download_file_path, 'wb') as handler:
                    handler.write(img_data)
                    
                time_spent = round(time.perf_counter()-timer,3)
                
                print("Downloaded - %i" %i)
                print("Time spent : %f" %time_spent)
                logging.info("Downloaded - %i" %i)
                logging.info("Time spent : %f" %time_spent)
                self.webcon_listbox.insert(0, "Downloaded - %i / %i" %(i, self.total_page))
                self.webcon_listbox.insert(0, "Time spent : %.2f s" %time_spent)
            
            # Modify FullFileList if file_ext is not .jpg
            if file_ext != ".jpg":
                window.fullfilelist[i - 1] = download_file_path
                listlevel.listbox1.delete(i - 1)
                listlevel.listbox1.insert(i - 1, file_name)
            
            self.downloaded_page_list[i - 1] = "Downloaded"
            
            self.downloaded_page = self.downloaded_page + 1
            # print(self.downloaded_page)
            self.next_path = next_path
        
        if self.skip_download:
            print("skipped this batch of download")
            logging.info("skipped this batch of download")
            self.webcon_listbox.insert(0, "This chapter skipped")            
            
        else:
            print("completed this batch of download")
            logging.info("completed this batch of download")
            self.webcon_listbox.insert(0, "This batch completed")
        
        if self.downloaded_page == self.total_page or self.skip_download:
            
            if self.next_chapter_path != None:       # go next chapter
                if self.web == "baozimh":
                    # window.after(10, self.baozimh_next_chapter)
                    window.thread_baozimh_next_chapter = threading.Thread(target = window.baozimh_next_chapter)
                    window.thread_baozimh_next_chapter.start()
                    
                elif self.web == "cartoonmad":
                    # window.after(10, self.cartoonmad_next_chapter)
                    window.thread_cartoonmad_next_chapter = threading.Thread(target = window.cartoonmad_next_chapter)
                    window.thread_cartoonmad_next_chapter.start()
                    
            else:                                    # end web mode
                print("completed all download")
                logging.info("completed all download")
                self.webcon_listbox.insert(0, "All batch completed")
                
                self.quit_web_mode()
   
    def skip_chapter(self):
        print("skip_chapter")
        logging.info("skip_chapter")
        
        self.skip_download = True
        
        if window.thread_batch_download.is_alive():
            while window.thread_batch_download.is_alive():
                window.update()
                time.sleep(0.1)
            
        else:
            print("skipped this batch of download")
            logging.info("skipped this batch of download")
            self.webcon_listbox.insert(0, "This chapter skipped")    
            
            if self.web == "baozimh":
                window.thread_baozimh_next_chapter = threading.Thread(target = window.baozimh_next_chapter)
                window.thread_baozimh_next_chapter.start()
                
            elif self.web == "cartoonmad":
                window.thread_cartoonmad_next_chapter = threading.Thread(target = window.cartoonmad_next_chapter)
                window.thread_cartoonmad_next_chapter.start()
        
        self.skip_download = False
   
# Exhentai
    def enter_exhentai_webscraping(self, http_path):
        
        def get_page_info(html_text):
            print("get_page_info")
            logging.info("get_page_info")
            
            bs = BeautifulSoup(html_text, "lxml")   
            
            # get title
            title = bs.find_all("title")[0].get_text()
            title = title[:-15]    # exclude the ExHentai.org tag
            # print(title)
            
            # get total number of pages
            total_page = bs.find_all("td", class_="gdt2")
            total_page = total_page[-2]
            total_page = total_page.get_text()      # get value inside tag
            total_page = int(total_page[:total_page.find("pages")])
            # print(total_page)
            
            return title, total_page
            
        def get_first_page(html_text, http_path):
            print("get_first_page")
            logging.info("get_first_page")
            
            bs = BeautifulSoup(html_text, "lxml")   
            first_page = bs.find_all("a")
        
            # print(first_page)
            exh_id = os.path.split(os.path.split(http_path[:-1])[0])[1]
            first_page_id = exh_id + "-1"
            for page in first_page:
                try:
                    page_href = page["href"]
                    
                except:
                    page_href = ""
                
                if page_href.find(first_page_id) >= 0:
                    first_page = page_href
                    break
                
            # print(first_page)
            return first_page
        
        # enter_exhentai_webscraping
        print("enter_exhentai_webscraping")
        logging.info("enter_exhentai_webscraping")
        
        self.url_cookies = {"igneous":"qnzyvr5kb88ipg1aq0e", "sk":"ngk0ktce7hft83dem4njd9tzyt6y", "arp_scroll_position":"0", "ipb_pass_hash":"a9a5869db2c244a2294a38aeafa65178", "ipb_member_id":"528230"}

        html_text = self.get_html(http_path, self.url_cookies)
        title, self.total_page = get_page_info(html_text)
        
        self.downloaded_page_list = [None] * self.total_page
        
        if len(window.fullfilelist) == 0:
            window.fullfilelist = [None] * self.total_page
        
        if len(title) > 150:    
            title = title[:150]                     # limit title to be 150 char
            
        prohibited_symbols = "\/:*?\"<>|?*"     
        for symbol in prohibited_symbols:
            title = title.replace(symbol, "")    # replace symbols
        
        while title[-1] == " ":
            title = title[:-1]                # fix filenotfounderror because folder name can't have space at last char
        
        print("Downloading: %s" %title)
        logging.info("Downloading: %s" %title)
        self.webcon_listbox.insert(0, "Downloading: %s" %title)   
        
        exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
        self.web_output_folder = exe_dir + "\Downloads\\" + title
        
        if not os.path.isdir(self.web_output_folder):
            os.makedirs(self.web_output_folder)
            
        # Generate file list
        savefilepath = []

        i = 0
        for i in range(self.total_page):
            i = i + 1
            temp_file_name = str(i).rjust(4, "0") + ".jpg"     # create temp file name
            file_path = os.path.join(self.web_output_folder, temp_file_name)
            savefilepath.append(file_path)
            
        first_page = get_first_page(html_text, http_path)
        
        # Get first page
        self.batch_download(first_page, self.url_cookies, self.web_output_folder, 0, 1)
        
        if window.fullfilelist[0] != None:   # fix the issue when 1st pic is not jpg
            first_ext = os.path.splitext(window.fullfilelist[0])[1]  
            if first_ext != ".jpg":      
                savefilepath[0] = window.fullfilelist[0]
        
        return savefilepath

# Baozimh
    def enter_baozimh_webscraping(self, front_path):
        
        def get_page_info(html_text):
            
            bs = BeautifulSoup(html_text, "lxml")   
            
            # get title
            title = bs.find_all("title")[0].get_text()
            title = title[:-7]    # exclude the baozhi tag
            title_separater = title.find(" - ")
            # print(title)
            # print(title_separater)
            
            title_no = title[:title_separater]
            title_name = title[title_separater + 3:]
            
            title = title_name + "_" + title_no
            
            # get img list
            img_list = []
            imgs = bs.find_all('amp-img')
            for img in imgs:
                # print(img)
                img_path = img["src"]
                if "baozicdn.com" in img_path:
                    img_list.append(img_path)
            # print(total_page)
            # print(img_list)
            total_page = ""
            
            # check whether it is last chapter
            next_chapter = bs.find_all("div", class_="next_chapter")
            next_chapter = next_chapter[0].get_text()
            
            if "這是本作品最後一話了" in next_chapter:
                next_chapter_path = None
            
            else:
                page_name = os.path.split(front_path)[1]
                page_name_nohtml = os.path.splitext(page_name)[0]
                page_no = page_name_nohtml[2:]
                next_page_no = str(int(page_no) + 1)
                next_chapter_path = os.path.split(front_path)[0] + "/0_" + next_page_no + ".html"
            
            # print(next_chapter_path)
            
            return title, img_list, next_chapter_path
        
        # enter_baozimh_webscraping
        print("enter_baozimh_webscraping")
        logging.info("enter_baozimh_webscraping")
        
        self.url_cookies = {"cdn_domain":"-mha1-nlams.baozicdn.com", "tuid":"Sxz2dl5Dp6bypfEafyGVoigtCMBD88Xz"}
        html_text = self.get_html(front_path, self.url_cookies)
        title, self.baozimh_img_list, self.next_chapter_path = get_page_info(html_text)

        print("Downloading: %s" %title)
        logging.info("Downloading: %s" %title)
        self.webcon_listbox.insert(0, "Downloading: %s" %title)   
        
        # print(self.baozimh_img_list)
        self.total_page = len(self.baozimh_img_list)
        
        if self.next_chapter_path == None:
            self.skip_chapter_button.config(state=tk.DISABLED)
        
        else:
            self.skip_chapter_button.config(state=tk.NORMAL)
        
        self.downloaded_page_list = [None] * self.total_page
        
        if len(window.fullfilelist) == 0:
            window.fullfilelist = [None] * self.total_page
        
        if len(title) > 150:    
            title = title[:150]                     # limit title to be 150 char
            
        prohibited_symbols = "\/:*?\"<>|?*"     
        for symbol in prohibited_symbols:
            title = title.replace(symbol, "")    # replace symbols
        
        exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
        self.web_output_folder = exe_dir + "\Downloads\\" + title
        
        if not os.path.isdir(self.web_output_folder):
            os.makedirs(self.web_output_folder)
            
        # Generate file list
        savefilepath = []

        i = 0
        for i in range(self.total_page):
            i = i + 1
            temp_file_name = str(i).rjust(4, "0") + ".jpg"     # create temp file name
            file_path = os.path.join(self.web_output_folder, temp_file_name)
            savefilepath.append(file_path)

        first_page = front_path
        
        self.batch_download(first_page, self.url_cookies, self.web_output_folder, 0, 1)
        
        if window.fullfilelist[0] != None:   # fix the issue when 1st pic is not jpg
            first_ext = os.path.splitext(window.fullfilelist[0])[1]  
            if first_ext != ".jpg":      
                savefilepath[0] = window.fullfilelist[0]
    
        return savefilepath
    
    def baozimh_next_chapter(self):
        print("baozimh_next_chapter")
        logging.info("baozimh_next_chapter")
        
        self.downloaded_page = 0
        
        savefilepath = self.enter_baozimh_webscraping(self.next_chapter_path)
        self.append_filelist(savefilepath)
        # print(window.fullfilelist)
        
        batch_download_page = max(1, min(20, self.total_page - 2))   # avoid loop continuing because next chapter is less than 20 pages
        
        window.thread_batch_download = threading.Thread(target = window.batch_download, args = (None, self.url_cookies, self.web_output_folder, 1, batch_download_page))
        window.thread_batch_download.start()
        
# Cartoonmad
    def enter_cartoonmad_webscraping(self, http_path):
        
        def get_page_info(html_text, http_path):
            print("get_page_info")
            logging.info("get_page_info")
            
            bs = BeautifulSoup(html_text, "lxml")   
            
            # get title
            title = bs.find_all("title")[0].get_text()
        
            title_no = os.path.split(http_path)[1]
            title_no = title_no[0:4]
            
            title = title_no + "_" + title
            # print(title)
            
            imgs = bs.find_all('img')
            for img in imgs:
                # print(img)
                img_path = img["src"]  
                
                # get total_page
                if "cc.fun8.us" in img_path:
                    
                    find_a = bs.find_all("a")
        
                    for a_elements in find_a:
                        try:
                            total_page = int(a_elements.get_text())
        
                        except:
                            pass
                    
                    # print(total_page)
                    break
            
            find_a = bs.find_all("a", class_="pages")
            
            # get next_chapter_path
            for result in find_a:
                # print(result.text)
                if "下一話" in result.text:
                    next_chapter_path = result["href"]
                    next_chapter_path = os.path.split(http_path)[0] + "/" + next_chapter_path
                    # print(next_chapter_path)
            
            next_chapter_html_text = self.get_html(next_chapter_path, self.url_cookies)
            
            if "An error occurred on the server when processing the URL" in next_chapter_html_text:
                print("This is the last chapter")
                next_chapter_path = None
            
            return title, total_page, next_chapter_path
        
        # enter_cartoonmad_webscraping
        print("enter_cartoonmad_webscraping")
        logging.info("enter_cartoonmad_webscraping")
        
        self.url_cookies = {"ASPSESSIONIDAGRCDCQT":"JCDLNBGBNKIHIFCNGGMJFNAC", "ASPSESSIONIDQUQTBQRA":"AEELIGDCPEDKNAPPIBJHLOJF", "ASPSESSIONIDSURRARRA":"KCFOLFJAALFOEENKOMJDLNGB", "ASPSESSIONIDSWTQBQRB": "LPJLOBADDFJMPGIGJEPFEIKP", "arp_scroll_position": "0"}

        html_text = self.get_html(http_path, self.url_cookies)
        title, self.total_page, self.next_chapter_path = get_page_info(html_text, http_path)

        if self.next_chapter_path == None:
            self.skip_chapter_button.config(state=tk.DISABLED)
        
        else:
            self.skip_chapter_button.config(state=tk.NORMAL)
            
        self.downloaded_page_list = [None] * self.total_page
        
        if len(window.fullfilelist) == 0:
            window.fullfilelist = [None] * self.total_page
        
        if len(title) > 150:    
            title = title[:150]                     # limit title to be 150 char
            
        prohibited_symbols = "\/:*?\"<>|?*"     
        for symbol in prohibited_symbols:
            title = title.replace(symbol, "")    # replace symbols
        
        print("Downloading: %s" %title)
        logging.info("Downloading: %s" %title)
        self.webcon_listbox.insert(0, "Downloading: %s" %title)   
        
        exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
        self.web_output_folder = exe_dir + "\Downloads\\" + title
        
        if not os.path.isdir(self.web_output_folder):
            os.makedirs(self.web_output_folder)
            
        # Generate file list
        savefilepath = []

        i = 0
        for i in range(self.total_page):
            i = i + 1
            temp_file_name = str(i).rjust(4, "0") + ".jpg"     # create temp file name
            file_path = os.path.join(self.web_output_folder, temp_file_name)
            savefilepath.append(file_path)
        
        # Get first page
        self.batch_download(http_path, self.url_cookies, self.web_output_folder, 0, 1)
        
        if window.fullfilelist[0] != None:   # fix the issue when 1st pic is not jpg
            first_ext = os.path.splitext(window.fullfilelist[0])[1]  
            if first_ext != ".jpg":      
                savefilepath[0] = window.fullfilelist[0]
        
        return savefilepath

    def cartoonmad_next_chapter(self):
        print("cartoonmad_next_chapter")
        logging.info("cartoonmad_next_chapter")
        
        self.downloaded_page = 0
        
        savefilepath = self.enter_cartoonmad_webscraping(self.next_chapter_path)
        self.append_filelist(savefilepath)
        # print(window.fullfilelist)
        
        batch_download_page = max(1, min(20, self.total_page - 2))   # avoid loop continuing because next chapter is less than 20 pages
        
        window.thread_batch_download = threading.Thread(target = window.batch_download, args = (self.next_path, self.url_cookies, self.web_output_folder, 1, batch_download_page))
        window.thread_batch_download.start()
        
# In[Quit Button]
    
    def quit(self):
        print("quit")
        logging.info("quit")
        
        self.is_stop_ani = True
        
        try:
            settinglevel.setting_create()              # run and save settings
            settinglevel.setting_ok()                # settings toplevel destroyed
        
        except:
            print("Not saved when quit: Settings Error")
            logging.info("Not saved when quit: Settings Error")
        
        settinglevel.parent.destroy()
        listlevel.list_canva.destroy()
        listlevel.parent.destroy()

        try:
            fulllevel.popup.destroy()
            fulllevel.full_con.destroy()
            fulllevel.photo_con.destroy()
            fulllevel.manga_con.destroy()
            
        except:
            pass

        try:
            window.stor.stop_storage(True)
            window.stor.stop_backend = True
            
            fulllevel.stor.stop_storage(True)
            fulllevel.stor.stop_backend = True
            
            fulllevel.photoalbum.stop_storage(True)
            fulllevel.photoalbum.stop_backend = True
            
            fulllevel.manga.stop_storage(True)
            fulllevel.manga.stop_backend = True
        
        except:
            pass
        
        try:
            del window.fullfilelist
            del window.stor.ListStor
            del window.stor.ListPhotoStor
            
        except:
            pass
        
        try:
            del fulllevel.stor.ListStor
            del fulllevel.stor.ListPhotoStor
        
        except:
            pass
        
        try:
            del fulllevel.photoalbum.ListStor
        
        except:
            pass
        
        try:
            del fulllevel.manga.ListStor
            
        except:
            pass
        
        try:
            window.after_cancel(window.thread_resize)     # it can only cancel one resize thread
            
        except:
            pass
        
        try:
            window.after_cancel(window.thread_hidecursor2)     # it can only cancel one thread
            
        except:
            pass
        
        window.gif_con.destroy()
        window.parent.destroy()                     # trigger window.mainloop() to end, but it is not necessary to be put at the end
        
# In[Forward Button]
    
    def forward(self, slide_forward = False, event=None):                                  # all modes except manga mode

        self.is_stop_ani = True                             # stop previous ani
        self.zoom_factor = 1                             # reset zoom
        is_cached = False
        is_fullcached = False
        is_photocached = False
        is_vid = False
        self.is_gif_pause = False
        self.rotate_degree = 0
        STORAGE_TRIGGER = 20
        DOWNLOAD_TRIGGER = 10
        
        # get fileindex
        pre_fileindex = self.fileindex
        prefile_name = os.path.split(self.fullfilelist[pre_fileindex])[1]
        self.fileindex = self.fileindex + 1                    # next file
    
        if self.fileindex == len(self.fullfilelist):           # back to start
            self.fileindex = 0
        
        print("forward - %i" %self.fileindex)
        logging.info("forward - %i" %self.fileindex)
        
        try:
            nextpath = self.fullfilelist[self.fileindex]          # get path of next file
        
        except IndexError:
            exception_emptypath()
            
        if window.is_web_mode:
            pre_web_fileindex = self.web_fileindex
            nextpath_folder = os.path.split(nextpath)[0]
            
            if nextpath_folder == self.web_output_folder:
                self.web_fileindex = self.web_fileindex + 1
            
            else:
                self.web_fileindex = 0
            # print(self.web_fileindex)
            
            if not os.path.isfile(nextpath):
                print("FileNotFoundError")
                
                self.fileindex = pre_fileindex         # show original pic if FileNotFound
                self.web_fileindex = pre_web_fileindex
                nextpath = self.fullfilelist[self.fileindex]
            
            if self.downloaded_page - self.web_fileindex <= DOWNLOAD_TRIGGER and self.web_fileindex != 0:
                if not window.thread_batch_download.is_alive():
                    window.thread_batch_download = threading.Thread(target = window.batch_download, args = (self.next_path, self.url_cookies, self.web_output_folder, self.web_fileindex, 20))
                    window.thread_batch_download.start()
        
        self.cancel_move()    
        self.folder_entry.delete(0,"end")
        self.folder_entry.insert(1, nextpath)             # replace folder entry
        
        listlevel.listbox1.delete(pre_fileindex)
        listlevel.listbox1.insert(pre_fileindex, prefile_name)
        
        file_name = os.path.split(nextpath)[1]
        listlevel.listbox1.delete(self.fileindex)
        listlevel.listbox1.insert(self.fileindex, u"\u25B6 " + file_name)
        listlevel.listbox1.see(self.fileindex)
        listlevel.listbox2.see(self.fileindex)
        listlevel.listbox3.see(self.fileindex)
        listlevel.listbox4.see(self.fileindex)
        listlevel.listbox5.see(self.fileindex)
        
        # check ext and assign def_ accordingly
        file_ext = os.path.splitext(nextpath)[1].lower()
        if file_ext in self.supported_img:                # img
            
        # check cache
            if self.stor.ListStor[self.fileindex] is not None:
                is_cached = True
            
            if fulllevel.stor.ListStor[self.fileindex] is not None:
                is_fullcached = True  
            
            try:    # when not yet entered photoalbum mode
                if fulllevel.photoalbum.ListStor[self.fileindex] is not None:
                    is_photocached = True  
            
            except:
                pass
                # print("failed to modify photoalbum cache")
                # logging.info("failed to modify photoalbum cache")
            
            # image enhance for next image
            if settinglevel.is_enhanceall:
                self.next_enhance = True
            
            else:
                self.next_enhance = False
                settinglevel.enhancecurrent_check.set(False)   
            
            if self.is_full_mode:
                
                if self.is_photoalbum_mode:
                    # check if thread should run
                    if fulllevel.photoalbum.last_index is not None and fulllevel.photoalbum.backend_run == False:
                        if abs(fulllevel.photoalbum.last_index - self.fileindex) <= STORAGE_TRIGGER or fulllevel.photoalbum.last_index - window.fileindex + len(window.fullfilelist) <= STORAGE_TRIGGER:
                            
                            fulllevel.photoalbum.pause_backend = False
                            
                            print("start photoalbum thread")
                            logging.info("start photoalbum thread")
                            fulllevel.photoalbum.thread_storage = threading.Thread(target = fulllevel.photoalbum.backend_storage, args = (window.fileindex,))
                            
                            fulllevel.photoalbum.stop_backend = False
                            fulllevel.photoalbum.thread_storage.start()
                    
                    self.ShowIMG_FullPhotoalbum(nextpath, True, is_photocached)  # Photo Album mode
                    
                    if fulllevel.photo_preview_visible:
                        window.ShowIMG_Preview(nextpath, False, False)
                        
                    window.after(20, self.ShowIMG_FullPhotoalbum, nextpath, False, is_photocached)  # # slight delay for next slide to fix crash issue of photo album mode
                
                else:   
                    # check if thread should run
                    if fulllevel.stor.last_index is not None and fulllevel.stor.backend_run == False:
                        if abs(fulllevel.stor.last_index - self.fileindex) <= STORAGE_TRIGGER or fulllevel.stor.last_index - window.fileindex + len(window.fullfilelist) <= STORAGE_TRIGGER:
                            
                            fulllevel.stor.pause_backend = False
                            
                            print("start fulllevel thread")
                            logging.info("start fulllevel thread")
                            fulllevel.stor.thread_storage = threading.Thread(target = fulllevel.stor.backend_storage, args = (window.fileindex,))
                            
                            fulllevel.stor.stop_backend = False
                            fulllevel.stor.thread_storage.start()
                            
                    if window.stor.backend_run_photoimage == False and window.check_photoimage(window.fileindex):
                        print("start fulllevel thread (PhotoImage)")
                        logging.info("start fulllevel thread (PhotoImage)")
                        fulllevel.stor.thread_storage_photoimage = threading.Thread(target = fulllevel.stor.backend_photoimage_storage, args = (window.fileindex,))
                        fulllevel.stor.thread_storage_photoimage.start()
                        
                    if window.is_slide_check:                                # slide mode
                        is_vid = False
                        self.ShowIMG_Full(nextpath, is_fullcached, is_vid, slide_forward)           # to resolve the blink issue in slide mode
                        
                        if window.is_slide_check:                                            # to avoid start slide again after quit slide
                            window.after(20, fulllevel.start_slide, is_fullcached, True)                # slight delay for next slide to fix crash issue of slide mode
                        
                    else:
                        self.ShowIMG_Full(nextpath, is_fullcached)            # simple fullscreen
                    
            else:
                self.ShowIMG(nextpath, is_cached)                    # window mode
                
                if window.stor.last_index is not None and window.stor.backend_run == False:
                    if abs(window.stor.last_index - self.fileindex) <= STORAGE_TRIGGER or window.stor.last_index - window.fileindex + len(window.fullfilelist) <= STORAGE_TRIGGER:
                        
                        window.stor.pause_backend = False
                        
                        print("start window thread")
                        logging.info("start window thread")
                        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
                        
                        window.stor.stop_backend = False
                        window.stor.thread_storage.start()
                        
                if window.stor.backend_run_photoimage == False and window.check_photoimage(window.fileindex):
                    print("start window thread (PhotoImage)")
                    logging.info("start window thread (PhotoImage")
                    window.stor.thread_storage_photoimage = threading.Thread(target = window.stor.backend_photoimage_storage, args = (window.fileindex,))
                    window.stor.thread_storage_photoimage.start()
                
        else:                                       # gif and vid
            # check cache
            try:
                is_cached = self.stor.ListStor[self.fileindex].get("is_cached", False)
            
            except AttributeError:
                is_cached = False
            
            try:
                is_fullcached = fulllevel.stor.ListStor[self.fileindex].get("is_cached", False)
            
            except AttributeError:
                is_fullcached = False
                
            if self.is_full_mode:
                if fulllevel.stor.last_index is not None and fulllevel.stor.backend_run == False:
                    if abs(fulllevel.stor.last_index - self.fileindex) <= STORAGE_TRIGGER or fulllevel.stor.last_index - window.fileindex + len(window.fullfilelist) <= STORAGE_TRIGGER:
                        
                        fulllevel.stor.pause_backend = False
                        
                        print("start fulllevel thread")
                        logging.info("start fulllevel thread")
                        fulllevel.stor.thread_storage = threading.Thread(target = fulllevel.stor.backend_storage, args = (window.fileindex,))
                        
                        fulllevel.stor.stop_backend = False
                        fulllevel.stor.thread_storage.start()
                        
                if fulllevel.stor.backend_run_photoimage == False:
                    print("start fulllevel thread (PhotoImage)")
                    logging.info("start fulllevel thread (PhotoImage)")
                    fulllevel.stor.thread_storage_photoimage = threading.Thread(target = fulllevel.stor.backend_photoimage_storage, args = (window.fileindex,))
                    fulllevel.stor.thread_storage_photoimage.start()
                
                #time.sleep(0.05)                                         # to resolve the blink issue in full mode
                
                if window.is_slide_check:                         # photo album mode
                    if self.is_photoalbum_mode:
                        fulllevel.fullforward()                     # skip ani/vid
                    
                    else:                                         # slide mode
                        is_vid = True
                        self.ShowIMG_Full(nextpath, False, is_vid)           # to resolve the blink issue in slide mode
                        
                        if window.is_slide_check:                       # to avoid start slide again after quit slide
                            window.after(20, fulllevel.start_slide, is_fullcached, True)    # slight delay for next slide to fix crash issue of slide mode
                
                else:                                            # simple fullscreen
                    # self.ShowANI_Full(nextpath, is_fullcached)             
                    is_vid = True
                    self.ShowIMG_Full(nextpath, False, is_vid)                       # to resolve the blink issue in full mode
                    window.after(20, self.ShowANI_Full, nextpath, is_fullcached, self.fileindex)      # slight delay for ANI for releasing memory

            else:                                                 # window mode
                if window.stor.last_index is not None and window.stor.backend_run == False:
                    if abs(window.stor.last_index - self.fileindex) <= STORAGE_TRIGGER or window.stor.last_index - window.fileindex + len(window.fullfilelist) <= STORAGE_TRIGGER:
                        
                        window.stor.pause_backend = False
                        
                        print("start window thread")
                        logging.info("start window thread")
                        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
                        
                        window.stor.stop_backend = False
                        window.stor.thread_storage.start()
                        
                if window.stor.backend_run_photoimage == False and window.check_photoimage(window.fileindex):
                    print("start window thread (PhotoImage)")
                    logging.info("start window thread (PhotoImage")
                    window.stor.thread_storage_photoimage = threading.Thread(target = window.stor.backend_photoimage_storage, args = (window.fileindex,))
                    window.stor.thread_storage_photoimage.start()

                # self.ShowANI(nextpath, is_cached)
                window.after(10, self.ShowANI, nextpath, is_cached, self.fileindex)      # slight delay for ANI for releasing memory
            
    def check_photoimage(self, fileindex):
        
        for i in range(self.stor.FORWARD_PHOTOIMAGE_STORAGE):
            listindex = fileindex + i                    # next file
            if listindex >= len(self.fullfilelist):           # back to start
                listindex = listindex - len(self.fullfilelist)
            
            try:
                file_path = self.fullfilelist[listindex]
            
            except:
                return False
            
            file_ext = os.path.splitext(file_path)[1]
            
            if file_ext in (self.supported_ani | self.supported_vid):
                return True
        
        return False
            
# In[Backward Button]
    
    def backward(self, slide_forward = False, event=None):                               # all modes except manga mode
        
        self.is_stop_ani = True                            # stop previous ani
        self.zoom_factor = 1                            # reset zoom
        is_cached = False
        is_fullcached = False
        is_photocached = False
        is_vid = False
        self.is_gif_pause = False
        self.rotate_degree = 0
        
        pre_fileindex = self.fileindex
        prefile_name = os.path.split(self.fullfilelist[pre_fileindex])[1]
        self.fileindex = self.fileindex - 1                  # previous file
        if self.fileindex < 0:                          # back to end
            self.fileindex = len(self.fullfilelist) - 1
        
        print("backward - %i" %self.fileindex)
        logging.info("backward - %i" %self.fileindex)
            
        try:
            filepath = self.fullfilelist[self.fileindex]         # get path of previous file
        
        except IndexError:
            exception_emptypath()
        
        if window.is_web_mode:
            nextpath_folder = os.path.split(filepath)[0]
            pre_web_fileindex = self.web_fileindex
            
            if nextpath_folder == self.web_output_folder:
                self.web_fileindex = self.web_fileindex - 1
            
            else:
                self.web_fileindex = 0
                
            # print(self.web_fileindex)
            
            if not os.path.isfile(filepath):
                print("FileNotFoundError")
            
                # stop forward if not yet download image
                self.fileindex = pre_fileindex
                filepath = self.fullfilelist[self.fileindex] 
                self.web_fileindex = pre_web_fileindex
                # return None
        
        self.cancel_move()
        
        self.folder_entry.delete(0,"end")
        self.folder_entry.insert(1, filepath)           # replace folder entry
        
        listlevel.listbox1.delete(pre_fileindex)
        listlevel.listbox1.insert(pre_fileindex, prefile_name)
        
        file_name = os.path.split(filepath)[1]
        listlevel.listbox1.delete(self.fileindex)
        listlevel.listbox1.insert(self.fileindex, u"\u25B6 " + file_name)
        listlevel.listbox1.see(self.fileindex)
        listlevel.listbox2.see(self.fileindex)
        listlevel.listbox3.see(self.fileindex)
        listlevel.listbox4.see(self.fileindex)
        listlevel.listbox5.see(self.fileindex)
        
        file_ext = os.path.splitext(filepath)[1].lower()
        if file_ext in self.supported_img:                 # img
           
            # check cache
            if self.stor.ListStor[self.fileindex] is not None:
                is_cached = True
                
            if fulllevel.stor.ListStor[self.fileindex] is not None:
                is_fullcached = True 
            
            try:    # when not yet entered photoalbum mode
                if fulllevel.photoalbum.ListStor[self.fileindex] is not None:
                    is_photocached = True  
            
            except:
                pass
                # print("failed to modify photoalbum cache")
                # logging.info("failed to modify photoalbum cache")
            
            # check image enhance for previous image
            if settinglevel.is_enhanceall:
                self.next_enhance = True
            
            else:
                self.next_enhance = False
                settinglevel.enhancecurrent_check.set(False)   
        
            if self.is_full_mode:
                
                if self.is_photoalbum_mode:
                    self.ShowIMG_FullPhotoalbum(filepath, True, is_photocached)  # Photo Album mode
                    
                    if fulllevel.photo_preview_visible:
                        window.ShowIMG_Preview(filepath, False, False)
                        
                    # self.ShowIMG_FullPhotoalbum(filepath)   # Photo Album mode
                    window.after(20, self.ShowIMG_FullPhotoalbum, filepath, False, is_photocached)   # Photo Album mode
                    
                else:   
                    # self.ShowIMG_Full(filepath, is_fullcached)            # simple fullscreen or slide mode
                    if window.is_slide_check:                                # slide mode
                        is_vid = False
                        self.ShowIMG_Full(filepath, is_fullcached, is_vid, slide_forward)           # to resolve the blink issue in slide mode
                        
                        if window.is_slide_check:                                            # to avoid start slide again after quit slide
                            window.after(20, fulllevel.start_slide, is_fullcached, True)                # slight delay for next slide to fix crash issue of slide mode
                        
                    else:
                        self.ShowIMG_Full(filepath, is_fullcached)            # simple fullscreen
            else:
                self.ShowIMG(filepath, is_cached)                     # window mode 
                
        else:                                         # gif and vid 
            # check cache
            try:
                is_cached = self.stor.ListStor[self.fileindex].get("is_cached", False)
            
            except AttributeError:
                is_cached = False
            
            try:
                is_fullcached = fulllevel.stor.ListStor[self.fileindex].get("is_cached", False)
            
            except AttributeError:
                is_fullcached = False
                                                           
            if self.is_full_mode:  
                if window.is_slide_check:                         # photo album mode
                    if self.is_photoalbum_mode:
                        fulllevel.fullbackward()                     # skip ani/vid
                    
                    else:                                         # slide mode
                        # self.ShowANI_Full(filepath, is_fullcached)                # simple fullscreen, slide mode, Photo Album mode
                        is_vid = True
                        window.after(20, self.ShowANI_Full, filepath, is_fullcached, self.fileindex)      # slight delay for ANI for releasing memory   
                        self.ShowIMG_Full(filepath, False, is_vid)                       # to resolve the blink issue in full mode

                else:                                         # simple full screen mode
                    # self.ShowANI_Full(filepath, is_fullcached)                # simple fullscreen, slide mode, Photo Album mode
                    is_vid = True
                    window.after(20, self.ShowANI_Full, filepath, is_fullcached, self.fileindex)      # slight delay for ANI for releasing memory   
                    self.ShowIMG_Full(filepath, False, is_vid)                       # to resolve the blink issue in full mode
                        
            else:
                # self.ShowANI(filepath, is_cached)                     # window mode
                window.after(10, self.ShowANI, filepath, is_cached, self.fileindex)      # slight delay for ANI for releasing memory
            
# In[Show Image]
    
    def ShowIMG_legacy(self, pic_path, is_cached = False):                         # window mode
        print("ShowIMG_legacy")    
        logging.info("ShowIMG_legacy")
        
        #timer_start = time.perf_counter()
        self.is_stop_ani = True
        
        self.error_label.config(text = "")
        self.gif_con.attributes('-topmost', False)
        self.gif_con.withdraw()
        
        self.parent.update()                                 # update pic_w, pic_h for fullscreen resize 
        self.pic_canvas.delete("all")                        
      
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        try:
            img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
        
        except FileNotFoundError:
            exception_filenotfound()
        
        if self.rotate_degree != 0:                          # skip rotate if haven't clicked rotate
            img = img.rotate(self.rotate_degree, expand = True)
        
        img_w, img_h = img.size
        
        try:
            pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()  # get canvas width and height
    
        except:
            pass                                          # exception when resize with 0 canvas
    
        if pic_w > 1 and pic_h > 1:
    
            if settinglevel.is_original:
                resize_scale = 1
    
            else:
                resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
                resize_scale = min(resize_scale, 1)            # avoid bigger than original
    
            w, h = int(img_w * resize_scale * self.zoom_factor), int(img_h * resize_scale * self.zoom_factor)
    
            try:
                resize_img = img.resize((w, h))  # it needs two brackets
            
            except OSError:                              # fix OSError: image file is truncated
                print("OSError: image file is truncated")
                logging.info("OSError: image file is truncated")               
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                resize_img = img.resize((w, h))
            
            #time_diff = time.perf_counter() - timer_start
            #print("time diff: ", time_diff)

            self.image = ImageTk.PhotoImage(resize_img)
            self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = self.image)
            
            # self.parent.focus_set()
            
            img.close()
            resize_img.close()
            del img
            del resize_img
    
    def ShowIMG(self, pic_path, is_cached = False):                         # window mode
        print("ShowIMG")    
        logging.info("ShowIMG")
        
        #timer_start = time.perf_counter()
        
        self.stor.pause_backend = True
        
        self.anticlock_button.config(state=tk.NORMAL)
        self.clock_button.config(state=tk.NORMAL)
        
        self.is_stop_ani = True
        self.gif_con.attributes('-topmost', False)
        self.gif_con.withdraw()
        
        self.error_label.config(text = "")
        self.parent.update()                                 # update pic_w, pic_h for fullscreen resize 
        self.pic_canvas.delete("all")                        

        
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        try:
            pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()  # get canvas width and height
        
        except:
            print("failed to get pic_w pic_h")
            logging.info("failed to get pic_w pic_h")  
        
        if not is_cached:
            
            img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            
            try:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            except:
                print("failed to run cvtColor")
                logging.info("failed to run cvtColor")
                self.ShowIMG_legacy(pic_path)
                self.stor.pause_backend = False
                return None                      # change to legacy function and exit this function 
            
            if img is None:
                exception_filenotfound()
            
            if window.rotate_degree != 0:
                if window.rotate_degree == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                elif window.rotate_degree == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                
                elif window.rotate_degree == 270:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            
            img_h, img_w = img.shape[:2]
            
            if pic_w > 1 and pic_h > 1:

                if settinglevel.is_original:
                    resize_scale = 1
        
                else:
                    resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
                    #resize_scale = min(resize_scale, 1)            # avoid bigger than original
        
                w, h = int(img_w * resize_scale * self.zoom_factor), int(img_h * resize_scale * self.zoom_factor)
                w_h = (w, h)
                
                try:
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                
                except OSError:                              # fix OSError: image file is truncated
                    print("OSError: image file is truncated")
                    logging.info("OSError: image file is truncated")               
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                
                if self.rotate_degree == 0 and self.zoom_factor == 1 and settinglevel.is_storage:
                    self.stor.write_storage(self.fileindex, resize_img)
                
                del img
                
        else:
            resize_img = self.stor.ListStor[self.fileindex]

        #time_diff = time.perf_counter() - timer_start
        #print("time diff: ", time_diff)
        
        self.img_IE = resize_img   # keep image for image enhance
        
        try:      # fix TypeError: Cannot handle this data type: (1, 1, 3), <u2
            self.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
        
        except TypeError:
            self.ShowIMG_legacy(pic_path)       # change to legacy function and exit this function
            self.stor.pause_backend = False
            return None
        
        self.stor.pause_backend = False
        
        if window.next_enhance:
            window.ShowIMG_ImageEnhance()
        
        else:
            self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = self.image)
        
            self.parent.update()
            
        del resize_img
    
    # Show Image in Fullscreen and Slide mode
    
    def ShowIMG_Full_legacy(self, pic_path):                     # full screen mode
        print("ShowIMG_Full_legacy")
        logging.info("ShowIMG_Full_legacy")    
        
        window.is_stop_ani = True
        window.error_label.config(text = "")
        
        fulllevel.anticlock_button2.config(state=tk.NORMAL)
        fulllevel.clock_button2.config(state=tk.NORMAL)
        
        self.gif_con.attributes('-topmost', False)
        self.gif_con.withdraw()
        
        if len(pic_path) > 255:
            exception_pathtoolong()
            
        try:
            img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
            img_w, img_h = img.size
        
        except FileNotFoundError:
            exception_filenotfound()
        
        if settinglevel.is_original:
            resize_scale = 1
        
        else:
            resize_scale = min(window.full_w / img_w, window.full_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
        #resize_scale = min(resize_scale,1)            # avoid bigger than original
        w, h = int(img_w * resize_scale * window.zoom_factor) , int(img_h * resize_scale * window.zoom_factor)
        
        try:
            resize_img = img.resize((w, h))
        
        except OSError:                                # fix OSError: image file is truncated
            print("OSError: image file is truncated")
            logging.info("OSError: image file is truncated")   
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            resize_img = img.resize((w, h))  
            
        fulllevel.image = ImageTk.PhotoImage(resize_img)
        fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2, anchor="center", image = fulllevel.image)
        
        # img.close()
        # resize_img.close()
        del img
        del resize_img
    
        if window.is_slide_check:
            fulllevel.countdown_timer()

    def ShowIMG_Full(self, pic_path, is_fullcached = False, is_vid = False, slide_forward = False):                     # full screen mode
        print("ShowIMG_Full")
        logging.info("ShowIMG_Full")    
        
        #timer_start = time.perf_counter()
        
        fulllevel.stor.pause_backend = True
        window.is_stop_ani = True
        window.error_label.config(text = "")
        
        fulllevel.anticlock_button2.config(state=tk.NORMAL)
        fulllevel.clock_button2.config(state=tk.NORMAL)
        
        if is_vid and not window.hide_gif_con:
            window.gif_con.attributes('-topmost', True)
            window.gif_con.deiconify()
        
        else:
            window.gif_con.attributes('-topmost', False)
            window.gif_con.withdraw()
        
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        
        if not is_fullcached:
            
            if not is_vid:
                img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            
            else:                   # show first frame of vid
                #print("vidcap")
                vidcap = cv2.VideoCapture(pic_path)

                success = True
                while success:
                    success,img = vidcap.read()
                    
                    if success:          # get the first frame
                        break
                    
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
            if img is None:
                exception_filenotfound()
                
            if window.rotate_degree != 0:
                if window.rotate_degree == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                elif window.rotate_degree == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                
                elif window.rotate_degree == 270:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    
            img_h, img_w = img.shape[:2]
            
            if window.full_w > 1 and window.full_h > 1:
        
                if settinglevel.is_original:
                    resize_scale = 1
        
                else:
                    resize_scale = min(window.full_w / img_w, window.full_h / img_h)   # calculate the resize ratio, maintaining height-width scale
                    #resize_scale = min(resize_scale, 1)            # avoid bigger than original
        
                w, h = int(img_w * resize_scale * window.zoom_factor), int(img_h * resize_scale * window.zoom_factor)
                w_h = (w, h)

                try:
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                
                except OSError:                              # fix OSError: image file is truncated
                    print("OSError: image file is truncated")
                    logging.info("OSError: image file is truncated")               
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)

                if window.rotate_degree == 0 and window.zoom_factor == 1 and not is_vid and settinglevel.is_storage:
                    print("write stor")
                    fulllevel.stor.write_storage(window.fileindex, resize_img)
                
                del img
                
        else:
            resize_img = fulllevel.stor.ListStor[window.fileindex] 

        #time_diff = time.perf_counter() - timer_start
        #print("time diff: ", time_diff)

        window.img_IE = resize_img

        try:
            if window.is_slide_check and not is_vid and not slide_forward:
                fulllevel.ShowIMG_FadeOut(window.pre_pic, window.img_IE)
        
        except AttributeError:
            pass

        window.pre_pic = window.img_IE
        
        try:      # fix TypeError: Cannot handle this data type: (1, 1, 3), <u2
            fulllevel.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
        
        except TypeError:
            self.ShowIMG_Full_legacy(pic_path)
            fulllevel.stor.pause_backend = False
            return None
            
        if window.next_enhance and not is_vid:
            window.ShowIMG_ImageEnhance()
        
        else:
            fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2, anchor="center", image = fulllevel.image)
            fulllevel.popup.update()
        
        fulllevel.stor.pause_backend = False
        
        del resize_img
        
        if window.is_slide_check and not is_vid and slide_forward:
        # if window.is_slide_check and not is_vid:    # slide_check to avoid countdown in ani
            fulllevel.countdown_timer()
    
    def ShowIMG_FadeOut(self, pre_pic, next_pic):
        print("ShowIMG_FadeOut")
        logging.info("ShowIMG_FadeOut")
        
        current_index = window.fileindex
        
        pre_index = window.fileindex - 1
        if pre_index < 0:
            pre_index = len(window.fullfilelist) - 1
        
        pre_path = window.fullfilelist[pre_index]
        current_path = window.fullfilelist[window.fileindex]
        
        if os.path.splitext(pre_path)[1] != os.path.splitext(current_path)[1]:    # skip fade out if ani to img
            return None
        
        img1_weight = 0
         
        pre_h, pre_w = pre_pic.shape[:2]
        next_h, next_w = next_pic.shape[:2]
        
        if pre_h != next_h or pre_w != next_w:
            return None                        # skip fade out if diff size
        
        while img1_weight <= 1:
            
            if current_index != window.fileindex:
                return None
            
            if not window.is_slide_check:
                return None
            
            img1_weight = img1_weight + 0.03
            img2_weight = 1 - img1_weight  
             
            weighted_img = cv2.addWeighted(next_pic, img1_weight , pre_pic, img2_weight , 0)
            
            image = ImageTk.PhotoImage(image = Image.fromarray(weighted_img))
            fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2, anchor="center", image = image)
            
            fulllevel.popup.update()
            
            time.sleep(0.02)    
    
    # Show Image in Photo Album Mode
    
    def ShowIMG_FullPhotoalbum(self, pic_path, initial=False, is_photocached=False):          # Photo Album mode
        print("ShowIMG_FullPhotoalbum - initial: ", initial)
        logging.info("ShowIMG_FullPhotoalbum - initial: %s" %initial)
        
        window.is_stop_ani = True
        window.gif_con.attributes('-topmost', False)
        window.gif_con.withdraw()
        
        fulllevel.anticlock_button3.config(state=tk.NORMAL)
        fulllevel.clock_button3.config(state=tk.NORMAL)
        
        fulllevel.timer = settinglevel.default_timer    # reset timer
        fulllevel.slide_timer = settinglevel.default_timer    # reset timer
        
        if is_photocached:
            resize_img = fulllevel.photoalbum.ListStor[window.fileindex] 
            
            window.img_IE = resize_img
            
            resize_img = Image.fromarray(resize_img)
            fulllevel.img_w, fulllevel.img_h = resize_img.size
            
            if window.full_w / fulllevel.img_w >= window.full_h / fulllevel.img_h:  
                w,h = fulllevel.img_w, fulllevel.img_h
                h_diff = max(0, h - window.full_h)                               # diff between final pic height and full screen height
                fulllevel.move_diff = (h_diff / fulllevel.timer / settinglevel.timer_frame) * -1     # move distance per frame
          
                if window.next_enhance:
                    window.ShowIMG_ImageEnhance()
                
                else:
                    fulllevel.pic_canvas.image = ImageTk.PhotoImage(resize_img)
                    fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(window.full_w / 2, 0, anchor="n", image = fulllevel.pic_canvas.image) # final pic
               
                del resize_img
                
                if not initial:     
                    fulllevel.move_photoalbum("h")
            
            else:
                w,h = resize_img.size
                w_diff = max(0, w - window.full_w)                            # diff between final pic width and full screen width
                fulllevel.move_diff = (w_diff / fulllevel.timer / settinglevel.timer_frame) * -1    # move distance per frame
                
                if window.next_enhance:
                    window.ShowIMG_ImageEnhance()
                
                else:
                    fulllevel.pic_canvas.image = ImageTk.PhotoImage(resize_img)
                    fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(0, window.full_h / 2, anchor="w",image = fulllevel.pic_canvas.image) # final pic
                
                del resize_img
                
                if not initial:
                    fulllevel.move_photoalbum("w")
        
        else:
            img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            if window.rotate_degree != 0:
                if window.rotate_degree == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                elif window.rotate_degree == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                
                elif window.rotate_degree == 270:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                    
            fulllevel.img_h, fulllevel.img_w = img.shape[:2]
            
            photoalbum_zoom_factor = window.photoalbum_zoom_factor
    
            if window.full_w / fulllevel.img_w >= window.full_h / fulllevel.img_h:                    # if the image is narrower than screen
                resize_scale = window.full_w / fulllevel.img_w                    # calculate the resize ratio, maintaining height-width scale
                w, h = int(fulllevel.img_w * resize_scale * photoalbum_zoom_factor), int(fulllevel.img_h * resize_scale * photoalbum_zoom_factor)
                
                if w < window.full_w and h < window.full_h:        # fit fullscreen size if the image is smaller than full screen
                    resize_scale = min(window.full_w / fulllevel.img_w, window.full_h / fulllevel.img_h)
                    w, h = int(fulllevel.img_w * resize_scale), int(fulllevel.img_h * resize_scale)
                
                h_diff = max(0, h - window.full_h)                               # diff between final pic height and full screen height
                fulllevel.move_diff = (h_diff / fulllevel.timer / settinglevel.timer_frame) * -1      # move distance per frame
        
                w_h = (w,h)
                
                try:
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                
                except OSError:                              # fix OSError: image file is truncated
                    print("OSError: image file is truncated")
                    logging.info("OSError: image file is truncated")               
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)

                try:
                    fulllevel.pic_canvas.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
                
                except TypeError:
                    self.ShowIMG_FullPhotoalbum_Legacy(pic_path)
                    fulllevel.stor.pause_backend = False
                    
                if window.rotate_degree == 0 and settinglevel.is_storage:
                    print("write stor")
                    fulllevel.photoalbum.write_storage(window.fileindex, resize_img)
                
                window.img_IE = resize_img
                
                del img
                del resize_img
                
                if window.next_enhance:
                    window.ShowIMG_ImageEnhance()
                
                else:
                    fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(window.full_w / 2, 0, anchor="n", image = fulllevel.pic_canvas.image) # final pic
                    
                if not initial:
                    fulllevel.move_photoalbum("h")
                    
            else:                                                            # if the image is wider than screen
                resize_scale = window.full_h / fulllevel.img_h                    # calculate the resize ratio, maintaining height-width scale
                w, h = int(fulllevel.img_w * resize_scale), int(fulllevel.img_h * resize_scale)       # photoalbum_zoom_factor does not support this kind of pic
                w_h = (w,h)
                w_diff = max(0, w - window.full_w)                            # diff between final pic width and full screen width
                fulllevel.move_diff = (w_diff / fulllevel.timer / settinglevel.timer_frame) * -1    # move distance per frame
                
                try:
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                
                except OSError:                              # fix OSError: image file is truncated
                    print("OSError: image file is truncated")
                    logging.info("OSError: image file is truncated")               
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                    
                try:
                    fulllevel.pic_canvas.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
                
                except TypeError:
                    self.ShowIMG_FullPhotoalbum_Legacy(pic_path, True)
                    window.after(10, self.ShowIMG_FullPhotoalbum_Legacy, pic_path, False)
                    fulllevel.stor.pause_backend = False
   
                if window.rotate_degree == 0 and settinglevel.is_storage:
                    print("write stor")
                    fulllevel.photoalbum.write_storage(window.fileindex, resize_img)
                
                window.img_IE = resize_img
                
                del img
                del resize_img
                
                if window.next_enhance:
                    window.ShowIMG_ImageEnhance()
                
                else:
                    fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(0, window.full_h / 2, anchor="w",image = fulllevel.pic_canvas.image) # final pic                    
                
                if not initial:       
                    fulllevel.move_photoalbum("w")
    
    def ShowIMG_FullPhotoalbum_Legacy(self, pic_path, initial=False):          # Photo Album mode
        print("ShowIMG_FullPhotoalbum_Legacy - initial: ", initial)
        logging.info("ShowIMG_FullPhotoalbum_Legacy - initial: %s" %initial)
        
        window.is_stop_ani = True
        window.gif_con.attributes('-topmost', False)
        window.gif_con.withdraw()
        
        fulllevel.anticlock_button3.config(state=tk.NORMAL)
        fulllevel.clock_button3.config(state=tk.NORMAL)
        
        fulllevel.timer = settinglevel.default_timer    # reset timer
        
        img = Image.open(pic_path)
                
        if window.rotate_degree != 0:                          # skip rotate if haven't clicked rotate
            img = img.rotate(window.rotate_degree, expand = True)
            
        fulllevel.img_w, fulllevel.img_h = img.size
        
        photoalbum_zoom_factor = window.photoalbum_zoom_factor

        if window.full_w / fulllevel.img_w >= window.full_h / fulllevel.img_h:                    # if the image is narrower than screen
            resize_scale = window.full_w / fulllevel.img_w                    # calculate the resize ratio, maintaining height-width scale
            w, h = int(fulllevel.img_w * resize_scale * photoalbum_zoom_factor), int(fulllevel.img_h * resize_scale * photoalbum_zoom_factor)
            
            if w < window.full_w and h < window.full_h:        # fit fullscreen size if the image is smaller than full screen
                resize_scale = min(window.full_w / fulllevel.img_w, window.full_h / fulllevel.img_h)
                w, h = int(fulllevel.img_w * resize_scale), int(fulllevel.img_h * resize_scale)
            
            try:
                resize_img = img.resize((w, h))  
            
            except OSError:                               # fix OSError: image file is truncated
                print("OSError: image file is truncated")
                logging.info("OSError: image file is truncated")      
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                resize_img = img.resize((w, h)) 

            fulllevel.pic_canvas.image = ImageTk.PhotoImage(resize_img)
            fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(window.full_w / 2, 0, anchor="n", image = fulllevel.pic_canvas.image) # final pic
                
            del img
            del resize_img
            
            if window.next_enhance:
                window.ShowIMG_ImageEnhance()
            
            if not initial:
                h_diff = max(0, h - window.full_h)                               # diff between final pic height and full screen height
                fulllevel.move_diff = (h_diff / fulllevel.timer / settinglevel.timer_frame) * -1      # move distance per frame
               
                fulllevel.move_photoalbum("h")
                
        else:                                                            # if the image is wider than screen
            resize_scale = window.full_h / fulllevel.img_h                    # calculate the resize ratio, maintaining height-width scale
            w, h = int(fulllevel.img_w * resize_scale), int(fulllevel.img_h * resize_scale)       # photoalbum_zoom_factor does not support this kind of pic
            resize_img = img.resize((w, h))   
            fulllevel.pic_canvas.image = ImageTk.PhotoImage(resize_img)
            fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(0, window.full_h / 2, anchor="w",image = fulllevel.pic_canvas.image) # final pic
            
            del img
            del resize_img
            
            if window.next_enhance:
                window.ShowIMG_ImageEnhance()
                
            if not initial:
                w_diff = max(0, w - window.full_w)                            # diff between final pic width and full screen width
                fulllevel.move_diff = (w_diff / fulllevel.timer / settinglevel.timer_frame) * -1    # move distance per frame
                
                fulllevel.move_photoalbum("w")
    
    def ShowIMG_ImageEnhance(self, enhance = True):
        print("ShowIMG_ImageEnhance")    
        logging.info("ShowIMG_ImageEnhance")
        
        window.next_enhance = True
        pre_timer_pause = True
        
        # only support img
        filepath = window.fullfilelist[window.fileindex]
        file_ext = os.path.splitext(filepath)[1].lower()      
        if file_ext not in window.supported_img:                 
            return None
        
        image_IE = Image.fromarray(np.uint8(window.img_IE))                 
        
        # enhancement
        if enhance:
            if round(window.brightness, 2) != 1.0:
                enhancer_Brightness = ImageEnhance.Brightness(image_IE)
                image_IE = enhancer_Brightness.enhance(window.brightness)
                
            if round(window.contrast, 2) != 1.0:  
                enhancer_Contrast = ImageEnhance.Contrast(image_IE)
                image_IE = enhancer_Contrast.enhance(window.contrast)
                
            if round(window.sharpness, 2) != 1.0:
                enhancer_Sharpness = ImageEnhance.Sharpness(image_IE)
                image_IE = enhancer_Sharpness.enhance(window.sharpness)
                
            if round(window.color, 2) != 1.0:
                enhancer_Color = ImageEnhance.Color(image_IE)
                image_IE = enhancer_Color.enhance(window.color)
            
            settinglevel.enhancecurrent_check.set(True)    
        
        # show pic
        if not window.is_full_mode:           # window mode
            window.pic_canvas.image = ImageTk.PhotoImage(image = image_IE)
            
            window.pic_canvas.delete("all")                 # remove existing image
            
            pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()
            window.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = window.pic_canvas.image)
            
            window.parent.update()
            
        else:
            if not window.is_photoalbum_mode and not window.is_manga_mode:            # simple full mode / slide mode
                fulllevel.pic_canvas.image = ImageTk.PhotoImage(image = image_IE)
                
                fulllevel.pic_canvas.delete("all")                 # remove existing image
                
                fulllevel.pic_canvas.create_image(self.full_w / 2, self.full_h / 2, anchor="center", image = fulllevel.pic_canvas.image)
                
                fulllevel.popup.update()
                
            elif window.is_photoalbum_mode:                                    # photo album mode
            
                if not window.is_timer_pause:                # pause photoalbum move to avoid wrong timer calculation
                    pre_timer_pause = False
                    window.is_timer_pause = True
                
                fulllevel.pic_canvas.image = ImageTk.PhotoImage(image = image_IE)
                
                try:
                    moved_distance = fulllevel.move_diff * settinglevel.timer_frame * (settinglevel.default_timer - fulllevel.slide_timer)  # calculate current position of pic
            
                except AttributeError:     # if no slide_timer
                    moved_distance = 0

                fulllevel.pic_canvas.delete("all")                 # remove existing image
                
                if window.full_w / fulllevel.img_w >= window.full_h / fulllevel.img_h:      # if pic is narrower than screen
                    fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(self.full_w / 2, moved_distance, anchor="n", image = fulllevel.pic_canvas.image)
                
                else:                                                                       # if pic is wider than screen
                    fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(moved_distance, self.full_h / 2, anchor="w", image = fulllevel.pic_canvas.image)
                
                fulllevel.popup.update()
                
                if not pre_timer_pause:                      # resume photoalbum move if paused previously
                    window.is_timer_pause = False
                
        del image_IE
    
    def brightness_decrease(self, event=None):
        window.brightness = round(min(2.0, max(0.1, window.brightness - 0.1)),2)
        print("brightness: ", window.brightness)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox20.delete(0)
            settinglevel.ie_listbox20.insert(5, "  %.2f" %window.brightness) 
            
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")
        
        window.ShowIMG_ImageEnhance()

    def brightness_increase(self, event=None):
        window.brightness = round(min(2.0, max(0.1, window.brightness + 0.1)),2)
        print("brightness: ", window.brightness)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox20.delete(0)
            settinglevel.ie_listbox20.insert(5, "  %.2f" %window.brightness)  
        
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")

        window.ShowIMG_ImageEnhance()
        
    def contrast_decrease(self, event=None):
        window.contrast = round(min(2.0, max(0.1, window.contrast - 0.1)),2)
        print("contrast: ", window.contrast)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox21.delete(0)
            settinglevel.ie_listbox21.insert(5, "  %.2f" %window.contrast)  
        
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")
        
        window.ShowIMG_ImageEnhance()
        
    def contrast_increase(self, event=None):
        window.contrast = round(min(2.0, max(0.1, window.contrast + 0.1)),2)
        print("contrast: ", window.contrast)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox21.delete(0)
            settinglevel.ie_listbox21.insert(5, "  %.2f" %window.contrast)  
        
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")
        
        window.ShowIMG_ImageEnhance()
        
    def sharpness_decrease(self, event=None):
        window.sharpness = round(min(4.0, max(0.0, window.sharpness - 0.25)),2)
        print("sharpness: ", window.sharpness)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox22.delete(0)
            settinglevel.ie_listbox22.insert(5, "  %.2f" %window.sharpness)  
        
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")
        
        window.ShowIMG_ImageEnhance()
        
    def sharpness_increase(self, event=None):
        window.sharpness = round(min(4.0, max(0.0, window.sharpness + 0.25)),2)
        print("sharpness: ", window.sharpness)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox22.delete(0)
            settinglevel.ie_listbox22.insert(5, "  %.2f" %window.sharpness)  
        
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")
        
        window.ShowIMG_ImageEnhance()
        
    def color_decrease(self, event=None):
        window.color = round(min(2.0, max(0.1, window.color - 0.1)),2)
        print("color: ", window.color)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox23.delete(0)
            settinglevel.ie_listbox23.insert(5, "  %.2f" %window.color)  
        
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")
        
        window.ShowIMG_ImageEnhance()
        
    def color_increase(self, event=None):
        window.color = round(min(2.0, max(0.1, window.color + 0.1)),2)
        print("color: ", window.color)
        
        try:      # error when the ie has not been created
            settinglevel.ie_listbox23.delete(0)
            settinglevel.ie_listbox23.insert(5, "  %.2f" %window.color)  
        
        except:
            print("failed to modify ie_listbox20")
            logging.info("failed to modify ie_listbox20")
        
        window.ShowIMG_ImageEnhance()
    
    def check_timer_pause(self):                                 # check if it is paused in zoom-slide mode
        
        if window.is_timer_pause:
            time.sleep(0.1)
            return True
        
        else:
            return False  
        
    def anticlockwise(self, event=None):
        print("anticlockwise")    
        logging.info("anticlockwise")
        
        window.stop_album = True                                        # to break loop in photo album mode
        
        fulllevel.timer = settinglevel.default_timer                             # reset timer in slide mode
        
        window.rotate_degree = (window.rotate_degree + 90) % 360                  # anti-clockwise
               
        filepath = window.fullfilelist[window.fileindex]
        
        file_ext = os.path.splitext(filepath)[1].lower()      
        
        if file_ext in window.supported_img:  
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    
                    if fulllevel.photo_preview_visible:
                        window.ShowIMG_Preview(filepath, False, False)
                        
                    window.after(20, window.ShowIMG_FullPhotoalbum, filepath)
                    
                else:
                    window.ShowIMG_Full(filepath)
            
            else:
                window.ShowIMG(filepath)
        
    def clockwise(self, event=None):
        print("clockwise")    
        logging.info("clockwise")
        
        window.stop_album = True                                        # to break loop in photo album mode
        
        fulllevel.timer = settinglevel.default_timer                             # reset timer in slide mode
        
        window.rotate_degree = (window.rotate_degree - 90) % 360                  # clockwise
        
        filepath = window.fullfilelist[window.fileindex]
        
        file_ext = os.path.splitext(filepath)[1].lower()      
        
        if file_ext in window.supported_img:  
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    
                    if fulllevel.photo_preview_visible:
                        window.ShowIMG_Preview(filepath, False, False)
                        
                    window.after(20, window.ShowIMG_FullPhotoalbum, filepath)
                
                else:
                    window.ShowIMG_Full(filepath)
            
            else:
                window.ShowIMG(filepath)
                
    def ShowIMG_Preview(self, pic_path, is_vid, listbox):                     # full screen mode
        print("ShowIMG_Preview")
        logging.info("ShowIMG_Preview")    
        
        #timer_start = time.perf_counter()
        if len(pic_path) > 255:
            exception_pathtoolong()

        if not is_vid:
            img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
        
        else:                   # show first frame of vid or gif
            #print("vidcap")
            vidcap = cv2.VideoCapture(pic_path)

            success = True
            while success:
                success,img = vidcap.read()
                
                if success:          # get the first frame
                    break
        
        if not listbox:            # for photo album only
            if window.rotate_degree != 0:
                if window.rotate_degree == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                
                elif window.rotate_degree == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                
                elif window.rotate_degree == 270:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if img is None:
            exception_filenotfound()
                
        img_h, img_w = img.shape[:2]
        
        if listbox:
            resize_scale = min(listlevel.list_canva_w / img_w, listlevel.list_canva_h / img_h)   # calculate the resize ratio, maintaining height-width scale
        
        else:
            resize_scale = min(fulllevel.photo_canva_w / img_w, fulllevel.photo_canva_h / img_h)   # calculate the resize ratio, maintaining height-width scale
        
        w, h = int(img_w * resize_scale), int(img_h * resize_scale)
        w_h = (w, h)
            
        try:
            resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
        
        except OSError:                              # fix OSError: image file is truncated
            print("OSError: image file is truncated")
            logging.info("OSError: image file is truncated")               
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            resize_img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
        
        del img
        
        #time_diff = time.perf_counter() - timer_start
        #print("time diff: ", time_diff)
        
        if listbox:
        # try:      # fix TypeError: Cannot handle this data type: (1, 1, 3), <u2
            listlevel.pic_canvas.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
            
            # except TypeError:
            #     self.ShowIMG_Full_legacy(pic_path)
                
            listlevel.pic_canvas.create_image(listlevel.list_canva_w / 2, listlevel.list_canva_h / 2, anchor="center", image = listlevel.pic_canvas.image)
            
            listlevel.list_canva.update()
        
        else:
            fulllevel.photo_canvas.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
            
            if fulllevel.photo_preview_auto_adjust:                # auto adjust by default and false after adjusting size
                fulllevel.photo_preview.geometry('%dx%d' %(w, h))    # adjust the preview window size
                fulllevel.photo_canvas.create_image(w / 2 - 1, h / 2, anchor="center", image = fulllevel.photo_canvas.image)
            else:
                fulllevel.photo_canvas.create_image(fulllevel.photo_canva_w / 2 - 1, fulllevel.photo_canva_h / 2, anchor="center", image = fulllevel.photo_canvas.image)
            
            fulllevel.photo_preview.update()
    
        del resize_img
             
# In[Show Animation]
    
    # def ShowANI_legacy(self, pic_path, is_cached = False):                       # window mode
    #     print("ShowANI")
    #     logging.info("ShowANI")
    
    #     self.is_stop_ani = False                         # enable running animation
    #     self.pic_canvas.delete("all")                 # remove existing image
    #     gif_img = []                             # create list to store frames of gif
    #     window.gif_speed2 = 1
    #     window.gif_speed3 = 1
    #     #self.is_ani_ready = False
    #     #self.ani_frame = 0
    #     self.error_label.config(text = "")
        
    #     self.gif_con.attributes('-topmost', True)
    #     self.gif_con.focus_set()
    #     self.gif_con.deiconify()
        
    #     if len(pic_path) > 255:
    #         exception_pathtoolong()
        
    #     #thread_ani_backend = threading.Thread(target = self.ShowANI_backend, args=(pic_path,))
    #     #thread_ani_backend.start()
        
    #     try:
    #         gif_img = Image.open(pic_path)
        
    #     except FileNotFoundError:
    #         exception_filenotfound()
        
    #     iter = ImageSequence.Iterator(gif_img)
    #     iter_length = len(list(iter))                  # get number of frame of iter
    #     #print(iter_length)
    #     del iter
        
    #     self.parent.update()
    #     self.parent.focus_set()

    #     pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()
    
    #     while not window.is_stop_ani and not window.is_full_mode:          # loop gif until stop
            
    #         #if not self.is_ani_ready:

                        
    #         #logging.info("time_check3: %s", time.perf_counter())
    #         #timer_start2 = time.perf_counter()
    #         iter = ImageSequence.Iterator(gif_img)   # create iterator to get frames
    #         i = 0
            
    #         #if pic_w > 1 and pic_h > 1:    
    #         img_w, img_h = iter[0].size
            
    #         if settinglevel.is_original:
    #             resize_scale = 1

    #         else:
    #             resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
    #         w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            
    #         #time_diff2 = time.perf_counter() - timer_start2
    #         #print("time diff start: ", time_diff2)
    #         #logging.info("time_diff_start: %s", time_diff2)
    #         total_time_diff = 0
    #         for frame in iter:
    #             timer_start = time.perf_counter()
                
    #             if not window.is_stop_ani: # stop animation controlled by other def
    #                 i = i + 1
    #                 #print(i)
    #                 #logging.info(i)
                    
    #                 gif_speed = window.check_gifspeed()
    #                 resize_img = frame.resize((w, h)) 
    #                 pic = ImageTk.PhotoImage(resize_img)
    #                 self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = pic)  # create image frame by frame
                    
    #                 self.parent.update()
                    
    #                 try:
    #                     gif_duration = gif_img.info['duration']
    #                     #print("duration: ", gif_duration)
                            
    #                 except:
    #                     gif_duration = 40     # set to 40 if can't find duration
                    
    #                 if i != iter_length:    # skip sleep for last frame to reduce gif lag issue in exe
                        
    #                     time_diff = time.perf_counter() - timer_start
    #                     #print("time diff: ", time_diff)
                           
    #                     sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.008))
    #                     sleep_time = min(1, sleep_time)
    #                     #print("sleep : ", sleep_time)
                    
    #                     time.sleep(sleep_time)
                    
    #                 if i == iter_length:
    #                     #print("Total time diff: " ,total_time_diff)
    #                     total_time_diff = 0
    #                 else:
    #                     total_time_diff = total_time_diff + time_diff

    #                 resize_img.close()
    #                 del pic
    #                 del resize_img
                    
    #                 #else:
    #                     #print("sleep : skipped for last frame")
                        
    #                 #logging.info("time_check1: %s", time.perf_counter())
    #                 '''
    #                 if not window.is_stop_ani:
    #                     logging.info("duration: %s", gif_duration)
                        
    #                     if i != iter_length:
    #                         logging.info("time_diff: %s", time_diff)
    #                         logging.info("sleep : %s", sleep_time)
                        
    #                     else: 
    #                         logging.info("sleep : skipped for last frame")
    #                         '''

    #                 #logging.info("time_check2: %s", time.perf_counter())
    #             else:
    #                 break
    #     '''    
    #     else:
    #         self.ShowANI_2(gif_duration, iter_length)
    #         '''
                        
                    
    #     del iter
    #     del gif_img
        
    def ShowANI(self, pic_path, is_cached = False, fileindex = None):                       # window mode
        print("ShowANI")
        logging.info("ShowANI")

        gc.disable()                                     # disable garbage collection
        #time0 = time.perf_counter()
        self.anticlock_button.config(state=tk.DISABLED)
        self.clock_button.config(state=tk.DISABLED)

        self.is_stop_ani = False                         # enable running animation
        self.stor.pause_backend = True
        photoimage_cached = False
        # self.pic_canvas.delete("all")                 # remove existing image
        self.error_label.config(text = "")
        window.gif_speed2 = 1
        window.gif_speed3 = 1
        window.frame_skip = False
        self.gif_con.attributes('-topmost', True)
        self.gif_con.deiconify()

        pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()
        
        if fileindex is None:     # get fileindex from forward / backward to fix fileindex change by fast click (IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices)
            fileindex = window.fileindex
            
        if is_cached:
            gif_duration = self.stor.ListStor[fileindex]["gif_duration"]
            gif_frame = self.stor.ListStor[fileindex]["img"]
            gif_len = len(gif_frame)
            
        else:
            if os.path.splitext(pic_path)[1].lower() in window.supported_ani:
                gif_len, gif_duration, gif_frame = self.Gif_Pic(pic_path, pic_w, pic_h)
            
            elif os.path.splitext(pic_path)[1].lower() in window.supported_vid:
                gif_len, gif_duration, gif_frame = self.Vid_Pic(pic_path, pic_w, pic_h)

        pic_frame = []
    
        if self.stor.ListPhotoStor[fileindex] is not None:
            for i in range(len(self.stor.ListPhotoStor[fileindex]["img"])):
                pic = self.stor.ListPhotoStor[fileindex]["img"][i]
                pic_frame.append(pic)
                photoimage_cached = True
                
            self.stor.clear_photoimage_storage(fileindex)     # clear cache after copying the photoimage
                              
        i = 0
        first_loop = True
        diff_actual_dur = 0
        self.stor.pause_backend = False
        timer_start = time.perf_counter()
        while not window.is_stop_ani and not window.is_full_mode:          # loop gif until stop
            timer_start2 = time.perf_counter()
            gif_dur = gif_duration[i]  

            if window.frame_skip > 0 and not first_loop:                                 # skip frame if gif_speed2 is low
               if np.floor(i % window.frame_skip) == 0 and i != gif_len - 1 and i != 0:
                   #print("Skipped :", i)
                   i = (i + 1) % gif_len
                   
                   continue
            
            if diff_actual_dur >= gif_dur / 2 and not first_loop and settinglevel.is_skipframespeed:               # skip frame if diff between actual vid and viewer is larger than half of next frame duration
                if i != gif_len - 1 and i != 0:
                    i = (i + 1) % gif_len
                    # print("Skipped :", i)
                    time_diff2 = time.perf_counter() - timer_start2
                    diff_actual_dur = diff_actual_dur - gif_dur + time_diff2

                    continue
                
            gif_speed = window.check_gifspeed()
            # print(gif_speed)
            
            if i == gif_len - 1:     # random gif speed
                if settinglevel.random_gifspeed:
                    rad = random.random()
                    window.gif_speed3 = (rad - 0.5) * 0.5 + 1
                    #print(window.gif_speed3)
                
                # time_diff2 = time.perf_counter() - timer_start
                # print(time_diff2)
            try:            
                if first_loop and not photoimage_cached:     # create a list to store pic in first loop
                    pic = ImageTk.PhotoImage(image = Image.fromarray(gif_frame[i]))
                    pic_frame.append(pic)
                    # print("not photoimage cached")
                    
                self.pic_canvas.delete("all")                 # remove existing image
                self.image = pic_frame[i]
                self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = self.image)  # create image frame by frame
            
            except Exception:   # fix the issue of some gifs doesn't have last frame
                print("Exception: No frame ", i)
                logging.info("Exception: No frame %s" %i)
                gif_len = len(pic_frame)
                i = gif_len - 1
                
            while window.is_gif_pause:               # pause gif
                time.sleep(0.1)
                self.parent.update()
                timer_start = time.perf_counter()
            
            self.parent.update()
            #if i != gif_len:    # skip sleep for last frame to reduce gif lag issue in exe
                
            time_diff = time.perf_counter() - timer_start

            sleep_time = max(0, gif_dur * gif_speed  - (time_diff + 0.0))
            sleep_time = min(1, sleep_time)
            
            # print("gif duration: ", gif_dur)
            # print("time diff: ", time_diff)
            # print("sleep : ", sleep_time)
            
            time.sleep(sleep_time)
            
            timer_start = time.perf_counter()
            
            if not first_loop and settinglevel.is_skipframespeed:
                diff_actual_dur = diff_actual_dur + max(0, time_diff - gif_dur)     
                # print("diff between actual vid and viewer: ", diff_actual_dur)
                
            i = (i + 1) % gif_len
            
            if i == 0:                  # end of loop
                first_loop = False
            '''
            if i == 0:
                print("Total time diff: " ,total_time_diff)
                total_time_diff = 0
                
            else:
                total_time_diff = total_time_diff + time_diff
            '''
        
        del gif_frame
        del pic_frame
        gc.enable()
    
    def Gif_Pic(self, pic_path, pic_w, pic_h):
        print("Gif_Pic")
        logging.info("Gif_Pic")
        
        cv_gif = []                             # create list to store frames of gif

        if len(pic_path) > 255:
            exception_pathtoolong()
        
        try:
            pil_gif = Image.open(pic_path)

        except FileNotFoundError:
            exception_filenotfound()

        img_w, img_h = pil_gif.size

        gif_duration = []

        iter = ImageSequence.Iterator(pil_gif) 
        
        for frame in iter:
            try:
                frame_duration = frame.info['duration']
                # if frame_duration == 0:     
                #         frame_duration = 40
                gif_duration.append(frame_duration / 1000)

            except:
                gif_duration.append(40 / 1000)   # set to 40 if can't find duration
        
        self.parent.update()
        
        # if window.is_stop_ani:
        #     try:
        #         pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()
        #         self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = self.image)  # create image frame by frame
            
        #     except:
        #         pass
            
        #     print("stop_ani_1")
        #     return None, None, None
        
        #print(gif_duration)

        # del pil_gif

        if settinglevel.is_original:
            resize_scale = 1

        else:
            resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
        
        w, h = int(img_w * resize_scale), int(img_h * resize_scale)
        w_h = (w, h)

        try:
            cv_gif = imageio.mimread(pic_path, memtest=False)

            gif_len = len(cv_gif)
            
            gif_frame = []

            for img in cv_gif:
                img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                gif_frame.append(img)
                
        except ValueError:     # for opening .webp file
            gif_frame = []
            i = 0
            try:
                while True:
                    frame = pil_gif.copy()
                    
                    resize_frame = frame.resize((w,h))
                    
                    buf = io.BytesIO()
                    resize_frame.save(buf, format='PNG')
                    byte_im = buf.getvalue()
                    img = np.asarray(bytearray(byte_im), dtype="uint8")
                    
                    img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    gif_frame.append(img)
                    
                    pil_gif.seek(i)
                    i = i + 1
                    
            except EOFError:
                del gif_frame[-1]
            
            gif_len = len(gif_frame)

        if not self.event_resize_stopstorage:       # stop storage after event_resize
            self.stor.write_ani_storage(window.fileindex, gif_duration=gif_duration, is_cached=True, img=gif_frame)
        
        if settinglevel.is_storage:
            print("Cached: window - ", window.fileindex, " (Ani)")
            logging.info("Cached: window - %s (Ani) ", window.fileindex)

        # del img
        # del cv_gif
        del pil_gif
        
        return gif_len, gif_duration, gif_frame
    
    def Vid_Pic(self, pic_path, pic_w, pic_h):
        print("Vid_Pic")
        logging.info("Vid_Pic")
        
        window.error_label.config(text = "Loading...")
        vidcap = cv2.VideoCapture(pic_path)

        img_w = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
        img_h = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        MAX_FRAME = 500
        gif_len = min(MAX_FRAME, int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)))
        # print(gif_len)
        gif_duration = []
        gif_frame = []
        
        fps = vidcap.get(cv2.CAP_PROP_FPS)    # convert frame per second to gif duration
        
        # print(fps)
        gif_duration = [round(1/fps ,6)] * (gif_len + 1)
        # print(gif_duration)
        
        if settinglevel.is_original:
            resize_scale = 1
            
        else:
            resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
        
        w, h = int(img_w * resize_scale), int(img_h * resize_scale)
        w_h = (w, h)
        
        i = 0
        success = True
        while success:
            success,image = vidcap.read()
            #print('Read a new frame: ', success, gif_len)

            if success:
                image = cv2.resize(image, w_h, interpolation = cv2.INTER_AREA)
                image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                gif_frame.append(image)
                
                i = i + 1
                if i >= MAX_FRAME:
                    window.error_label.config(text = "Max frame reached : %s" %MAX_FRAME)
                    break
                
                self.parent.update()
                if window.is_stop_ani:     # cancel loading vid if forward/backward
                    try:
                        pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()
                        self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = self.image)  # create image frame by frame
                    
                    except:
                        print("failed to get pic_w pic_h")
                        logging.info("failed to get pic_w pic_h")
                    
                    window.error_label.config(text = "")
                    print("stop loading video")
                    
                    del image
                    del vidcap
                    
                    return None, None, None
            
        else:
            window.error_label.config(text = "")
                
        if not self.event_resize_stopstorage:       # stop storage after event_resize
            self.stor.write_ani_storage(window.fileindex, gif_duration=gif_duration, is_cached=True, img=gif_frame)
        
        if settinglevel.is_storage:
            print("Cached: window - ", window.fileindex, " (Vid)")
            logging.info("Cached: window - %s (Vid) ", window.fileindex) 
            
        del image
        del vidcap

        return gif_len, gif_duration, gif_frame
    
# Show Animation in Fullscreen, Slide mode and Photo Album mode
    
    # def ShowANI_Full_legacy(self, pic_path):
    #     print("showANI_Full")
    #     logging.info("showANI_Full")
        
    #     window.is_stop_ani = False                         # enable running animation
    #     window.is_skip_ani = False
    #     window.gif_speed2 = 1
    #     window.gif_speed3 = 1
        
    #     self.gif_con.attributes('-topmost', True)
    #     self.gif_con.focus_set()
    #     self.gif_con.deiconify()
        
    #     window.error_label.config(text = "")
    #     fulllevel.pic_canvas.delete("all")                 # remove existing image
        
    #     if window.is_slide_check:
    
    #         fulllevel.timer = settinglevel.gif_loop     # get timer
        
    #     gif_img2 = []                             # create list to store frames of gif
        
    #     if len(pic_path) > 255:
    #         exception_pathtoolong()
            
    #     try:
    #         gif_img2 = Image.open(pic_path)
        
    #     except FileNotFoundError:
    #         exception_filenotfound()
        
    #     iter = ImageSequence.Iterator(gif_img2)
    #     iter_length = len(list(iter))               # get number of frame of iter
    #     del iter
    #     total_time_diff = 0
    #     while not window.is_stop_ani and window.is_full_mode:          # loop gif until stop
    #         #timer_start2 = time.perf_counter()
    #         iter = ImageSequence.Iterator(gif_img2)   # create iterator to get frames
    #         i = 0
            
    #         img_w, img_h = iter[0].size
            
    #         if settinglevel.is_original:
    #             resize_scale = 1
    
    #         else:
    #             resize_scale = min(window.full_w / img_w, window.full_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
    #         w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            
    #         #time_diff2 = time.perf_counter() - timer_start2
    #         #print("time diff start: ", time_diff2)
    #         #logging.info("time_diff_start: %s", time_diff2)
            
    #         for frame in iter:
    #             timer_start = time.perf_counter()
                
    #             if not window.is_stop_ani: # stop animation controlled by other def
    #                 i = i + 1
    #                 #print(i)
    #                 #logging.info(i)
                    
    #                 if window.is_skip_ani:                         # skip ani in slide mode
    #                     fulllevel.timer = fulllevel.check_timer(True)                 # control timer and countdown
                
    #                     if fulllevel.timer <= 0 and window.is_slide_check:
    #                         fulllevel.fullforward()                        # forward
                        
    #                     if fulllevel.timer > settinglevel.default_timer and window.is_slide_check:
    #                         fulllevel.fullbackward()                        # forward
                    
    #                 gif_speed = window.check_gifspeed()
    #                 resize_img = frame.resize((w, h))
    #                 pic = ImageTk.PhotoImage(resize_img)
    #                 fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2,anchor="center",image = pic)  # create image frame by frame
                    
    #                 while window.is_gif_pause:               # pause gif
    #                     time.sleep(0.1)
    #                     fulllevel.popup.update()
                    
    #                 fulllevel.popup.update()
                    
    #                 try:
    #                     gif_duration = gif_img2.info['duration']
                        
    #                 except:
    #                     gif_duration = 40
                    
    #                 if i != iter_length:    # skip sleep for last frame to reduce gif lag issue in exe
    #                     time_diff = time.perf_counter() - timer_start
    #                     #print("time diff: ", time_diff)
                        
    #                     sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.008))
    #                     #print("sleep : ", sleep_time)
    #                     sleep_time = min(1, sleep_time)
    #                     while window.is_gif_pause:
    #                         time.sleep(sleep_time)
                            
    #                 else:
    #                     if settinglevel.random_gifspeed:
    #                         rad = random.random()
    #                         window.gif_speed3 = (rad - 0.5) * 0.4 + 1
    #                         print(window.gif_speed3)
                        
    #                 if i == iter_length:
    #                     print("Total time diff: " ,total_time_diff)
    #                     total_time_diff = 0
    #                 else:
    #                     total_time_diff = total_time_diff + time_diff
                    
    #                 #else:
    #                     #print("sleep : skipped for last frame")
    #                 '''    
    #                 if not window.is_stop_ani:
    #                     logging.info("duration: %s", gif_duration)
                        
    #                     if i != iter_length:
    #                         logging.info("time_diff: %s", time_diff)
    #                         logging.info("sleep : %s", sleep_time)
                        
    #                     else: 
    #                         logging.info("sleep : skipped for last frame")
    #                         '''
    #             else:
    #                 break
                
    #         if window.is_slide_check:
    #             fulllevel.timer = fulllevel.check_timer(True)                 # control timer and countdown
    
    #             if fulllevel.timer <= 0 and window.is_slide_check:
    #                 fulllevel.fullforward()                        # forward
                
    #             if fulllevel.timer > settinglevel.gif_loop and window.is_slide_check:
    #                 fulllevel.fullbackward()                        # backward
        
    #     del iter
    #     del gif_img2
    #     del pic
    #     del resize_img
    
    def ShowANI_Full(self, pic_path, is_fullcached = False, fileindex = None):                       # window mode
        print("showANI_Full")
        logging.info("showANI_Full")
        
        file_ext = os.path.splitext(pic_path)[1]      # to fix unexpected ShowANI_Full
        if not file_ext in (self.supported_ani | self.supported_vid):
            print("Unexpected ShowANI_Full, pic_path=%s, fileindex=%s" %(pic_path, window.fileindex))
            logging.info("Unexpected ShowANI_Full, pic_path=%s, fileindex=%s" %(pic_path, window.fileindex))
            return None
        
        fulllevel.anticlock_button2.config(state=tk.DISABLED)
        fulllevel.clock_button2.config(state=tk.DISABLED)
        fulllevel.anticlock_button3.config(state=tk.DISABLED)
        fulllevel.clock_button3.config(state=tk.DISABLED)
        
        gc.disable()
        window.is_stop_ani = False                         # enable running animation
        window.is_skip_ani = False
        self.stor.pause_backend = True
        window.gif_speed2 = 1
        window.gif_speed3 = 1
        window.frame_skip = False
        gif_loop_override = 0
        gif_speed_override = 0
        pause_override = 0
        photoimage_cached = False
        fulllevel.timer = settinglevel.gif_loop            # get timer
        
        if fileindex is None:     # get fileindex from forward / backward to fix fileindex change by fast click (IndexError: only integers, slices (`:`), ellipsis (`...`), numpy.newaxis (`None`) and integer or boolean arrays are valid indices)
            fileindex = window.fileindex
        
        if not self.hide_gif_con:
            self.gif_con.attributes('-topmost', True)
            self.gif_con.deiconify()

        window.error_label.config(text = "")

        if window.is_slide_check:
            
            #load config_gif
            self.config = configparser.ConfigParser()
            config_path = os.path.join(os.path.split(pic_path)[0], "_config_gif.ini")
            self.config.read(config_path)
            
            file_name = os.path.split(pic_path)[1]
                            
            for section in self.config.sections():

                if section in file_name:
                    gif_loop_override = self.getconfig("gif_loop_override", gif_loop_override, section)
                    gif_speed_override = self.getconfig("gif_speed_override", gif_speed_override, section)
                    pause_override = self.getconfig("pause_override", pause_override, section)
            
            if gif_loop_override:
                fulllevel.timer = int(gif_loop_override)
        
            
            if gif_speed_override:
                window.gif_speed2 = round(float(gif_speed_override), 2)
                self.check_frame_skip()
            
            if pause_override:
                pause_override = round(float(pause_override), 2)
            
        if is_fullcached:
            gif_duration = fulllevel.stor.ListStor[fileindex]["gif_duration"]
            gif_frame = fulllevel.stor.ListStor[fileindex]["img"]
            gif_len = len(gif_frame)
            
        else:
            if os.path.splitext(pic_path)[1].lower() in window.supported_ani:
                gif_len, gif_duration, gif_frame = self.Gif_Pic_Full(pic_path)
            
            elif os.path.splitext(pic_path)[1].lower() in window.supported_vid:
                gif_len, gif_duration, gif_frame = self.Vid_Pic_Full(pic_path)
        
        #total_time_diff = 0
        pic_frame = []
        
        if fulllevel.stor.ListPhotoStor[fileindex] is not None:
            for i in range(len(fulllevel.stor.ListPhotoStor[fileindex]["img"])):
                pic = fulllevel.stor.ListPhotoStor[fileindex]["img"][i]
                pic_frame.append(pic)
                photoimage_cached = True
                
            fulllevel.stor.clear_photoimage_storage(fileindex)     # clear cache after copying the photoimage
        
        i = 0
        first_loop = True
        diff_actual_dur = 0
        self.stor.pause_backend = False
        timer_start = time.perf_counter()
        
        while not window.is_stop_ani and window.is_full_mode:          # loop gif until stop
            timer_start2 = time.perf_counter()
            gif_dur = gif_duration[i]  
        
            if window.frame_skip > 0 and not first_loop:                                 # skip frame if gif_speed2 is low
               if np.floor(i % window.frame_skip) == 0 and i != gif_len - 1 and i != 0:
                   #print("Skipped :", i)
                   i = (i + 1) % gif_len
                   
                   continue
            
            if diff_actual_dur >= gif_dur / 2 and not first_loop and settinglevel.is_skipframespeed:               # skip frame if diff between actual vid and viewer is larger than half of next frame duration
                if i != gif_len - 1 and i != 0:
                    i = (i + 1) % gif_len
                    # print("Skipped :", i)
                    time_diff2 = time.perf_counter() - timer_start2
                    diff_actual_dur = diff_actual_dur - gif_dur + time_diff2

                    continue
            
            gif_speed = window.check_gifspeed()
            
            if i == gif_len - 1:     # Random gif speed
                if settinglevel.random_gifspeed:
                    rad = random.random()
                    window.gif_speed3 = (rad - 0.5) * 0.5 + 1

            try:
                if first_loop and not photoimage_cached:     # create a list to store pic in first loop
                    pic = ImageTk.PhotoImage(image = Image.fromarray(gif_frame[i]))
                    pic_frame.append(pic)
                    # print("not photoimage cached")
                    
                # time_diff2 = time.perf_counter() - timer_start
                # print(time_diff2)
                fulllevel.image = pic_frame[i]
                fulllevel.pic_canvas.delete("all")                 # remove existing image
                fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2,anchor="center",image = fulllevel.image)  # create image frame by frame
                
            except Exception:   # fix the issue of some gifs doesn't have last frame
                print("Exception: No frame ", i)
                logging.info("Exception: No frame %s" %i)
                gif_len = len(pic_frame)
                i = gif_len - 1
            
            while window.is_gif_pause:               # pause gif
                time.sleep(0.1)
                fulllevel.popup.update()
                timer_start = time.perf_counter()
                
            fulllevel.popup.update()
            
            #if i != gif_len:    # skip sleep for last frame to reduce gif lag issue in exe
                
            time_diff = time.perf_counter() - timer_start

            sleep_time = max(0, gif_dur * gif_speed - time_diff)

            if window.is_slide_check and settinglevel.random_gifloop and i == gif_len - 1: # min 2.5 sec sleep for last frame in random gif loop, otherwise 1 sec
                sleep_time = min(2.5, sleep_time)
            
            else:
                sleep_time = min(1, sleep_time)
                
            # print("gif duration: ", gif_duration[i]/1000)
            # print("time diff: ", time_diff)
            # print("sleep : ", sleep_time)
            
            time.sleep(sleep_time)
            
            timer_start = time.perf_counter()
            
            if not first_loop and settinglevel.is_skipframespeed:
                diff_actual_dur = diff_actual_dur + max(0, time_diff - gif_dur)     
                # print("diff between actual vid and viewer: ", diff_actual_dur)
                
            i = (i + 1) % gif_len
            
            if i == 0:              # end of first loop
                first_loop = False
            
            if window.is_skip_ani:                         # skip ani in slide mode
                fulllevel.timer = fulllevel.check_timer(True, gif_duration[gif_len - 1])                 # control timer and countdown
        
                if fulllevel.timer <= 0 and window.is_slide_check:
                    fulllevel.fullforward()                        # forward
                
                if fulllevel.timer > settinglevel.gif_loop + 500 and window.is_slide_check:
                    fulllevel.fullbackward()                        # backward
            
            if i == 0 and window.is_slide_check:
                fulllevel.timer = fulllevel.check_timer(True, gif_duration[gif_len - 1], gif_loop_override)       # control timer and countdown
    
                if fulllevel.timer <= 0 and window.is_slide_check:
                    while pause_override > 0 and window.is_slide_check and not window.is_skip_ani:      # short pause in slide mode
                        pause_override = pause_override - 0.1
                        fulllevel.popup.update()
                        
                        time.sleep(0.1)
                        
                    fulllevel.fullforward()                        # forward
                
                if fulllevel.timer > settinglevel.gif_loop + 500 and window.is_slide_check:
                    fulllevel.fullbackward()                        # backward
            '''
            if i == 0:
                print("Total time diff: " ,total_time_diff)
                total_time_diff = 0
           
            else:
                total_time_diff = total_time_diff + time_diff
            '''
        
        del gif_frame  
        del pic_frame
        gc.enable()
        
    def Gif_Pic_Full(self, pic_path):
        print("Gif_Pic_Full")
        logging.info("Gif_Pic_Full")
        
        cv_gif = []                             # create list to store frames of gif
        
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        try:
            pil_gif = Image.open(pic_path)

        except FileNotFoundError:
            exception_filenotfound()
            
        img_w, img_h = pil_gif.size
        
        gif_duration = []
        
        iter = ImageSequence.Iterator(pil_gif) 
        
        for frame in iter:
            try:
                frame_duration = frame.info['duration']
                #if frame_duration < 40:
                 #   frame_duration = 40
                gif_duration.append(frame_duration / 1000)
            
            except:
                gif_duration.append(40 / 1000)   # set to 40 if can't find duration

        #print(gif_duration)
            
        # del pil_gif
        
        if settinglevel.is_original:
            resize_scale = 1

        else:
            resize_scale = min(window.full_w / img_w, window.full_h / img_h)   # calculate the resize ratio, maintaining height-width scale
        
        w, h = int(img_w * resize_scale), int(img_h * resize_scale)
        w_h = (w, h)
        
        try:
            cv_gif = imageio.mimread(pic_path, memtest=False)
            
            gif_len = len(cv_gif)
            
            gif_frame = []
            
            for img in cv_gif:
                img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                gif_frame.append(img)
                
        except ValueError:     # for opening .webp file
            gif_frame = []
            i = 0
            try:
                while True:
                    frame = pil_gif.copy()
                    
                    resize_frame = frame.resize((w,h))
                    
                    buf = io.BytesIO()
                    resize_frame.save(buf, format='PNG')
                    byte_im = buf.getvalue()
                    img = np.asarray(bytearray(byte_im), dtype="uint8")
                    
                    img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    
                    gif_frame.append(img)
                    
                    pil_gif.seek(i)
                    i = i + 1
                    
            except EOFError:
                del gif_frame[-1]
            
            gif_len = len(gif_frame)
            
        if not window.event_resize_stopstorage:       # stop storage after event_resize
            fulllevel.stor.write_ani_storage(window.fileindex, gif_duration=gif_duration, is_cached=True, img=gif_frame)
        
        if settinglevel.is_storage:
            print("Cached: full - ", window.fileindex, " (Ani)")
            logging.info("Cached: full - %s (Ani) ", window.fileindex)
        
        del img
        del cv_gif
        del pil_gif

        return gif_len, gif_duration, gif_frame

    def Vid_Pic_Full(self, pic_path):
        print("Vid_Pic_Full")
        logging.info("Vid_Pic_Full")
        
        vidcap = cv2.VideoCapture(pic_path)
        
        img_w = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
        img_h = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        MAX_FRAME = 500
        gif_len = min(MAX_FRAME, int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)))
        
        gif_duration = []
        gif_frame = []

        fps = vidcap.get(cv2.CAP_PROP_FPS)    # convert frame per second to gif duration
        #print(fps)
        gif_duration = [round(1/fps, 6)] * (gif_len + 1)
        
        if settinglevel.is_original:
            resize_scale = 1
            
        else:
            resize_scale = min(window.full_w / img_w, window.full_h / img_h)   # calculate the resize ratio, maintaining height-width scale
        
        w, h = int(img_w * resize_scale), int(img_h * resize_scale)
        w_h = (w, h)
        
        i = 0
        success = True
        while success:
            success, image = vidcap.read()
            #print('Read a new frame: ', success, gif_len)
            
            if success:
                image = cv2.resize(image, w_h, interpolation = cv2.INTER_AREA)
                image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                gif_frame.append(image)
                
                i = i + 1
                if i >= MAX_FRAME:
                    break
                
                self.parent.update()
                if window.is_stop_ani:     # cancel loading vid if forward/backward
                    try:
                        fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2,anchor="center",image = fulllevel.image)  
                    
                    except:
                        print("failed to create image")
                        logging.info("failed to create image")
                    
                    print("stop loading video")
                    
                    del image
                    del vidcap
                    
                    return None, None, None
                
        if not window.event_resize_stopstorage:       # stop storage after event_resize
            fulllevel.stor.write_ani_storage(window.fileindex, gif_duration=gif_duration, is_cached=True, img=gif_frame)

        if settinglevel.is_storage:
            print("Cached: full - ", window.fileindex, " (Vid)")
            logging.info("Cached: full - %s (Vid) ", window.fileindex)

        del image
        del vidcap
        
        return gif_len, gif_duration, gif_frame
    
    def check_gifspeed(self):
        
        # gif_speed : gif speed in settings
        # gif_speed2 : manually controlled gif speed
        # gif_speed3 : random generated after checking random gif speed
        # print(settinglevel.gif_speed)
        # print(window.gif_speed2)
        # print(window.gif_speed3)
        
        return settinglevel.gif_speed * window.gif_speed2 * window.gif_speed3

    def gif_speedup(self, event=None):
        
        window.gif_speed2 = round(max(0.3, window.gif_speed2 - 0.1), 2)
        
        self.check_frame_skip()
        
        #print("Gif Speed Up: ", window.gif_speed2, "; Frame Skip : ", window.frame_skip)
        logging.info("Gif Speed Up: %.2f", window.gif_speed2)
    
    def gif_speeddown(self, event=None):
        
        window.gif_speed2 = round(min(2, window.gif_speed2 + 0.1), 2)
        
        self.check_frame_skip()
        
        #print("Gif Speed Down: ", window.gif_speed2, "; Frame Skip : ", window.frame_skip)
        logging.info("Gif Speed Down: %.2f", window.gif_speed2)
    
    def check_frame_skip(self):
        
        if window.gif_speed2 == 0.7:
            window.frame_skip = 8
        
        elif window.gif_speed2 == 0.6:
            window.frame_skip = 5

        elif window.gif_speed2 == 0.5:
            window.frame_skip = 3

        elif window.gif_speed2 == 0.4:
            window.frame_skip = 2
        
        elif window.gif_speed2 == 0.3:
            window.frame_skip = 1.5
            
        else:
            window.frame_skip = False
        
        print("Frame Skip: ", window.frame_skip)
        
    def gif_pause(self, event=None):
        print("gif_pause")
        logging.info("gif_pause")
        
        if not self.is_gif_pause:
            self.is_gif_pause = True
        
        else:
            self.is_gif_pause = False

# In[When Resize]
    
    def window_resize(self, e):
        print("window_resize")
        logging.info("window_resize")
        
        window.is_gif_pause = True           # pause gif to gain stability
        
        time.sleep(0.2)                      # reduce the frequency of window resize to avoid crash
        
        settinglevel.window_state = "normal"
        
        window.stor.stop_storage(False) 
        fulllevel.stor.stop_storage(False)  
        
        window.stor.stop_backend = True        # force stop backend to avoid crash 
        fulllevel.stor.stop_backend = True
        
        x1 = self.parent.winfo_pointerx()
        y1 = self.parent.winfo_pointery()
        x0 = self.parent.winfo_rootx()
        y0 = self.parent.winfo_rooty()
       
        self.parent.geometry("%sx%s" % ((x1-x0),(y1-y0))) # for resizing the window
        
        window.is_gif_pause = False
        
    def event_resize(self, event=None):          # window mode
        
        window.parent.update()
        listlevel.listbox1.focus_set()
        self.zoom_factor = 1                    # reset zoom
        
        if event.width == self.parent.winfo_width() and event.height == self.parent.winfo_height(): # trigger
            self.check_width[0] = self.check_width[1]
            self.check_height[0] = self.check_height[1]
            self.check_width[1] = event.width
            self.check_height[1] = event.height
            
            if self.check_width[0] != self.check_width[1] or self.check_height[0] != self.check_height[1]: # 2nd trigger
                
                self.event_resize_no += 1
                if self.event_resize_no > 1:      # to skip the first event resize when start
                    print("event_resize")
                    logging.info("event_resize")
                    
                    if len(self.stor.ListStor) > 0:
                        self.stor.stop_storage(True)               
                        self.stor.create_reset_storage()
                    
                    window.stor.backend_run = True                          # temporarily stop restarting storage
                    self.event_resize_stopstorage = True
                    self.time_resize = time.perf_counter()
                    self.thread_resize = self.after(3000, self.thread_AfterResize) # trigger thread restart after 3 sec
                    
                    filepath = str(self.folder_entry.get())
                    file_ext = os.path.splitext(filepath)[1].lower()              # separate file name and extension
                    
                    if file_ext in self.supported_img:
                        self.ShowIMG(filepath)
                    
                    elif file_ext in (self.supported_ani | self.supported_vid):
                        self.ShowANI(filepath)                
                    
                    time.sleep(0.05)                      # reduce the frequency of event_resize

        window.stor.stop_backend = False
        fulllevel.stor.stop_backend = False
    
    def thread_AfterResize(self):
        print("After: ", time.perf_counter()- self.time_resize)
        logging.info("After: %s", time.perf_counter()- self.time_resize)
        
        window.stor.backend_run = False
        self.event_resize_stopstorage = False
        
        if time.perf_counter() - self.time_resize >= 3:
            if not window.stor.backend_run and len(window.fullfilelist) > 0:
                window.stor.stop_backend = False
                window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
                window.stor.thread_storage.start()

        if window.check_photoimage(window.fileindex):
            window.stor.thread_storage_photoimage = threading.Thread(target = window.stor.backend_photoimage_storage, args = (window.fileindex,))
            window.stor.thread_storage_photoimage.start()
        
# In[When Zoom]
    
    def event_zoom(self, event):                  # window mode or full screen mode         
        print("event_zoom")
        logging.info("event_zoom")
        
        if not window.event_zoom_ongoing:         # can't run until the previous zoom has been finished
            window.event_zoom_ongoing = True
            x = self.pic_canvas.canvasx(event.x)
            y = self.pic_canvas.canvasy(event.y)
                
            if event.delta > 1:                           # scroll up
                window.zoom_factor = window.zoom_factor + 0.5
            
            else:                                         # scroll down
                window.zoom_factor = max(window.zoom_factor - 0.5, 1)
            
            filepath = str(window.folder_entry.get())
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext in window.supported_img:                 # skip gif
                if window.is_full_mode:                            
                    self.ShowIMG_Full(filepath)
            
                else:                                             # move in window mode only
                    self.ShowIMG(filepath)
                
                try:
                    self.pic_canvas.scale("tk.ALL", x, y, window.zoom_factor, window.zoom_factor) 
                    
                except:
                    pass                                    # exception when slide mode -> zoom -> quit
            
            window.event_zoom_ongoing = False
            
    def cancel_move(self):
        
        ''' cancel move pic when no zoom
        try:
            pic_canvas.unbind('<ButtonPress-1>', pic_move_from)
            pic_canvas.unbind('<B1-Motion>', pic_move_to)
        
        except:
            pass
            '''
        self.pic_canvas.xview_moveto(self.origX)
        self.pic_canvas.yview_moveto(self.origY)
        
        if self.is_full_mode:
            fulllevel.pic_canvas.xview_moveto(fulllevel.origX)
            fulllevel.pic_canvas.yview_moveto(fulllevel.origY)
        
    def move_from(self, event):
        
        self.photo_y = event.y
        self.pic_canvas.scan_mark(event.x, event.y)
    
    def move_to(self, event):
        
        self.pic_canvas.scan_dragto(event.x, event.y, gain=1)
        
        if window.is_photoalbum_mode:
            self.pic_canvas.scan_dragto(event.x, self.photo_y, gain=1)

# In[When FocusIn]

    def event_focusin(self, event):
        # print("event_focusin")
        # logging.info("event_focusin")
        
        if self.hide:
            print("back_from_hide")
            logging.info("back_from_hide")
            self.hide = False
            self.parent.geometry('+{x}+{y}'.format(x=self.premin_x,y=self.premin_y))
            self.parent.focus_set()
            
        if self.is_full_mode:
            window.parent.attributes('-topmost', False)
            fulllevel.popup.focus_set()   

# In[Hide Window]

    def window_hide(self):
        print("window_hide")
        logging.info("window_hide")

        self.hide = True
        
        listlevel.hide_listbox()
        settinglevel.setting_hide()
        settinglevel.enhancer_hide()
        
        self.premin_x = self.parent.winfo_x() 
        self.premin_y = self.parent.winfo_y() 
    
        self.parent.geometry('+{x}+{y}'.format(x=-1000,y=-1000)) 

# In[Window Zoomed and Normal]

    def window_zoomed(self):
        print("window_zoomed")
        logging.info("window_zoomed")
        
        # record current size and position of window normal
        settinglevel.window_width = self.parent.winfo_width() 
        settinglevel.window_height = self.parent.winfo_height()
        settinglevel.window_x = self.parent.winfo_x()
        settinglevel.window_y = self.parent.winfo_y()
        self.grip.place(relx=0.0, rely=0.0, anchor="se")
        # self.parent.resizable(width=False, height=False)  # can't modify resizable otherwise can't show in taskbar
        
        self.max_button.config(text = "\u2583", command = self.window_normal)
        settinglevel.window_state = "zoomed"
        
        # the below works if single screen
        # SPI_GETWORKAREA = 0x0030
    
        # desktopWorkingArea = wintypes.RECT() # This var will receive the result to SystemParametersInfoW  
        
        # _ = windll.user32.SystemParametersInfoW(SPI_GETWORKAREA,0,byref(desktopWorkingArea),0)
        
        # right = desktopWorkingArea.right
        # bottom = desktopWorkingArea.bottom
        
        # self.parent.geometry("%dx%d+0+0" %(right, bottom)) 
        
        # multiple screen
        
        window_mid_pt = int(int(settinglevel.window_x) + int(settinglevel.window_width) / 2)   # find the mid point of parent to match window's behaviour
        
        try:
            monitor_info = GetMonitorInfo(MonitorFromPoint((window_mid_pt,0)))   # to get the current monitor based on x,y
        
        except:
            monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))                       # error if x,y not existent
            
        # monitor_area = monitor_info.get("Monitor")
        work_area = monitor_info.get("Work")                            # work area is the area without taskbar
        # print("The taskbar height is {}.".format(monitor_area[3]-work_area[3]))
        # print(monitor_area)
        # print(work_area)
        
        width = work_area[2] - work_area[0]
        height = work_area[3] - work_area[1]
        x = work_area[0]
        y = work_area[1]
        
        self.parent.geometry("%dx%d+%d+%d" %(width, height, x, y)) 
    
    def window_normal(self):
        print("window_normal")
        logging.info("window_normal")
        
        self.max_button.config(text = "\u2587", command = self.window_zoomed)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        settinglevel.window_state = "normal"
        self.parent.geometry('%dx%d+%d+%d' %(int(settinglevel.window_width), int(settinglevel.window_height), int(settinglevel.window_x), int(settinglevel.window_y))) # re adjust window size

    def getconfig(self, column, var, section="ImageViewer"):   # put under class WindowsGUI as it is shared by class FullscreenGUI and SettingsGUI
        
        try:
            if self.config.get(section, str(column)) == "False":
                return False                   # return boolean as all strings are deemed True
            
            elif self.config.get(section, str(column)) == "True":
                return True                   # return boolean as all strings are deemed True
            
            else:
                return self.config.get(section, str(column))
        
        except:
            return var
        
# In[fullscreen mode]

class FullscreenGUI(WindowGUI):
    
    def __init__(self, popup, full_con, photo_con, photo_preview, manga_con, name):
        print("class FullscreenGUI _init_")
        logging.info("class FullscreenGUI _init_")
        
        self.name = name
        self.popup = popup
        self.full_con = full_con
        self.photo_con = photo_con
        self.photo_preview = photo_preview
        self.manga_con = manga_con
        self.popup.withdraw()           # to avoid extra window pop up
        self.full_con.withdraw()        # to avoid extra window pop up
        self.photo_con.withdraw()       # to avoid extra window pop up
        self.photo_preview.withdraw()   # to avoid extra window pop up
        self.manga_con.withdraw()       # to avoid extra window pop up
        self.is_fullcreated = False
        self.stor = Storage("fulllevel")
        
        window.is_slide_check = False
        window.is_photoalbum_mode = False
        
    def enter_full(self):
        print("enter_full")

        if len(window.fullfilelist) == 0:
            exception_emptypath()
            return None 
        
        window.is_full_mode = True
        window.is_stop_ani = True
        self.con_visible = False
        window.Img_IE = None
        
        # reset photo preview
        self.photo_preview_auto_adjust = True
        self.photo_canva_w = 200
        self.photo_canva_h = 200
        self.photo_preview.geometry('%dx%d+0+0' %(self.photo_canva_w, self.photo_canva_h))  

        # if not self.is_fullcreated:
        #     self.fullscreen_create()
        
        window.cancel_move()
        
        self.photo_con.deiconify()
        self.photo_preview.deiconify()
        self.manga_con.deiconify()
        self.full_con.deiconify()
        self.popup.deiconify()
        
        if window.list_with_img:                  
            self.manga_button2.config(state=tk.NORMAL)
            self.photoalbum_button2.config(state=tk.NORMAL)
            
        else:                        # disable manga mode and photo album mode if only gif/vid
            self.manga_button2.config(state=tk.DISABLED)
            self.photoalbum_button2.config(state=tk.DISABLED)
        
        # multiple screen
        current_winfo_x = window.parent.winfo_x()    # to get current monitor
        
        window_mid_pt = int(int(current_winfo_x) + int(settinglevel.window_width) / 2)    # find the mid point of parent to match window's behaviour
        
        try:
            monitor_info = GetMonitorInfo(MonitorFromPoint((window_mid_pt,0)))   # to get the current monitor based on x,y
        
        except:
            monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))     # error if x,y not existent
            
        monitor_area = monitor_info.get("Monitor")                # full screen area
        # work_area = monitor_info.get("Work")

        # print(monitor_area)
        # print(work_area)
        
        width = monitor_area[2] - monitor_area[0]
        height = monitor_area[3] - monitor_area[1]
        self.mon_x = monitor_area[0]
        self.mon_y = monitor_area[1]
        
        self.popup.geometry("%dx%d+%d+%d" %(width, height, self.mon_x, self.mon_y)) 
        self.full_con.geometry("+%d+%d" % (window.full_w / 2 + self.mon_x - 950 /2, window.full_h - 64 + self.mon_y))
        self.photo_con.geometry("+%d+%d" % (window.full_w / 2 - 1000/2 + self.mon_x, window.full_h - 64 + self.mon_y))
        self.photo_preview.geometry("+%d+%d" % (50 + self.mon_x, window.full_h - 250 + self.mon_y))
        self.manga_con.geometry("+%d+%d" % (window.full_w / 2- 780 /2 + self.mon_x, window.full_h - 64 + self.mon_y))
        
        self.popup.update()
        self.motion()
        
        window.parent.attributes('-topmost', False)
        self.popup.focus_set()    
        window.pic_canvas.delete("all")
        
        try:
            settinglevel.setting_hide()
            settinglevel.enhancer_hide()
        
        except:
            print("failed to hide settings or enhancer")
            logging.info("failed to hide settings or enhancer")
        
        if len(window.fullfilelist) == 0:
            exception_emptypath()
        
        window.stor.stop_storage(False)       

        self.stor.thread_storage = threading.Thread(target = self.stor.backend_storage, args = (window.fileindex,))
        
        self.stor.stop_backend = False
        self.stor.thread_storage.start()    
        
        self.stor.ListPhotoStor = [None] * len(window.fullfilelist)  # clear cache of photoimage
        
        if self.stor.backend_run_photoimage == False and window.check_photoimage(window.fileindex):
            print("start fulllevel thread (PhotoImage)")
            logging.info("start fulllevel thread (PhotoImage)")
            self.stor.thread_storage_photoimage = threading.Thread(target = self.stor.backend_photoimage_storage, args = (window.fileindex,))
            self.stor.thread_storage_photoimage.start()
        
        filepath = window.fullfilelist[window.fileindex] 
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if not window.is_manga_mode and not window.is_photoalbum_mode:
            if file_ext in window.supported_img:                     # full screen mode
                window.ShowIMG_Full(filepath)
            
            else:
                window.after(20, window.ShowANI_Full, filepath) 
                # window.ShowANI_Full(filepath) 
        
    def fullscreen_create(self):
        print("fullscreen_create")
        logging.info("fullscreen_create")
        
        self.is_fullcreated = True

        # GUI of Fullscreen
        self.popup.resizable(False,False)
        self.popup.overrideredirect(1)
        self.popup.geometry("%dx%d+0+0" % (window.full_w, window.full_h))

        self.button_esc = self.popup.bind("<Escape>", self.quit_full)
        self.button1 = self.popup.bind("<Button-1>", self.fullforward)
        self.button3 = self.popup.bind("<Button-3>", self.fullbackward)
        self.wheel = self.popup.bind("<MouseWheel>", self.event_zoom)            # trigger zoom event
        self.button2_click = self.popup.bind('<ButtonPress-2>', self.move_from)
        self.button2_motion = self.popup.bind('<B2-Motion>', self.move_to)
        self.popup.bind("<Up>", self.gif_speedup)
        self.popup.bind("<Down>", self.gif_speeddown)
        self.button_forward = self.popup.bind("<Right>", self.fullforward)
        self.button_backward = self.popup.bind("<Left>", self.fullbackward)
        self.p_button = self.popup.bind("<p>", window.gif_pause)
        self.s_button = self.popup.bind("<s>", fulllevel.start_slide)
        self.a_button = self.popup.bind("<a>", fulllevel.start_photoalbum)
        self.m_button = self.popup.bind("<m>", fulllevel.start_manga)
        self.popup.bind("<a>", fulllevel.start_photoalbum)
        self.popup.bind("<m>", fulllevel.start_manga)
        
        self.popup.bind("<Tab>", settinglevel.enhancer_click)
        self.popup.bind("<q>", window.brightness_increase)
        self.popup.bind("<w>", window.brightness_decrease)
        self.popup.bind("<e>", window.contrast_increase)
        self.popup.bind("<r>", window.contrast_decrease)
        self.popup.bind("<t>", window.sharpness_increase)
        self.popup.bind("<y>", window.sharpness_decrease)
        self.popup.bind("<u>", window.color_increase)
        self.popup.bind("<i>", window.color_decrease)
        
        self.full_con.bind("<Escape>", self.quit_full)
        self.full_con.bind("<MouseWheel>", self.event_zoom)            # trigger zoom event
        self.full_con.bind("<Up>", self.gif_speedup)
        self.full_con.bind("<Down>", self.gif_speeddown)
        self.full_con.bind("<Right>", self.fullforward)
        self.full_con.bind("<Left>", self.fullbackward)
        self.full_con.bind("<p>", window.gif_pause)
        self.s_button_con = self.full_con.bind("<s>", fulllevel.start_slide)
    
        self.pic_canvas = tk.Canvas(self.popup, width = window.full_w, height = window.full_h, highlightthickness = 0)
        self.pic_canvas.pack()
        self.pic_canvas.configure(background='black')
        self.pic_canvas.configure(scrollregion = self.pic_canvas.bbox("all"))
        
        # Controller in fullscreen
        s = ttk.Style()
        s.configure('my.TButton', font=('Arial', 13))
        
        self.full_con.resizable(False,False)
        self.full_con.overrideredirect(1)
        self.full_con.geometry("1025x50+%d+%d" % (window.full_w / 2- 1025 /2, window.full_h - 64))
        
        self.listbox_button2 = ttk.Button(self.full_con, text = "List", style='primary.TButton', command = listlevel.show_listbox, width=8)
        self.listbox_button2.pack(side =tk.LEFT, padx = 5)
        
        self.settings_button2 = ttk.Button(self.full_con, text = "Settings", style='primary.TButton', command = settinglevel.setting_buttonclick, width=8)
        self.settings_button2.pack(side=tk.LEFT,padx= 5)
        
        self.enhancer_button2 = ttk.Button(self.full_con, text = "Enhance", style='primary.TButton', command = settinglevel.enhancer_show, width=8)
        self.enhancer_button2.pack(side=tk.LEFT,padx= 10)

        self.anticlock_button2 = ttk.Button(self.full_con, text= "\u2937", width=3, command= window.anticlockwise, style='my.TButton')
        self.anticlock_button2.pack(side =tk.LEFT, padx = 5)
        
        self.clock_button2 = ttk.Button(self.full_con, text= "\u2936", width=3, command= window.clockwise, style='my.TButton')
        self.clock_button2.pack(side =tk.LEFT, padx = 10)
        
        self.backward_button2 = ttk.Button(self.full_con, text= u"\u2B98", width=3, command= self.fullbackward, style='primary.TButton')
        self.backward_button2.pack(side =tk.LEFT, padx = 10)
        
        self.forward_button2 = ttk.Button(self.full_con, text= u"\u2B9A", width=3, command= self.fullforward, style='primary.TButton')
        self.forward_button2.pack(side =tk.LEFT, padx = 5)
        
        self.quit_button2 = ttk.Button(self.full_con, text= "\u03A7", width=3, style='primary.TButton', command = self.quit_full)
        self.quit_button2.pack(side =tk.RIGHT, padx = 5)
        
        self.manga_button2 = ttk.Button(self.full_con, text= "Manga Mode", width=12, command = self.start_manga, style='primary.TButton')
        self.manga_button2.pack(side =tk.RIGHT, padx = 5)
        
        self.photoalbum_button2 = ttk.Button(self.full_con, text= "Photo Album", width=12, command = self.start_photoalbum, style='primary.TButton')
        self.photoalbum_button2.pack(side =tk.RIGHT, padx = 5)
        
        self.slide_button2 = ttk.Button(self.full_con, text= "Slide Mode", width=12, command = self.start_slide, style='primary.TButton')
        self.slide_button2.pack(side =tk.RIGHT, padx = 10)
        
        # Controller in photo album mode
        self.photo_con.resizable(False,False)
        self.photo_con.overrideredirect(1)
        self.photo_con.geometry("1000x50+%d+%d" % (window.full_w / 2 - 1000/2, window.full_h - 64))
        self.forward_speed = 1
        
        self.listbox_button3 = ttk.Button(self.photo_con, text = "List", style='primary.TButton', command = listlevel.show_listbox, width=8)
        self.listbox_button3.pack(side =tk.LEFT, padx = 5)
        
        self.settings_button3 = ttk.Button(self.photo_con, text = "Settings", style='primary.TButton', command = settinglevel.setting_buttonclick, width=8)
        self.settings_button3.pack(side=tk.LEFT,padx= 5)
        
        self.enhancer_button3 = ttk.Button(self.photo_con, text = "Enhance", style='primary.TButton', command = settinglevel.enhancer_show, width=8)
        self.enhancer_button3.pack(side=tk.LEFT,padx= 10)

        self.anticlock_button3 = ttk.Button(self.photo_con, text= "\u2937", width=3, command= window.anticlockwise, style='my.TButton')
        self.anticlock_button3.pack(side =tk.LEFT, padx = 5)
        
        self.clock_button3 = ttk.Button(self.photo_con, text= "\u2936", width=3, command= window.clockwise, style='my.TButton')
        self.clock_button3.pack(side =tk.LEFT, padx = 10)
        
        self.backward_button3 = ttk.Button(self.photo_con, text= u"\u2B98", width=3, command= self.fullbackward, style='my.TButton')
        self.backward_button3.pack(side =tk.LEFT, padx = 10)
        
        self.forward_button3 = ttk.Button(self.photo_con, text= u"\u2B9A", width=3, command= self.fullforward, style='my.TButton')
        self.forward_button3.pack(side =tk.LEFT, padx = 5)
        
        self.zoomin_button3 = ttk.Button(self.photo_con, text= "+", width=3, command= self.zoomin_photoalbum, style='my.TButton')
        self.zoomin_button3.pack(side =tk.LEFT, padx = 10)
        
        self.zoomout_button3 = ttk.Button(self.photo_con, text= "-", width=3, command= self.zoomout_photoalbum, style='my.TButton')
        self.zoomout_button3.pack(side =tk.LEFT, padx = 5)
        
        self.decreaseforward_button3 = ttk.Button(self.photo_con, text= "<<", width=3, command= self.decrease_forward, style='my.TButton')
        self.decreaseforward_button3.pack(side =tk.LEFT, padx = 10)
        
        self.increaseforward_button3 = ttk.Button(self.photo_con, text= ">>", width=3, command= self.increase_forward, style='my.TButton')
        self.increaseforward_button3.pack(side =tk.LEFT, padx = 5)
        
        self.quit_button3 = ttk.Button(self.photo_con, text= "\u03A7", width=3, style='my.TButton', command = self.quit_photoalbum)
        self.quit_button3.pack(side =tk.RIGHT, padx = 5)
        
        self.auto_button3 = ttk.Button(self.photo_con, text= "\u23ef", width=6, style='my.TButton', command = self.pause_auto)
        self.auto_button3.pack(side =tk.RIGHT, padx = 15)
        
        # Preview Canva in photo album mode
        self.photo_canva_w = 200
        self.photo_canva_h = 200
        self.photo_preview.resizable(False,False)
        self.photo_preview.overrideredirect(1)
        self.photo_preview.geometry('%dx%d+0+0' %(self.photo_canva_w, self.photo_canva_h))    
        
        self.photo_canvas = tk.Canvas(self.photo_preview, width = self.photo_canva_w, height = self.photo_canva_h, highlightthickness = 0)
        self.photo_canvas.pack()
        self.photo_canvas.configure(background='black')
        self.photo_canvas.configure(scrollregion = self.photo_canvas.bbox("all"))
        self.photo_canvas.bind('<Button-1>', self.photo_preview_predrag)
        self.photo_canvas.bind('<B1-Motion>', self.photo_preview_drag)
        
        # gripper for resizing
        self.photo_canvas_grip = ttk.Sizegrip(self.photo_preview)
        self.photo_canvas_grip.place(relx=1.0, rely=1.0, anchor="se")
        self.photo_canvas_grip.bind("<B1-Motion>", self.photo_preview_resize)
        self.photo_canvas_grip.bind("<ButtonRelease-1>", self.photo_preview_event_resize)
        
        # Controller in manga mode
        self.manga_con.resizable(False,False)
        self.manga_con.overrideredirect(1)
        self.manga_con.geometry("780x50+%d+%d" % (window.full_w / 2- 780 /2, window.full_h - 64))
        
        self.listbox_button4 = ttk.Button(self.manga_con, text = "List", style='primary.TButton', command = listlevel.show_listbox, width=8)
        self.listbox_button4.pack(side =tk.LEFT, padx = 5)
        
        self.settings_button4 = ttk.Button(self.manga_con, text = "Settings", style='primary.TButton', command = settinglevel.setting_buttonclick, width=8)
        self.settings_button4.pack(side=tk.LEFT,padx= 15)
        
        self.fastbackward_button4 = ttk.Button(self.manga_con, text= u"\u290a", style="my.TButton", width=3, command= self.backward_manga)
        self.fastbackward_button4.pack(side =tk.LEFT, padx = 5)
        
        self.fastforward_button4 = ttk.Button(self.manga_con, text= "\u290b", style="my.TButton", width=3, command= self.forward_manga)
        self.fastforward_button4.pack(side =tk.LEFT, padx = 10)

        self.backward_button4 = ttk.Button(self.manga_con, text= u"\u2191", width=3, command= self.keyscroll_backward_manga, style='my.TButton')
        self.backward_button4.pack(side =tk.LEFT, padx = 10)
        
        self.forward_button4 = ttk.Button(self.manga_con, text= u"\u2193", width=3, command= self.keyscroll_forward_manga, style='my.TButton')
        self.forward_button4.pack(side =tk.LEFT, padx = 5)
        
        self.decreaseforward_button4 = ttk.Button(self.manga_con, text= "<<", width=3, command= self.decrease_forward, style='my.TButton')
        self.decreaseforward_button4.pack(side =tk.LEFT, padx = 10)
        
        self.increaseforward_button4 = ttk.Button(self.manga_con, text= ">>", width=3, command= self.increase_forward, style='my.TButton')
        self.increaseforward_button4.pack(side =tk.LEFT, padx = 5)
        
        self.quit_button4 = ttk.Button(self.manga_con, text= "\u03A7", width=3, style='my.TButton', command = self.quit_manga)
        self.quit_button4.pack(side =tk.RIGHT, padx = 5)
        
        self.auto_button4 = ttk.Button(self.manga_con, text= "\u23ef", width=6, style='my.TButton', command = self.auto_scrollmanga)
        self.auto_button4.pack(side =tk.RIGHT, padx = 15)
        
        self.motion1 = self.popup.bind("<Motion>", self.motion)                          # control appearance controller

        self.popup.withdraw()                                 # close full screen and controller
        self.full_con.withdraw()
        self.photo_con.withdraw()
        self.photo_preview.withdraw()
        self.manga_con.withdraw()
        
    def photo_preview_predrag(self, event):
        print("drag_photo_preview")    
        logging.info("drag_photo_preview")
        
        self.photo_preview_offsetx = event.x
        self.photo_preview_offsety = event.y
        
    def photo_preview_drag(self, event):
        
        x = self.photo_preview.winfo_x() + event.x - self.photo_preview_offsetx
        y = self.photo_preview.winfo_y() + event.y - self.photo_preview_offsety
        
        self.photo_preview.geometry('+{x}+{y}'.format(x=x,y=y))

    def photo_preview_resize(self, event):
        print("photo_preview_resize")
        logging.info("photo_preview_resize")
        
        time.sleep(0.1)                      # reduce the frequency of photo_preview resize to avoid crash
        
        self.photo_preview_auto_adjust = False
        
        x1 = self.photo_preview.winfo_pointerx()
        y1 = self.photo_preview.winfo_pointery()
        x0 = self.photo_preview.winfo_rootx()
        y0 = self.photo_preview.winfo_rooty()
        
        fulllevel.photo_canva_w = max(100, x1-x0)
        fulllevel.photo_canva_h = max(100, y1-y0)
        
        self.photo_preview.geometry("%sx%s" %(fulllevel.photo_canva_w, fulllevel.photo_canva_h)) # for resizing the window
        self.photo_canvas.configure(width = fulllevel.photo_canva_w, height = fulllevel.photo_canva_h)
    
    def photo_preview_event_resize(self, event):
        print("photo_preview_event_resize")
        logging.info("photo_preview_event_resize")
        
        pic_path = window.fullfilelist[window.fileindex]
        window.ShowIMG_Preview(pic_path, False, False)
        
    def fullforward(self, event=None):                           # full screen mode
        print("fullforward")    
        logging.info("fullforward")
        
        self.pic_canvas.delete("all")
        
        self.timer = settinglevel.default_timer 
        
        if event is not None and window.is_slide_check:
            slide_forward = True
        
        else:
            slide_forward = False
            
        try:
            window.forward(slide_forward)
        
        except RecursionError as e:                           # force quit slide or photoalbum to fix recursion error
            print("RecursionError : ", e)
            logging.error("RecursionError: maximum recursion depth exceeded while calling a Python object")
            
            if window.is_slide_check and not window.is_photoalbum_mode:
                self.quit_slide()
                window.forward()
            
            elif window.is_slide_check and window.is_photoalbum_mode:
                self.quit_photoalbum()
        
        # except Exception as e:                 # try to fix the slide mode crash issue
        #     print("UnknownError : ", e)
        #     logging.error("UnknownError : %s" %e)
            
        #     if window.is_slide_check and not window.is_photoalbum_mode:
        #         # self.quit_slide()
        #         window.forward()
            
        #     elif window.is_slide_check and window.is_photoalbum_mode:
        #         self.quit_photoalbum()
    
    def fullbackward(self, event=None):                           # full screen mode
        print("fullbackward")  
        logging.info("fullbackward")
        
        self.pic_canvas.delete("all")
    
        self.timer = settinglevel.default_timer
        
        if event is not None and window.is_slide_check:
            slide_forward = True
        
        else:
            slide_forward = False
        
        window.backward(slide_forward)
        
    def back_simple_full(self):           # from slide mode, Photo Album, manga to simple fullscreen
        print("back_simple_full")
        logging.info("back_simple_full")
        
        try:
            self.popup.unbind("<s>",fulllevel.s_button2)
            self.full_con.unbind("<s>",fulllevel.s_button_con2)
            
        except:
            print("failed to unbind s")
            logging.info("failed to unbind s")
        
        self.s_button = self.popup.bind("<s>", fulllevel.start_slide)
        self.a_button = self.popup.bind("<a>", fulllevel.start_photoalbum)
        self.m_button = self.popup.bind("<m>", fulllevel.start_manga)
        
        self.s_button_con = self.full_con.bind("<s>", fulllevel.start_slide)
        
        window.is_slide_check = False
        window.is_photoalbum_mode = False
        window.is_manga_mode = False
        window.is_auto_manga = False
        fulllevel.timer = settinglevel.default_timer                       # reset timer
        
        fulllevel.popup.update()
        
        fulllevel.popup.focus_set()
        
        window.cancel_move()
        
        fulllevel.pic_canvas.delete("all")                    # remove existing image
        
        pic_path = window.fullfilelist[window.fileindex]
        
        file_ext = os.path.splitext(pic_path)[1].lower()      # separate file name and extension
        
        try:
            is_fullcached = fulllevel.stor.ListStor[window.fileindex].get("is_cached", False)
        
        except AttributeError:
            is_fullcached = False 
        
        if file_ext in window.supported_img:     
            window.ShowIMG_Full(pic_path, is_fullcached)                    # back to simple full screen
        
        elif file_ext in (window.supported_ani | window.supported_vid):
            window.ShowANI_Full(pic_path, is_fullcached)                    # back to simple full screen
    
    def quit_full(self, event=None):                              # from full screen mode to window mode
        print("quit_full")
        logging.info("quit_full")    
    
        # window.is_slide_check = False 
        window.is_full_mode = False
        window.hide_gif_con = False
        
        fulllevel.popup.withdraw()                                 # close full screen and controller
        fulllevel.full_con.withdraw()
        fulllevel.photo_con.withdraw()
        fulllevel.photo_preview.withdraw()
        fulllevel.manga_con.withdraw()
        
        fulllevel.pic_canvas.delete("all")
        
        try:
            settinglevel.setting_hide()
            settinglevel.enhancer_hide()
        
        except:
            print("failed to hide setting or enhancer")
            logging.info("failed to hide setting or enhancer")
        
        if window.is_slide_check:
            try:
                fulllevel.quit_slide()
                
            except:
                print("failed to quit slide")
                logging.info("failed to quit slide")
            
        window.is_slide_check = False 
        
        # listlevel.hide_listbox()
        
        filepath = str(window.folder_entry.get())              # refresh root window
        file_ext = os.path.splitext(filepath)[1].lower()                  
        fulllevel.stor.stop_storage(False)  
        
        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
        
        window.stor.stop_backend = False
        window.stor.thread_storage.start()
        
        if file_ext in window.supported_img:
            window.ShowIMG(filepath)
        
        elif file_ext in (window.supported_ani | window.supported_vid):
            window.ShowANI(filepath)                
        
    def motion(self, event=None):                      # in full screen
    
        self.popup.config(cursor="")
        
        if window.is_full_mode and not window.is_stop_ani and window.gif_con.state() == "withdrawn":
            window.gif_con.deiconify()
            window.hide_gif_con = False
        
        if event is not None:
            x = event.x + self.mon_x                       # mouse pointer location, adjusted by multi screen
            y = event.y + self.mon_y                       # mouse pointer location, adjusted by multi screen
        
        else:
            x = self.mon_x
            y = self.mon_y
    
        if y > window.full_h - 70:
            
            if window.is_photoalbum_mode:
                self.photo_con.focus_set()                          # show controller
                
                self.photo_preview_visible = True

                if not settinglevel.is_alwayspreview and not self.con_visible:
                    pic_path = window.fullfilelist[window.fileindex]
                    window.ShowIMG_Preview(pic_path, False, False)
                
                self.photo_preview.focus_set()
                
            elif window.is_manga_mode:
                self.manga_con.focus_set()                          # show controller
                
                self.photo_preview_visible = True

                if not settinglevel.is_alwayspreview and not self.con_visible:
                    pic_path = window.fullfilelist[window.fileindex]
                    window.ShowIMG_Preview(pic_path, False, False)
                 
                self.photo_preview.focus_set()
                
            else:
                self.full_con.focus_set()                          # show controller
                
            self.con_visible = True                         # to avoid loading showimg_preview again and again
            
        if y < window.full_h - 70:
            self.con_visible = False
            
            self.popup.focus_set()                           # hide controller
            
            if not settinglevel.is_alwayspreview:
                self.photo_preview_visible = False
            
            window.thread_hidecursor1 = window.after(50, self.hide_cursor_precheck, x, y)    # hide cursor
    
    def hide_cursor_precheck(self, x, y):
        # 2-stage hide_cursor to fix the issue of spamming error when quit full mode and close program immediately
        
        precheck_x, precheck_y = self.popup.winfo_pointerxy()[0], self.popup.winfo_pointerxy()[1]

        if (precheck_x, precheck_y) == (x,y):
            window.thread_hidecursor2 = window.after(2500, self.hide_cursor, precheck_x, precheck_y)    # hide cursor
                
    def hide_cursor(self, x, y): 

        try:
            if self.popup.winfo_pointerxy() == (x,y):
                self.popup.config(cursor="none")
                
                if window.is_full_mode and not window.is_stop_ani and window.gif_con.state() == "normal":
                    window.gif_con.withdraw()
                    window.hide_gif_con = True
                
        except:
            pass

# In[Auto slide mode]
    
    def start_slide(self, event=None, forward=False):                        # slide mode or Photo Album mode
        print("start_slide")
        logging.info("start_slide")
        
        if not forward:
            self.slide_button2.config(text = "Stop Slide", command=self.quit_slide)
            self.photoalbum_button2.config(state=tk.DISABLED)
            self.manga_button2.config(state=tk.DISABLED)
            self.popup.unbind("<m>", self.m_button)
            self.popup.unbind("<a>", self.a_button)
            self.popup.unbind("<s>", self.s_button)
            self.s_button2 = self.popup.bind("<s>", self.quit_slide)
            
            self.full_con.unbind("<s>", self.s_button_con)
            self.s_button_con2 = self.full_con.bind("<s>", self.quit_slide)
            
            if not window.is_photoalbum_mode:                          # slide mode
                self.popup.unbind("<Button-1>", self.button1)
                self.popup.unbind("<Button-3>", self.button3)
                self.left_slide_button = self.popup.bind("<Button-1>", self.leftclick_slide)
                self.right_slide_button = self.popup.bind("<Button-3>", self.rightclick_slide)
            
        window.is_slide_check = True
        window.is_timer_pause = False
        
        self.timer = settinglevel.default_timer
        
        filepath = window.fullfilelist[window.fileindex] 
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if not window.is_photoalbum_mode:                          # slide mode
            # self.popup.unbind("<Button-1>", self.button1)
            # self.popup.unbind("<Button-3>", self.button3)
            # self.left_slide_button = self.popup.bind("<Button-1>", self.leftclick_slide)
            # self.right_slide_button = self.popup.bind("<Button-3>", self.rightclick_slide)
        
            if file_ext in window.supported_img:  
                if fulllevel.stor.ListStor[window.fileindex] is not None:
                    is_fullcached = True      
                
                else:
                    is_fullcached = False
                    
                window.ShowIMG_Full(filepath, is_fullcached, False, True)
            
            else:
                try:
                    is_fullcached = fulllevel.stor.ListStor[window.fileindex].get("is_cached", False)
                    
                except AttributeError:
                    is_fullcached = False 
                    
                window.ShowANI_Full(filepath, is_fullcached)
    
    def leftclick_slide(self, event):
        print("leftclick_slide")
        logging.info("leftclick_slide")
        
        self.timer = self.timer - settinglevel.default_timer - settinglevel.gif_loop
        window.is_skip_ani = True
        
    def rightclick_slide(self, event):
        print("rightclick_slide")
        logging.info("rightclick_slide")
        
        self.timer = self.timer + settinglevel.default_timer + settinglevel.gif_loop + 1000
        window.is_skip_ani = True
    
    def countdown_timer(self):                       # ShowIMG_full only, to fix "crash in slide mode when click fast for 200+ times"
        print("countdown_timer")
        logging.info("countdown_timer")
        
        time0 = time.perf_counter() + 100            # make negative value for first frame

        while self.check_timer(False) >= 0 and window.is_slide_check: # check and control timer
            self.popup.update()
            
            if not window.is_slide_check:
                break

            if self.timer > settinglevel.default_timer and window.is_slide_check:    # backward
                break
            
            time_adj = max(0, time.perf_counter() - time0)
            
            try:
                time.sleep(1 / settinglevel.timer_frame - time_adj)                     # maintain frame
            
            except ValueError:        # no sleep if negative value
                pass
                
            time0 = time.perf_counter()
        
        # if self.timer > settinglevel.default_timer and window.is_slide_check:    # forward
        #     self.fullbackward()
        #     return None
        
        # if self.timer < 0 and window.is_slide_check:    # forward
        #     self.fullforward()
        
        if window.is_slide_check:
            if self.timer > settinglevel.default_timer:    # forward
                self.fullbackward()
            
            else:
                self.fullforward()
            
    def check_timer(self, is_ani, duration=None, gif_loop_override=False):         # timer in slide mode or Photo Album mode   
        
        #print("timer:", format(timer, ".3f"), end= " ")
        #logging.info("timer: %s", timer)
        
        if not is_ani:                                            # from ShowIMG_Full and ShowIMG_Fullphotoalbum
            self.timer = self.timer - 1 / settinglevel.timer_frame * self.forward_speed
            #print(self.timer)
            return self.timer
            
        else:                                                      # from ShowANI_Full
            if settinglevel.random_gifloop and not gif_loop_override:                        
                rad = random.random()
                percentage = 0.15
                
                # timer = gif_loop
                if rad > (1 - percentage):                                      # 15% -2; 70% -1; 15% -0
                    self.timer = max(0, self.timer - 2)                   
                    
                elif rad > percentage:
                    self.timer = self.timer - 1
                    
                else:
                    self.timer = self.timer - 0
            
            else:
                self.timer = self.timer - 1
            
            # print(self.timer)
            return self.timer
        
    def quit_slide(self, event=None):                                              # slide mode and Photo Album mode
        print("quit_slide")
        logging.info("quit_slide")
        
        self.slide_button2.config(text = "Slide Mode", command=self.start_slide)
        self.photoalbum_button2.config(state = tk.NORMAL)
        self.manga_button2.config(state = tk.NORMAL)
        
        if not window.is_photoalbum_mode:                            # slide mode
            self.popup.unbind("<Button-1>", self.left_slide_button)
            self.popup.unbind("<Button-3>", self.right_slide_button)

        self.button1 = self.popup.bind("<Button-1>", self.fullforward)
        self.button3 = self.popup.bind("<Button-3>", self.fullbackward)
        
        self.back_simple_full()
        
# In[Photo Album Mode]
    
    def start_photoalbum(self, event=None):                           # Photo Album mode
        print("start_photoalbum")
        logging.info("start_photoalbum")
        
        if not window.list_with_img:                     # prevent entering photo album mode if only gif/vid file
            print("no image file in the list")
            logging.info("no image file in the list")
            return None
        
        try:
            settinglevel.setting_hide()
            settinglevel.enhancer_hide()
        
        except:
            print("failed to hide setting or enhancer")
            logging.info("failed to hide setting or enhancer")
        
        # listlevel.hide_listbox()
        window.cancel_move()

        self.popup.unbind("<Escape>", self.button_esc)
        self.popup.unbind("<MouseWheel>", self.wheel)
        self.popup.unbind("<Button-1>", self.button1)
        self.popup.unbind("<Button-3>", self.button3)
        self.popup.unbind("<Right>", self.button_forward)
        self.popup.unbind("<Left>", self.button_backward)
        self.popup.unbind("<p>", self.p_button)
        
        self.pause_button = self.popup.bind("<Button-1>", self.pause_auto)
        self.pause_button2 = self.popup.bind("<p>", self.pause_auto)
        self.updown_wheel = self.popup.bind("<MouseWheel>", self.wheel_photoalbum)
        self.esc_quit_photoalbum = self.popup.bind("<Escape>", self.quit_photoalbum)
        self.backward_button_photoalbum = self.popup.bind("<Up>", self.backward_photoalbum)
        self.forward_button_photoalbum = self.popup.bind("<Down>", self.forward_photoalbum)
        self.clockwise_button_photoalbum = self.popup.bind("<Right>", window.clockwise)
        self.anticlockwise_button_photoalbum = self.popup.bind("<Left>", window.anticlockwise)
        self.increase_forward_photoalbum = self.popup.bind("<x>", self.increase_forward)
        self.decrease_forward_photoalbum = self.popup.bind("<z>", self.decrease_forward)
        self.forward_speed = 1
        
        self.photo_con.bind("<p>", self.pause_auto)
        self.photo_con.bind("<MouseWheel>", self.wheel_photoalbum)
        self.photo_con.bind("<Escape>", self.quit_photoalbum)
        self.photo_con.bind("<Up>", self.backward_photoalbum)
        self.photo_con.bind("<Down>", self.forward_photoalbum)
        self.photo_con.bind("<Right>", window.clockwise)
        self.photo_con.bind("<Left>", window.anticlockwise)
        self.photo_con.bind("<x>", self.increase_forward)
        self.photo_con.bind("<z>", self.decrease_forward)

        fulllevel.stor.pause_backend = True
        window.is_photoalbum_mode = True
        window.is_slide_check = True
        
        self.timer = settinglevel.default_timer
        
        self.popup.focus_set()
        
        if settinglevel.is_alwayspreview:
            self.photo_preview.deiconify()
            self.photo_preview.attributes('-topmost', True)
            self.photo_preview_visible = True
        
        else:
            self.photo_preview_visible = False
        
        self.pic_canvas.delete("all") 
        
        self.photoalbum = Storage("photoalbum")   
        self.photoalbum.create_reset_storage()
        
        self.photoalbum.thread_storage = threading.Thread(target = self.photoalbum.backend_storage, args = (window.fileindex,))
        
        self.photoalbum.stop_backend = False
        self.photoalbum.thread_storage.start()  
        
        self.start_slide()                                 # use common definition as slide mode
        
        self.popup.unbind("<s>", self.s_button2)
        
        pic_path = window.fullfilelist[window.fileindex]
        file_ext = os.path.splitext(pic_path)[1].lower()      # separate file name and extension
        
        if file_ext in window.supported_img:
            self.ShowIMG_FullPhotoalbum(pic_path, True)           # Photo Album mode
            
            if self.photo_preview_visible:                    # skip this if there is no preview
                window.ShowIMG_Preview(pic_path, False, False)
                
            # self.ShowIMG_FullPhotoalbum(pic_path)           # Photo Album mode
            window.after(10, self.ShowIMG_FullPhotoalbum, pic_path)   # Photo Album mode
            
        elif file_ext in (window.supported_ani | window.supported_vid):
            # window.ShowIMG_Preview(pic_path, True, False)
            # self.ShowANI_Full(pic_path)                    # same as full mode for gif
            self.fullforward()
           
    def quit_photoalbum(self, event=None):                          # Photo Album mode
        print("quit_photoalbum")    
        logging.info("quit_photoalbum")
 
        self.popup.unbind("<Button-1>", self.pause_button)
        self.popup.unbind("<p>", self.pause_button2)
        self.popup.unbind("<MouseWheel>", self.updown_wheel)
        self.popup.unbind("<Escape>", self.esc_quit_photoalbum)
        self.popup.unbind("<Up>", self.backward_button_photoalbum)
        self.popup.unbind("<Down>", self.forward_button_photoalbum)
        self.popup.unbind("<Right>", self.clockwise_button_photoalbum)
        self.popup.unbind("<Left>", self.anticlockwise_button_photoalbum)
        self.popup.unbind("<z>", self.decrease_forward_photoalbum)
        self.popup.unbind("<x>", self.increase_forward_photoalbum)
        self.p_button = self.popup.bind("<p>", window.gif_pause)
        
        #self.motion1 = self.popup.bind("<Motion>", self.motion)                          # control appearance controller 
        self.button_esc = self.popup.bind("<Escape>", self.quit_full)
        self.wheel = self.popup.bind("<MouseWheel>", self.event_zoom)  
        self.button_forward = self.popup.bind("<Right>", self.fullforward)
        self.button_backward = self.popup.bind("<Left>", self.fullbackward)
        
        window.photoalbum_zoom_factor = 1
        
        settinglevel.setting_hide()
        settinglevel.enhancer_hide()
        # listlevel.hide_listbox()
        fulllevel.photo_con.attributes('-topmost', False)
        fulllevel.photo_preview.attributes('-topmost', False)
        fulllevel.photo_preview.withdraw()

        fulllevel.stor.pause_backend = False
        
        self.quit_slide()
        
        self.photoalbum.stop_storage(True)
        del self.photoalbum
        
    def move_photoalbum(self, w_h):
        
        photoalbum_zoom_factor = window.photoalbum_zoom_factor
        time_adj = 0                                    # for timer accurancy
        #time0 = time.perf_counter() + 100
        window.event_zoom_ongoing = False
        
        window.stop_album = False
        
        if w_h == "h":
            h_diff = fulllevel.move_diff
            w_diff = 0
        
        else:
            h_diff = 0
            w_diff = fulllevel.move_diff
        
        while window.is_slide_check:
            
            while window.check_timer_pause():            # pause
                fulllevel.popup.update()
                if photoalbum_zoom_factor != window.photoalbum_zoom_factor:
                    break
                
                if window.stop_album:
                    break
                
            if photoalbum_zoom_factor != window.photoalbum_zoom_factor:
                break
            
            if window.stop_album:
                break
          
            fulllevel.slide_timer = float(fulllevel.check_timer(False))
            #print(fulllevel.slide_timer)
        
            fulllevel.pic_canvas.move(fulllevel.zoom_pic, w_diff * self.forward_speed, h_diff * self.forward_speed)
            
            fulllevel.popup.update()
            
            if fulllevel.slide_timer >= settinglevel.default_timer + 2 and window.is_slide_check: # backward
                break
                # fulllevel.fullbackward()
            
            if fulllevel.slide_timer < 0 and window.is_slide_check:  # forward
                break
                # fulllevel.fullforward()
            
            #time_adj = max(0, time.perf_counter() - time0)
            #print("time adj: ", time_adj)
            #print(max(0.001, 1 / settinglevel.timer_frame - time_adj))
            time.sleep(max(0.001, 1 / settinglevel.timer_frame - time_adj))
            #time0 = time.perf_counter()
            
        if window.is_slide_check and not window.stop_album:
            window.stop_album = True     # to avoid hotkey click while loading next slide
            
            if fulllevel.slide_timer >= settinglevel.default_timer + 2 and window.is_slide_check: # backward
                fulllevel.fullbackward()
            
            if fulllevel.slide_timer < 0 and window.is_slide_check:  # forward
                fulllevel.fullforward()
                
    def pause_auto(self, event=None):                              # Photo Album mode
        print("pause_auto")
        logging.info("pause_auto")
        
        if not window.is_timer_pause:
            window.is_timer_pause = True
        
        else:
            window.is_timer_pause = False
               
    def wheel_photoalbum(self, event):                      # Photo Album mode
        print("wheel_photoalbum")
        logging.info("wheel_photoalbum")
        
        if event.delta > 1:                           # scroll up
            self.timer = self.timer + settinglevel.scroll_multiplier           # add timer
            
            if window.full_w/self.img_w >= window.full_h/self.img_h:
                self.pic_canvas.move(self.zoom_pic, 0, fulllevel.move_diff * settinglevel.timer_frame * - settinglevel.scroll_multiplier)  # move up
                
            else:
                self.pic_canvas.move(self.zoom_pic, fulllevel.move_diff * settinglevel.timer_frame * - settinglevel.scroll_multiplier, 0)
                
        else:                                          # scroll down
            self.timer = self.timer - settinglevel.scroll_multiplier                          # reduce timer
            
            if window.full_w/self.img_w >= window.full_h/self.img_h:
                self.pic_canvas.move(self.zoom_pic, 0, fulllevel.move_diff * settinglevel.timer_frame * settinglevel.scroll_multiplier)  # move down
            
            else:
                self.pic_canvas.move(self.zoom_pic, fulllevel.move_diff * settinglevel.timer_frame * settinglevel.scroll_multiplier, 0)
        
    def forward_photoalbum(self, event=None):
        print("forward_photoalbum")
        logging.info("forward_photoalbum")
        
        if not window.stop_album:
            fulllevel.slide_timer = -1

    def backward_photoalbum(self, event=None):
        print("backward_photoalbum")
        logging.info("backward_photoalbum")
        
        fulllevel.slide_timer = settinglevel.default_timer + 100
        
    def zoomin_photoalbum(self, event=None):
        print("zoomin_photoalbum")
        logging.info("zoomin_photoalbum")
        
        if not window.event_zoom_ongoing:         # can't run until the previous zoom has been finished
            window.event_zoom_ongoing = True
            
            if window.photoalbum_zoom_factor < 0.6:
                factor_increase = 0.05
            else:
                factor_increase = 0.1
                
            window.photoalbum_zoom_factor = round(window.photoalbum_zoom_factor + factor_increase, 2)
            window.cancel_move()
            
            self.photoalbum.stop_storage(True)
            
            fulllevel.photoalbum.pause_backend = False
                        
            print("start photoalbum thread")
            logging.info("start photoalbum thread")
            fulllevel.photoalbum.thread_storage = threading.Thread(target = fulllevel.photoalbum.backend_storage, args = (window.fileindex,))
            
            fulllevel.photoalbum.stop_backend = False
            fulllevel.photoalbum.thread_storage.start()

            filepath = str(window.folder_entry.get())
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext in window.supported_img:                 # skip gif                          
                window.after(10, self.ShowIMG_FullPhotoalbum, filepath)
            
    def zoomout_photoalbum(self, event=None):
        print("zoomout_photoalbum")
        logging.info("zoomout_photoalbum")
        
        if not window.event_zoom_ongoing:         # can't run until the previous zoom has been finished
            photoalbum_zoom_factor = window.photoalbum_zoom_factor   # previous value
            if photoalbum_zoom_factor <= 0.6:
                factor_decrease = 0.05
            else:
                factor_decrease = 0.1
                
            window.photoalbum_zoom_factor = round(max(0.4, window.photoalbum_zoom_factor - factor_decrease), 2)
            
            if photoalbum_zoom_factor != window.photoalbum_zoom_factor:   # no reset if zoom factor unchanged
                window.event_zoom_ongoing = True
                window.cancel_move()
                
                self.photoalbum.stop_storage(True)
                
                fulllevel.photoalbum.pause_backend = False
                        
                print("start photoalbum thread")
                logging.info("start photoalbum thread")
                fulllevel.photoalbum.thread_storage = threading.Thread(target = fulllevel.photoalbum.backend_storage, args = (window.fileindex,))
                
                fulllevel.photoalbum.stop_backend = False
                fulllevel.photoalbum.thread_storage.start()
                
                filepath = str(window.folder_entry.get())
                file_ext = os.path.splitext(filepath)[1].lower()
                
                if file_ext in window.supported_img:                 # skip gif                          
                    window.after(10, self.ShowIMG_FullPhotoalbum, filepath)
                    
    def increase_forward(self, event=None):        # photo album mode and manga mode
        
        if self.forward_speed >= 1:
            self.forward_speed = round(min(4, self.forward_speed + 0.25), 2)
        
        else:
            self.forward_speed = round(self.forward_speed + 0.15, 2)
        
        print("increase_forward : %s" %self.forward_speed)
        logging.info("increase_forward : %s" %self.forward_speed)  
        
    def decrease_forward(self, event=None):        # photo album mode and manga mode
        
        if self.forward_speed > 1:
            self.forward_speed = round(self.forward_speed - 0.25, 2)
            
        else:
            self.forward_speed = round(max(0.1, self.forward_speed - 0.15), 2)
        
        print("decrease_forward : %s" %self.forward_speed)
        logging.info("decrease_forward : %s" %self.forward_speed) 
        
# In[Manga Mode]
    
    def start_manga(self, event=None):
        print("start_manga")
        logging.info("start_manga")

        if not window.list_with_img:            # prevent entering manga mode if only gif/vid file
            print("no image file in the list")
            logging.info("no image file in the list")
            return None        
        
        # check if next image has been downloaded for web mode
        i = 1
        while True:
            window.next_mangaindex = window.fileindex + i
            
            if window.next_mangaindex == len(window.fullfilelist):
                window.next_mangaindex = i - 1
                
            pic_path = window.fullfilelist[window.next_mangaindex]
            file_ext = os.path.splitext(pic_path)[1].lower()
            
            if file_ext in window.supported_img:
                break
            
            else:
                i = i + 1
        
        if not os.path.isfile(window.fullfilelist[window.next_mangaindex]):
            print("next image isn't ready yet")
            logging.info("next image isn't ready yet")
            return None
            
        try:
            settinglevel.setting_hide()
            settinglevel.enhancer_hide()
        
        except:
            print("failed to hide setting or enhancer")
            logging.info("failed to hide setting or enhancer")
        
        # listlevel.hide_listbox()
        window.cancel_move()
        
        if settinglevel.is_alwayspreview:
            self.photo_preview.attributes('-topmost', True)
            self.photo_preview_visible = True
        
        else:
            self.photo_preview_visible = False
        
        self.popup.unbind("<a>", self.a_button)
        self.popup.unbind("<m>", self.m_button)
        self.popup.unbind("<s>", self.s_button)
        self.popup.unbind("<Button-1>", self.button1)
        self.popup.unbind("<Button-3>", self.button3)
        self.popup.unbind("<Escape>", self.button_esc)
        self.popup.unbind("<MouseWheel>", self.wheel)
        self.popup.unbind("<Right>", self.button_forward)
        self.popup.unbind("<Left>", self.button_backward)
        self.popup.unbind("<p>", self.p_button)
        self.popup.unbind("<ButtonPress-2>", self.button2_click)
        self.popup.unbind("<B2-Motion>", self.button2_motion)

        self.auto_button = self.popup.bind("<Button-1>", self.auto_scrollmanga)
        self.auto_button2 = self.popup.bind("<p>", self.auto_scrollmanga)
        self.updown_wheel_manga = self.popup.bind("<MouseWheel>", self.scroll_manga)
        self.esc_quit_manga = self.popup.bind("<Escape>", self.quit_manga)
        self.backward_button_manga = self.popup.bind("<Up>", self.backward_manga)
        self.forward_button_manga = self.popup.bind("<Down>", self.forward_manga)
        self.increase_forward_manga = self.popup.bind("<x>", self.increase_forward)
        self.decrease_forward_manga = self.popup.bind("<z>", self.decrease_forward)
        
        self.manga_con.bind("<p>", self.auto_scrollmanga)
        self.manga_con.bind("<MouseWheel>", self.scroll_manga)
        self.manga_con.bind("<Escape>", self.quit_manga)
        self.manga_con.bind("<Up>", self.backward_manga)
        self.manga_con.bind("<Down>", self.forward_manga)
        self.manga_con.bind("<x>", self.increase_forward)
        self.manga_con.bind("<z>", self.decrease_forward)
        
        window.is_stop_ani = True
        window.is_manga_mode = True
        window.is_auto_manga = False
        fulllevel.stor.pause_backend = True
        self.forward_speed = 1
        window.rotate_degree = 0
        
        self.pic_canvas.delete("all") 
        self.popup.focus_set()
        
        while True:
          filepath = window.fullfilelist[window.fileindex] 
          file_ext = os.path.splitext(filepath)[1].lower()
          if file_ext in window.supported_img:
              break
          
          else:
              window.fileindex = window.fileindex + 1
        
        self.manga = Storage("manga")   
        self.manga.create_reset_storage()
        
        self.manga.thread_storage = threading.Thread(target = self.manga.backend_storage, args = (window.fileindex,))
        
        self.manga.stop_backend = False
        self.manga.thread_storage.start()  
        
        '''
           w1
           w2
           w3
                                 |  pre2_mangaindex
        h1                                                     
          [manga_top] resized_h1 |  pre_mangaindex                 
        h2                                                   0             full_w
          [manga_mid] resized_h2 |  mangaindex                 [pic_canvas]
        h3                                               full_h
          [manga_bot] resized_h3 |  next_mangaindex
        h4  
                                 |  next2_mangaindex
        '''
        
        self.h2 = 0               
        self.show_manga_top()
        self.show_manga_mid()                                  
        self.h1 = 0 - self.resized_h1
        self.h3 = 0 + self.resized_h2
        self.show_manga_bot()
            
        self.h4 = 0 + self.resized_h2 + self.resized_h3
    
    def show_manga_top(self):
        print("show_manga_top")
        logging.info("show_manga_top")
        
        # 1st image
        i = 1
        while True:
            window.pre_mangaindex = window.fileindex - i
            
            if window.pre_mangaindex < 0:                          # back to end
                window.pre_mangaindex = len(window.fullfilelist) - i
                
            pic_path = window.fullfilelist[window.pre_mangaindex]
            
            if not os.path.isfile(pic_path):    # for web mode
                pic_path = window.ico_path      # use ico image to fake the top image
            
            file_ext = os.path.splitext(pic_path)[1].lower()
            if file_ext in window.supported_img:
                break
          
            else:
                i = i + 1
            
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        if self.manga.ListStor[window.pre_mangaindex] is not None:
            self.resized_h1 = self.manga.ListStor[window.pre_mangaindex][1]
            resize_img = self.manga.ListStor[window.pre_mangaindex][0]
            globals()['image_%s' % window.pre_mangaindex] = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
            
        else:
            try:
                img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
            
            except FileNotFoundError:
                exception_filenotfound()
                        
            img_w, img_h = img.size
            
            resize_scale = window.full_w / img_w * settinglevel.manga_resize               # calculate the resize ratio, maintaining height-width scale
            self.resized_w1,self.resized_h1=int(img_w*resize_scale),int(img_h*resize_scale)
            
            try:
                resize_img = img.resize((self.resized_w1,self.resized_h1))   
            
            except OSError:
                print("OSError: image file is truncated")
                logging.info("OSError: image file is truncated")               
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                resize_img = img.resize((self.resized_w1,self.resized_h1))   
                
            globals()['image_%s' % window.pre_mangaindex] = ImageTk.PhotoImage(resize_img) 
            
            del img
        
        self.w1 = int((1-settinglevel.manga_resize) / 2 * window.full_w)
        #dynamic variable to get manga_[mangaindex]
        globals()['manga_%s' % window.pre_mangaindex] = self.pic_canvas.create_image(self.w1, self.h2,anchor="sw",image=globals()['image_%s' % window.pre_mangaindex])
        
        del resize_img
        
        print("Add: ", ['manga_%s' % window.pre_mangaindex])
        #print("image Height: ", resized_h1)
        logging.info("Add: %s", ['manga_%s' % window.pre_mangaindex])
        #logging.info("image Height: %s", resized_h1)
    
    def show_manga_mid(self):
        print("show_manga_mid")
        logging.info("show_manga_mid")
        
        # 2nd image
        pic_path = window.fullfilelist[window.fileindex]
        
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        try:
            img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
        
        except FileNotFoundError:
            exception_filenotfound()
                             
        img_w, img_h = img.size
        
        resize_scale = window.full_w / img_w * settinglevel.manga_resize               # calculate the resize ratio, maintaining height-width scale
        self.resized_w2, self.resized_h2 = int(img_w * resize_scale), int(img_h * resize_scale)
        
        try:
            resize_img = img.resize((self.resized_w2, self.resized_h2)) 
        
        except OSError:
            print("OSError: image file is truncated")
            logging.info("OSError: image file is truncated")               
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            resize_img = img.resize((self.resized_w2, self.resized_h2)) 
            
        globals()['image_%s' % window.fileindex] = ImageTk.PhotoImage(resize_img)
        self.w2 = int((1- settinglevel.manga_resize) / 2 * window.full_w)
        globals()['manga_%s' % window.fileindex] = self.pic_canvas.create_image(self.w2, self.h2,anchor="nw",image=globals()['image_%s' % window.fileindex])
        
        if self.photo_preview_visible:
            window.after(0, window.ShowIMG_Preview, pic_path, False, False)
        
        del img
        del resize_img
        
        print("Add: ",  ['manga_%s' % window.fileindex])
        #print("image Height: ", resized_h2)
        logging.info("Add: %s", ['manga_%s' % window.fileindex])
        #logging.info("image Height: %s", resized_h2)
    
    def show_manga_bot(self):
        print("show_manga_bot")
        logging.info("show_manga_bot")
        
        # 3rd image
        i = 1
        while True:
            window.next_mangaindex = window.fileindex + i
            
            if window.next_mangaindex == len(window.fullfilelist):
                window.next_mangaindex = i - 1
                
            pic_path = window.fullfilelist[window.next_mangaindex]
            file_ext = os.path.splitext(pic_path)[1].lower()
            
            if file_ext in window.supported_img:
                break
            
            else:
                i = i + 1

        if len(pic_path) > 255:
            exception_pathtoolong()
        
        if self.manga.ListStor[window.next_mangaindex] is not None:
            self.resized_h3 = self.manga.ListStor[window.next_mangaindex][1]
            resize_img = self.manga.ListStor[window.next_mangaindex][0]
            globals()['image_%s' % window.next_mangaindex] = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
            
        else:      
            try:
                img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
            
            except FileNotFoundError:
                exception_filenotfound()
                       
            img_w, img_h = img.size
            
            resize_scale = window.full_w / img_w * settinglevel.manga_resize             # calculate the resize ratio, maintaining height-width scale
            self.resized_w3, self.resized_h3 = int(img_w * resize_scale), int(img_h * resize_scale)
            
            try:
                resize_img = img.resize((self.resized_w3, self.resized_h3))   
            
            except OSError:
                print("OSError: image file is truncated")
                logging.info("OSError: image file is truncated")               
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                resize_img = img.resize((self.resized_w3, self.resized_h3))   
                
            globals()['image_%s' % window.next_mangaindex] = ImageTk.PhotoImage(resize_img)
            
            del img
            
        self.w3 = int((1 - settinglevel.manga_resize)/2 * window.full_w)
        globals()['manga_%s' % window.next_mangaindex] = self.pic_canvas.create_image(self.w3, self.h3, anchor="nw",image = globals()['image_%s' % window.next_mangaindex])
        
        del resize_img

        print("Add: ",  ['manga_%s' % window.next_mangaindex])
        #print("image Height: ", resized_h3)
        logging.info("Add: %s", ['manga_%s' % window.next_mangaindex])
        #logging.info("image Height: %s", resized_h3)
    
    def scroll_manga(self, event=None, auto=0, forward_backward=0):                       # manga mode
        #print("scroll_manga")
        #logging.info("scroll_manga")

        if auto == 0:          
            if forward_backward != 0:   # forward/backward
                scroll_dis = abs(forward_backward)    # move 1 screen
            
            else:                       # manual scroll
                scroll_dis = settinglevel.auto_dis * settinglevel.scroll_multiplier
                
        else:                           # auto scroll
            scroll_dis = int(auto / settinglevel.auto_frame)
        
        forward = True
        if event is None:
            if forward_backward >= 0:                 # auto scroll and forward
                if window.is_web_mode: 
                    j = 1
                    while True:
                         next2_mangaindex = window.next_mangaindex + j

                         if next2_mangaindex == len(window.fullfilelist):
                             next2_mangaindex = j - 1
                             
                         pic_path = window.fullfilelist[next2_mangaindex]
                         file_ext = os.path.splitext(pic_path)[1].lower()
                         
                         if file_ext in window.supported_img:
                             break
                         
                         else:
                             j = j + 1
                            
                    next2_path = window.fullfilelist[next2_mangaindex]       
                    # print(next2_path)
                    
                    if not os.path.isfile(next2_path):
                        forward = False
                        scroll_dis = max(0, min(scroll_dis, self.h4 - window.full_h - 1))
                #         print("restricted")
                        
                # print(scroll_dis)
                self.scrollup_forward_manga(scroll_dis, forward)
        
            else:                                     # backward
                if window.is_web_mode: 
                    pre2_mangaindex = len(window.fullfilelist) - 1
                            
                    pre2_path = window.fullfilelist[pre2_mangaindex]       
                    # print(pre2_path)
                    
                    if not os.path.isfile(pre2_path) and window.fileindex == 0:
                        scroll_dis = max(0, min(scroll_dis, abs(self.h2 - 1)))
                        # print("restricted")
                        
                # print(self.h2)
                # print(scroll_dis)
                self.scrolldown_backward_manga(scroll_dis)
            
        elif event.delta > 1:                      # manual scroll
            if window.is_web_mode: 
                j = 1
                while True:
                    next2_mangaindex = window.next_mangaindex + j
                    
                    if next2_mangaindex == len(window.fullfilelist):
                        next2_mangaindex = j - 1
                        
                    pic_path = window.fullfilelist[next2_mangaindex]
                    file_ext = os.path.splitext(pic_path)[1].lower()
                    
                    if file_ext in window.supported_img:
                        break
                    
                    else:
                        j = j + 1
                next2_path = window.fullfilelist[next2_mangaindex]       
                # print(next2_path)
                if not os.path.isfile(next2_path):
                    forward = False
                    scroll_dis = max(0, min(scroll_dis, self.h4 - window.full_h - 1))
            #         print("restricted")

            # print(scroll_dis)
            self.scrollup_forward_manga(scroll_dis, forward)
        
        elif event.delta < 1:
            if window.is_web_mode: 
                pre2_mangaindex = len(window.fullfilelist) - 1
                        
                pre2_path = window.fullfilelist[pre2_mangaindex]       
                # print(pre2_path)
                
                if not os.path.isfile(pre2_path) and window.fileindex == 0:
                    scroll_dis = max(0, min(scroll_dis, abs(self.h2 - 1)))
            #         print("restricted")
                    
            # print(self.h2)
            # print(scroll_dis)
            
            self.scrolldown_backward_manga(scroll_dis)

    def scrollup_forward_manga(self, scroll_dis, forward=True):
        
        # Forward
        if self.h3 < window.full_h / 2 and forward:                          
            pre_fileindex = window.fileindex
            prefile_name = os.path.split(window.fullfilelist[pre_fileindex])[1]
            
            while True:
                window.fileindex = window.fileindex + 1

                if window.fileindex == len(window.fullfilelist):
                    window.fileindex = 0
                    
                pic_path = window.fullfilelist[window.fileindex]
                file_ext = os.path.splitext(pic_path)[1].lower()
                
                if file_ext in window.supported_img:
                    break
            
            if window.is_web_mode:
                nextpath_folder = os.path.split(pic_path)[0]
                if nextpath_folder == window.web_output_folder:
                    window.web_fileindex = window.web_fileindex + 1
                
                else:
                    window.web_fileindex = 0
                
            listlevel.listbox1.delete(pre_fileindex)
            listlevel.listbox1.insert(pre_fileindex, prefile_name)
    
            file_name = os.path.split(pic_path)[1]
            listlevel.listbox1.delete(window.fileindex)
            listlevel.listbox1.insert(window.fileindex, u"\u25B6 " + file_name)
            listlevel.listbox1.see(window.fileindex)
            listlevel.listbox2.see(window.fileindex)
            listlevel.listbox3.see(window.fileindex)
            listlevel.listbox4.see(window.fileindex)
            listlevel.listbox5.see(window.fileindex)
            
            self.h1 = self.h2
            self.h2 = self.h3
            self.h3 = self.h4
            
            self.show_manga_bot()
            
            if self.photo_preview_visible:
                window.after(0, window.ShowIMG_Preview, pic_path, False, False)
            
            # Check if the download should run
            DOWNLOAD_TRIGGER = 10
            if window.is_web_mode:
                if window.downloaded_page - window.web_fileindex <= DOWNLOAD_TRIGGER and window.web_fileindex != 0:
                    if not window.thread_batch_download.is_alive():
                        window.thread_batch_download = threading.Thread(target = window.batch_download, args = (window.next_path, window.url_cookies, window.web_output_folder, window.web_fileindex, 20))
                        window.thread_batch_download.start()
                        
            # Check if thread should run
            if self.manga.last_index is not None and self.manga.backend_run == False:
                if abs(self.manga.last_index - window.fileindex) <= 20 or self.manga.last_index - window.fileindex + len(window.fullfilelist) <= 20:
                    
                    self.manga.pause_backend = False
                    
                    print("start manga thread")
                    logging.info("start manga thread")
                    self.manga.thread_storage = threading.Thread(target = self.manga.backend_storage, args = (window.fileindex,))
                    
                    self.manga.stop_backend = False
                    self.manga.thread_storage.start()
            
            # Delete previous image
            self.pic_canvas.delete(globals()['manga_%s' % window.pre_mangaindex])
            del globals()['manga_%s' % window.pre_mangaindex]               # del to release resource
            del globals()['image_%s' % window.pre_mangaindex]
            print("Remove: ",  ['manga_%s' % window.pre_mangaindex])
            logging.info("Remove: %s",  ['manga_%s' % window.pre_mangaindex])

            self.h4 = self.h3 + self.resized_h3
            
            window.pre_mangaindex = pre_fileindex
        
        # run ShowIMG_Preview for web mode
        if self.h3 < window.full_h / 2 and not forward and self.photo_preview_visible: 
            while True:
                temp_fileindex = window.fileindex + 1
                
                if temp_fileindex == len(window.fullfilelist):
                    temp_fileindex = 0
                    
                pic_path = window.fullfilelist[temp_fileindex]
                file_ext = os.path.splitext(pic_path)[1].lower()
                
                if file_ext in window.supported_img:
                    break
            
            window.after(0, window.ShowIMG_Preview, pic_path, False, False)
        
        # Move
        self.pic_canvas.move(globals()['manga_%s' % window.pre_mangaindex], 0, scroll_dis * -1)
        self.pic_canvas.move(globals()['manga_%s' % window.fileindex], 0, scroll_dis * -1)     
        
        try:                                # for multi-thread in auto scroll
            self.pic_canvas.move(globals()['manga_%s' % window.next_mangaindex], 0, scroll_dis * -1)
        
        except:
            print("failed to move next manga")
            logging.info("failed to move next manga")
        
        self.h1 = self.h1 - scroll_dis
        self.h2 = self.h2 - scroll_dis
        self.h3 = self.h3 - scroll_dis
        self.h4 = self.h4 - scroll_dis
            
    def scrolldown_backward_manga(self, scroll_dis):
        
        # Move
        self.pic_canvas.move(globals()['manga_%s' % window.pre_mangaindex], 0, scroll_dis * 1)
        self.pic_canvas.move(globals()['manga_%s' % window.fileindex], 0, scroll_dis * 1)     
        self.pic_canvas.move(globals()['manga_%s' % window.next_mangaindex], 0, scroll_dis * 1)
        
        self.h1 = self.h1 + scroll_dis
        self.h2 = self.h2 + scroll_dis
        self.h3 = self.h3 + scroll_dis
        self.h4 = self.h4 + scroll_dis
        
        # Backward
        if self.h2 > window.full_h:                            # full_h = 865
            pre_fileindex = window.fileindex
            prefile_name = os.path.split(window.fullfilelist[pre_fileindex])[1]
            
            while True:
                window.fileindex = window.fileindex - 1
                
                if window.fileindex < 0:                          # back to end
                    window.fileindex = len(window.fullfilelist) - 1
                    
                pic_path = window.fullfilelist[window.fileindex]
                file_ext = os.path.splitext(pic_path)[1].lower()
                
                if file_ext in window.supported_img:
                    break
                
            if window.is_web_mode:
                nextpath_folder = os.path.split(pic_path)[0]
                if nextpath_folder == window.web_output_folder:
                    window.web_fileindex = window.web_fileindex - 1
                
                else:
                    window.web_fileindex = 0
                    
            listlevel.listbox1.delete(pre_fileindex)
            listlevel.listbox1.insert(pre_fileindex, prefile_name)
    
            file_name = os.path.split(pic_path)[1]
            listlevel.listbox1.delete(window.fileindex)
            listlevel.listbox1.insert(window.fileindex, u"\u25B6 " + file_name)
            listlevel.listbox1.see(window.fileindex)
            listlevel.listbox2.see(window.fileindex)
            listlevel.listbox3.see(window.fileindex)
            listlevel.listbox4.see(window.fileindex)
            listlevel.listbox5.see(window.fileindex)
            
            self.h4 = self.h3
            self.h3 = self.h2
            self.h2 = self.h1
            
            self.show_manga_top()
            
            if self.photo_preview_visible:
                window.after(0, window.ShowIMG_Preview, pic_path, False, False)
            
            self.pic_canvas.delete(globals()['manga_%s' % window.next_mangaindex])
            del globals()['manga_%s' % window.next_mangaindex]              # del to release resource
            del globals()['image_%s' % window.next_mangaindex]
            print("Remove: ",  ['manga_%s' % window.next_mangaindex])
            logging.info("Remove: %s",  ['manga_%s' % window.next_mangaindex])
            
            self.h1 = self.h2 - self.resized_h1
            
            window.next_mangaindex = pre_fileindex
    
    def auto_scrollmanga(self, event=None):                         # auto scroll
        print("auto_manga")
        logging.info("auto_manga")
        
        if window.is_auto_manga:
            window.is_auto_manga = False
        
        else:
            window.is_auto_manga = True
            
        while window.is_auto_manga:
            self.scroll_manga(None, settinglevel.auto_dis * self.forward_speed)
            self.popup.update()
            time.sleep(1 / settinglevel.auto_frame)
    
    def forward_manga(self, event=None):                  # controller: fast forward
        print("forward_manga")
        logging.info("forward_manga")
        
        dis = window.winfo_screenheight() * 1 
        
        self.scroll_manga(None,0, dis)
    
    def backward_manga(self, event=None):                 # controller: fast backward
        print("backward_manga")
        logging.info("backward_manga")
        
        dis = window.winfo_screenheight() * -1
        
        self.scroll_manga(None,0, dis)
    
    def keyscroll_forward_manga(self, event=None):         # controller: forward

        dis = settinglevel.auto_dis * settinglevel.scroll_multiplier * 1 
        
        self.scroll_manga(None,0, dis)
    
    def keyscroll_backward_manga(self, event=None):        # controller: backward
        
        dis = settinglevel.auto_dis * settinglevel.scroll_multiplier * -1
        
        self.scroll_manga(None,0, dis)
        
    def quit_manga(self, event=None):                       # manga mode
        print("quit_manga")
        logging.info("quit_manga")
        
        self.manga.stop_storage(True)
        del self.manga
        
        self.photo_preview.attributes('-topmost', False)
    
        self.popup.unbind("<Button-1>", self.auto_button)
        self.popup.unbind("<p>", self.auto_button2)
        self.popup.unbind("<MouseWheel>", self.updown_wheel_manga)
        self.popup.unbind("<Escape>", self.esc_quit_manga)
        self.popup.unbind("<Up>", self.backward_button_manga)
        self.popup.unbind("<Down>", self.forward_button_manga)
        self.popup.unbind("<z>", self.decrease_forward_manga)
        self.popup.unbind("<x>", self.increase_forward_manga)
        self.button_forward = self.popup.bind("<Right>", self.fullforward)
        self.button_backward = self.popup.bind("<Left>", self.fullbackward)
        self.button2_click = self.popup.bind('<ButtonPress-2>', self.move_from)
        self.button2_motion = self.popup.bind('<B2-Motion>', self.move_to)
        
        self.button_esc = self.popup.bind("<Escape>", self.quit_full)
        self.button1 = self.popup.bind("<Button-1>", self.fullforward)
        self.button3 = self.popup.bind("<Button-3>", self.fullbackward)
        self.wheel = self.popup.bind("<MouseWheel>",self.event_zoom) 
        self.p_button = self.popup.bind("<p>", window.gif_pause)
        
        del globals()['manga_%s' % window.pre_mangaindex]               # del to release resource
        del globals()['image_%s' % window.pre_mangaindex]               # del to release resource
        del globals()['manga_%s' % window.fileindex]                   # del to release resource
        del globals()['manga_%s' % window.next_mangaindex]             # del to release resource
        del globals()['image_%s' % window.fileindex]                   # del to release resource
        del globals()['image_%s' % window.next_mangaindex]              # del to release resource
        
        print("garbage collected: ", gc.collect()) # return no. of unreachable object which will be collected
        logging.info("garbage collected: %s", gc.collect()) 
        
        filepath = window.fullfilelist[window.fileindex]
        window.folder_entry.delete(0,"end")
        window.folder_entry.insert(1, filepath)               # reset folder entry
        
        fulllevel.stor.pause_backend = False
        
        settinglevel.setting_hide()
        settinglevel.enhancer_hide()
        # listlevel.hide_listbox()
        fulllevel.manga_con.attributes('-topmost', False)  
       
        self.back_simple_full()
    
# In[Listbox]
class ListboxGUI():
    
    def __init__(self, parent, list_canva, name):
        print("class ListboxGUI _init_")
        logging.info("class ListboxGUI _init_")
        
        self.name = name
        self.parent = parent
        self.list_canva = list_canva
        self.current_select = None
        
    def create_listbox(self):
        print("create_listbox")    
        logging.info("create_listbox")
        
        self.parent.resizable(False,False)
        self.parent.overrideredirect(1)
        self.parent.geometry('316x550+%d+%d' %(int(settinglevel.listbox_x), int(settinglevel.listbox_y)))    # re adjust list position
        
        self.button_frame = ttk.Frame(self.parent, style='Warning.TFrame')           
        self.button_frame.pack(pady=5, fill="y", side = tk.TOP)  
        
        self.rad_button = ttk.Button(self.button_frame, text= "Random List", width=12, style='primary.TButton', command= window.random_button)
        self.rad_button.pack(side=tk.LEFT,padx=10)   
        self.rad_button.config(state=tk.DISABLED)

        self.filter_button = ttk.Button(self.button_frame, text= "Filter", width=12, style='primary.TButton', command = window.filter_show)
        self.filter_button.pack(side =tk.RIGHT, padx = 10)
        self.filter_button.config(state=tk.DISABLED)
        
        self.folder_frame = ttk.Frame(self.parent, style='Warning.TFrame')           
        self.folder_frame.pack(pady=5, fill="y", side = tk.TOP)  

        self.listbox_scroll = ttk.Scrollbar(self.folder_frame, orient='vertical', style="Vertical.TScrollbar", command = self.OnVsb) 
        self.listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox1 = tk.Listbox(self.folder_frame, width = 30, height = 100, highlightthickness=2, font = ("Arial", 10), selectmode = tk.SINGLE, yscrollcommand = self.listbox_scroll.set)
        self.listbox1.configure(background='black')
        self.listbox1.pack(side=tk.LEFT)
        
        self.listbox5 = tk.Listbox(self.folder_frame, width = 2 , height = 100, highlightthickness=2, font = ("Arial", 10), yscrollcommand = self.listbox_scroll.set)
        self.listbox5.configure(background='black')
        self.listbox5.pack(side=tk.RIGHT)
        
        self.listbox4 = tk.Listbox(self.folder_frame, width = 2 , height = 100, highlightthickness=2, font = ("Arial", 10), yscrollcommand = self.listbox_scroll.set)
        self.listbox4.configure(background='black')
        self.listbox4.pack(side=tk.RIGHT)
        
        self.listbox3 = tk.Listbox(self.folder_frame, width = 2 , height = 100, highlightthickness=2, font = ("Arial", 10), yscrollcommand = self.listbox_scroll.set)
        self.listbox3.configure(background='black')
        self.listbox3.pack(side=tk.RIGHT)
        
        self.listbox2 = tk.Listbox(self.folder_frame, width = 2 , height = 100, highlightthickness=2, font = ("Arial", 10), yscrollcommand = self.listbox_scroll.set)
        self.listbox2.configure(background='black')
        self.listbox2.pack(side=tk.RIGHT)
        
        self.listbox1.bind("<MouseWheel>", self.OnMouseWheel)
        self.listbox2.bind("<MouseWheel>", self.OnMouseWheel)
        self.listbox3.bind("<MouseWheel>", self.OnMouseWheel)
        self.listbox4.bind("<MouseWheel>", self.OnMouseWheel)
        self.listbox5.bind("<MouseWheel>", self.OnMouseWheel)

        # Listbox Drag
        self.list_offsetx = 0
        self.list_offsety = 0
        self.listbox2.bind('<Button-1>', self.listbox_predrag)
        self.listbox2.bind('<B1-Motion>', self.listbox_drag)
        self.listbox3.bind('<Button-1>', self.listbox_predrag)
        self.listbox3.bind('<B1-Motion>', self.listbox_drag)
        self.listbox4.bind('<Button-1>', self.listbox_predrag)
        self.listbox4.bind('<B1-Motion>', self.listbox_drag)
        self.listbox5.bind('<Button-1>', self.listbox_predrag)
        self.listbox5.bind('<B1-Motion>', self.listbox_drag)
        
        # list Canva
        self.list_canva_w = 200
        self.list_canva_h = 160
        self.list_canva.resizable(False,False)
        self.list_canva.overrideredirect(1)
        self.list_canva.geometry('%dx%d+0+0' %(self.list_canva_w, self.list_canva_h + 30))    
        
        self.top_frame = ttk.Frame(self.list_canva, style='Warning.TFrame')           
        self.top_frame.pack(pady=0, fill="y", side = tk.TOP)  
        
        self.top_label = ttk.Label(self.top_frame, text = "                                  " , style='fg.TLabel') # to push quit button to the right
        self.top_label.pack(pady=0, side= tk.LEFT)
        
        self.quit_button = ttk.Button(self.top_frame, text= "\u03A7", width=1, style='primary.Outline.TButton', command = self.list_canva_quit)
        self.quit_button.pack(side =tk.RIGHT, padx = 0)
        
        self.pic_canvas = tk.Canvas(self.list_canva, width = self.list_canva_w, height = self.list_canva_h, highlightthickness = 1)
        self.pic_canvas.pack()
        self.pic_canvas.configure(background='black')
        self.pic_canvas.configure(scrollregion = self.pic_canvas.bbox("all"))
        
        self.listbox1.bind("<Double-Button-1>", self.select_listbox)
        self.listbox1.bind("<Return>", self.select_listbox)
        self.listbox1.bind('<<ListboxSelect>>', self.list_canva_show)
        self.listbox1.bind('<Up>', self.up_listbox)
        self.listbox1.bind('<Down>', self.down_listbox)
        
        self.list_canva_quit()
    
    def OnVsb(self, *args):
        
        self.listbox1.yview(*args)
        self.listbox2.yview(*args)
        self.listbox3.yview(*args)
        self.listbox4.yview(*args)
        self.listbox5.yview(*args)

    def OnMouseWheel(self, event):
    
        self.listbox1.yview("scroll", int(event.delta/-10), "units")
        self.listbox2.yview("scroll", int(event.delta/-10), "units")
        self.listbox3.yview("scroll", int(event.delta/-10), "units")
        self.listbox4.yview("scroll", int(event.delta/-10), "units")
        self.listbox5.yview("scroll", int(event.delta/-10), "units")
        
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"
    
    def listbox_predrag(self, event):
        print("drag_listbox")    
        logging.info("drag_listbox")
        
        self.list_offsetx = event.x
        self.list_offsety = event.y
        
    def listbox_drag(self, event):
        
        self.x = self.parent.winfo_x() + event.x - self.list_offsetx
        self.y = self.parent.winfo_y() + event.y - self.list_offsety
    
        self.parent.geometry('+{x}+{y}'.format(x=self.x,y=self.y))
        
        self.list_canva_quit()
    
    def show_listbox(self):                          # in window and fullscreen mode
        print("show_listbox")    
        logging.info("show_listbox")
        
        if not window.is_filter_con_created:
            window.filter_con = tk.Toplevel(window.parent)
            window.filter_con_create()
        
        try:    
            fulllevel.listbox_button2.config(text = "Hide", command=self.hide_listbox)
            fulllevel.listbox_button3.config(text = "Hide", command=self.hide_listbox)
            fulllevel.listbox_button4.config(text = "Hide", command=self.hide_listbox)
            fulllevel.popup.unbind("<Motion>", fulllevel.motion1)    # fullscreen mode 
            
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    fulllevel.photo_con.attributes('-topmost', True)
                    
                elif window.is_manga_mode:
                    fulllevel.manga_con.attributes('-topmost', True)
                
                else:
                    fulllevel.full_con.attributes('-topmost', True)

        except:
            pass
            # print("failed to modify listbox button or con")
            # logging.info("failed to modify listbox button or con")
        
        self.parent.attributes('-topmost', True)
        window.listbox_button.config(text = "Hide List", command=self.hide_listbox)
        self.parent.deiconify()
        self.listbox1.focus_set()
    
    def cached_listbox(self, name, fileindex, add_remove):
        
        if name == "window":
            if add_remove:
                self.listbox2.delete(fileindex)
                self.listbox2.insert(fileindex, u"\u2713")
                
            else:
                self.listbox2.delete(fileindex)
                self.listbox2.insert(fileindex, "")  
            
            # print(self.listbox2.size())

        if name == "fulllevel":
            if add_remove:
                self.listbox3.delete(fileindex)
                self.listbox3.insert(fileindex, u"\u2713")
                
            else:
                self.listbox3.delete(fileindex)
                self.listbox3.insert(fileindex, "")  
        
            # print(self.listbox3.size())
            
        if name == "photoalbum":
            if add_remove:
                self.listbox4.delete(fileindex)
                self.listbox4.insert(fileindex, u"\u2713")
                
            else:
                self.listbox4.delete(fileindex)
                self.listbox4.insert(fileindex, "")  
                
        if name == "manga":
            if add_remove:
                self.listbox5.delete(fileindex)
                self.listbox5.insert(fileindex, u"\u2713")
                
            else:
                self.listbox5.delete(fileindex)
                self.listbox5.insert(fileindex, "")  
            
            # print(self.listbox5.size())
            
    def reset_cached_listbox(self, name):
        
        window.parent.update()

        if name == "window":
            for i in range(len(window.fullfilelist)):
                listlevel.listbox2.delete(i)
                listlevel.listbox2.insert(i, "")
                
        if name == "fulllevel":           
            for i in range(len(window.fullfilelist)):
                listlevel.listbox3.delete(i)
                listlevel.listbox3.insert(i, "")

        if name == "photoalbum":         
            for i in range(len(window.fullfilelist)):
                listlevel.listbox4.delete(i)
                listlevel.listbox4.insert(i, "")
                
        if name == "manga":         
            for i in range(len(window.fullfilelist)):
                listlevel.listbox5.delete(i)
                listlevel.listbox5.insert(i, "")
                
    def list_canva_show(self, event=None):
        
        if self.listbox1.curselection()[0] == self.current_select: # avoid running twice when double click
            return None
        
        listbox_x = listlevel.parent.winfo_x()
        listbox_y = listlevel.parent.winfo_y()
        
        self.list_canva.deiconify()
        self.list_canva.attributes('-topmost', True)
        
        if event is None:
            canva_y = listbox_y
        
        else:
            canva_y = event.y
            
        self.list_canva.geometry('+{x}+{y}'.format(x=listbox_x + 300,y=canva_y + 100))
        
        # Show IMG
        try:
            self.current_select = self.listbox1.curselection()[0]     # select on listbox, return integer
            
        except IndexError:                                  # error when double click
            self.list_canva_quit()
            return None
        
        filepath = window.fullfilelist[self.current_select]
        file_ext = os.path.splitext(filepath)[1].lower()      # separate file name and extension
        
        if file_ext in (window.supported_ani | window.supported_vid):
            is_vid = True
        
        else:
            is_vid = False
        
        if os.path.isfile(filepath):  # avoid FileNotFoundError in web mode
            window.ShowIMG_Preview(filepath, is_vid, True)
    
    def list_canva_quit(self, event=None):
        
        self.list_canva.withdraw()
        self.listbox1.focus_set()
    
    def up_listbox(self, event):
        print("up_listbox")
        logging.info("up_listbox")
        
        if self.current_select is None:
            new_select = 0
            
        else:
            new_select = self.current_select - 1
        
        if new_select < 0 :
            new_select = len(window.fullfilelist) - 1
            
        if self.current_select is None:
            self.listbox1.selection_set(new_select)
        
        else:
            self.listbox1.selection_clear(self.current_select)
            self.listbox1.selection_set(new_select)
        
        self.list_canva_show()
    
    def down_listbox(self, event):
        print("down_listbox")
        logging.info("down_listbox")
        
        if self.current_select is None:
            new_select = 0
            
        else:
            new_select = self.current_select + 1
        
        if new_select > len(window.fullfilelist) - 1:
            new_select = 0
            
        if self.current_select is None:
            self.listbox1.selection_set(new_select)    
        
        else:
            self.listbox1.selection_clear(self.current_select)
            self.listbox1.selection_set(new_select)
            
        self.list_canva_show()
    
    def select_listbox(self, event):
        print("select_listbox")
        logging.info("select_listbox")
        
        try:
            pre_fileindex = window.fileindex
            prefile_name = os.path.split(window.fullfilelist[pre_fileindex])[1]
            window.fileindex = self.listbox1.curselection()[0]     # select on listbox, return integer
            filepath = window.fullfilelist[window.fileindex]
            
        except IndexError:       # error when double click empty space
            print("IndexError")
            logging.info("IndexError")
            return None

        if not os.path.isfile(filepath):     # avoid FileNotFoundError in web mode
            print("FileNotFoundError")
            logging.info("FileNotFoundError")
            return None
        
        is_cached = False
        is_fullcached = False
        window.is_gif_pause = False
        window.stor.pause_backend = True
        
        self.list_canva_quit()
        
        window.folder_entry.delete(0,"end")
        window.folder_entry.insert(1, filepath)           # replace folder entry
        
        self.listbox1.delete(pre_fileindex)
        self.listbox1.insert(pre_fileindex, prefile_name)        # remove play signal of previous file
        
        file_name = os.path.split(filepath)[1]          
        self.listbox1.delete(window.fileindex)
        self.listbox1.insert(window.fileindex, u"\u25B6 " + file_name)   # show play signal of current file
        self.listbox1.see(window.fileindex)
        self.listbox2.see(window.fileindex)
        self.listbox3.see(window.fileindex)
        self.listbox4.see(window.fileindex)
        self.listbox5.see(window.fileindex)
        
        self.listbox1.selection_set(window.fileindex)
        self.current_select = window.fileindex
        
        file_ext = os.path.splitext(filepath)[1].lower()      # separate file name and extension
            
        if window.is_full_mode:                      # full screen mode
            if window.is_photoalbum_mode:
                self.select_photo_mode(filepath, file_ext)
            
            elif window.is_manga_mode:
                self.select_manga_mode()
            
            else: 
                self.select_full_mode(filepath, file_ext, is_fullcached)
                
        else:                                        # window mode
            self.select_window_mode(filepath, file_ext, is_cached)
        
    def select_window_mode(self, filepath, file_ext, is_cached):
       
        window.stor.stop_storage(False)       

        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
        
        window.stor.stop_backend = False
        window.stor.thread_storage.start()
        
        window.stor.ListPhotoStor = [None] * len(window.fullfilelist)  # clear cache of photoimage
        
        if window.check_photoimage(window.fileindex):
            print("start window thread (PhotoImage)")
            logging.info("start window thread (PhotoImage)")
            window.stor.thread_storage_photoimage = threading.Thread(target = window.stor.backend_photoimage_storage, args = (window.fileindex,))
            window.stor.thread_storage_photoimage.start()

        if file_ext in window.supported_img:
            if window.stor.ListStor[window.fileindex] is not None:
                is_cached = True
            window.ShowIMG(filepath, is_cached)
        
        elif file_ext in (window.supported_ani | window.supported_vid):
            try:
                is_cached = window.stor.ListStor[window.fileindex].get("is_cached", False)
            
            except AttributeError:
                is_cached = False

            window.ShowANI(filepath, is_cached)   
    
    def select_full_mode(self, filepath, file_ext, is_fullcached):
       
        fulllevel.stor.stop_storage(False)  
        
        fulllevel.stor.thread_storage = threading.Thread(target = fulllevel.stor.backend_storage, args = (window.fileindex,))
        
        fulllevel.stor.stop_backend = False
        fulllevel.stor.thread_storage.start()
        
        fulllevel.stor.ListPhotoStor = [None] * len(window.fullfilelist)  # clear cache of photoimage
        
        if window.check_photoimage(window.fileindex):
            print("start fulllevel thread (PhotoImage)")
            logging.info("start fulllevel thread (PhotoImage)")
            fulllevel.stor.thread_storage_photoimage = threading.Thread(target = fulllevel.stor.backend_photoimage_storage, args = (window.fileindex,))
            fulllevel.stor.thread_storage_photoimage.start()
        
        if file_ext in window.supported_img:
            if fulllevel.stor.ListStor[window.fileindex] is not None:
                is_fullcached = True
                
            window.ShowIMG_Full(filepath, is_fullcached)
        
        elif file_ext in (window.supported_ani | window.supported_vid):
            try:
                is_fullcached = fulllevel.stor.ListStor[self.fileindex].get("is_cached", False)
            
            except AttributeError:
                is_fullcached = False
                
            window.ShowANI_Full(filepath, is_fullcached) 
    
    def select_photo_mode(self, filepath, file_ext):
        
        window.stop_album = True
        
        fulllevel.photoalbum.stop_storage(False)          # pause current storage thread
        fulllevel.photoalbum.pause_backend = False
                        
        print("start photoalbum thread")
        logging.info("start photoalbum thread")
        fulllevel.photoalbum.thread_storage = threading.Thread(target = fulllevel.photoalbum.backend_storage, args = (window.fileindex,))
        
        fulllevel.photoalbum.stop_backend = False
        fulllevel.photoalbum.thread_storage.start()
        
        if fulllevel.photoalbum.ListStor[window.fileindex] is not None:
            is_photocached = True
        else:
            is_photocached = False
        
        if file_ext in window.supported_img:
            
            if fulllevel.photo_preview_visible:
                window.ShowIMG_FullPhotoalbum(filepath, True, is_photocached)  # Photo Album mode
                window.ShowIMG_Preview(filepath, False, False)
                
            window.after(20, window.ShowIMG_FullPhotoalbum, filepath)  # Photo Album mode
            
        if file_ext in window.supported_ani:
            # window.ShowIMG_Preview(filepath, True, False)
            # window.ShowANI_Full(filepath)
            window.fullforward()
            
    def select_manga_mode(self):
        
        fulllevel.h2 = 0                                         
        fulllevel.show_manga_top()
        fulllevel.show_manga_mid()                                  
        fulllevel.h1 = 0 - fulllevel.resized_h1
        fulllevel.h3 = 0 + fulllevel.resized_h2
        fulllevel.show_manga_bot()
        fulllevel.h4 = 0 + fulllevel.resized_h2 + fulllevel.resized_h3
        
        fulllevel.manga.stop_storage(False)          # pause current storage thread
        
        # restart another thread
        fulllevel.manga.thread_storage = threading.Thread(target = fulllevel.manga.backend_storage, args = (window.fileindex,))
        
        fulllevel.manga.stop_backend = False
        fulllevel.manga.thread_storage.start()  
    
    def hide_listbox(self):                            # in fullscreen mode
        print("hide_listbox")
        logging.info("hide_listbox")
        
        try:
            fulllevel.listbox_button2.config(text = "List", command=self.show_listbox)
            fulllevel.listbox_button3.config(text = "List", command=self.show_listbox)
            fulllevel.listbox_button4.config(text = "List", command=self.show_listbox)
            fulllevel.motion1 = fulllevel.popup.bind("<Motion>", fulllevel.motion)
            
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    fulllevel.photo_con.attributes('-topmost', False)
                    
                elif window.is_manga_mode:
                    fulllevel.manga_con.attributes('-topmost', False)
                
                else:
                    fulllevel.full_con.attributes('-topmost', False)           
        except:
            pass
            # print("failed to modify listbox button or con")
            # logging.info("failed to modify listbox button or con")
        
        self.parent.attributes('-topmost', False)
        
        try:
            window.listbox_button.config(text = "List", command=self.show_listbox)
        
        except:
            print("failed to modify listbox button")
            logging.info("failed to modify listbox button")
        
        self.parent.withdraw()
        self.list_canva_quit()

# In[Settings]
class SettingGUI(WindowGUI):
    
    def __init__(self, parent, ie, name):
        print("class SettingGUI _init_")
        logging.info("class SettingGUI _init_")
        
        self.name = name
        self.parent = parent
        self.ie = ie
        self.is_settingcreated = False
        self.is_iecreated = False
        
        self.parent.withdraw()
        self.ie.withdraw()
        
    def import_settings(self):
        print("import_settings") 
        logging.info("import_settings")
        
        # Default Settings
        # window mode
        self.window_width = 800
        self.window_height = 600
        self.window_x = 300
        self.window_y = 150
        self.window_state = "normal"
    
        self.listbox_x = 50
        self.listbox_y = 120
        
        self.setting_x = 150
        self.setting_y = 100
        
        self.ie_x = 150
        self.ie_y = 300
        
        self.gif_con_x = window.full_w - 1500
        self.gif_con_y = window.full_h - 200
        
        self.webcon_x = window.full_w - 1500
        self.webcon_y = window.full_h - 200
        
        self.webpopup_x = 500
        self.webpopup_y = 350
        
        self.parent_check = tk.BooleanVar()
        self.is_parent = False
        self.parent_check.set(False)                        # include subfolder
        
        self.natsort_check = tk.BooleanVar()
        self.is_natsort = False
        self.natsort_check.set(False)                       # natural sort
        
        self.original_check = tk.BooleanVar()
        self.is_original = False
        self.original_check.set(False)                        # original size
        
        self.storage_check = tk.BooleanVar()               
        self.is_storage = True
        self.storage_check.set(True)                       # enable cache
        
        self.randomgifspeed_check = tk.BooleanVar()
        self.random_gifspeed = False
        self.randomgifspeed_check.set(False)                        # random gif speed
        
        self.randomgifloop_check = tk.BooleanVar()
        self.random_gifloop = False
        self.randomgifloop_check.set(False)                        # random number of gif loop
        
        self.alwayspreview_check = tk.BooleanVar()
        self.is_alwayspreview = False
        self.alwayspreview_check.set(False)                        # always show preview in photo album mode
        
        self.skipframespeed_check = tk.BooleanVar()
        self.is_skipframespeed = False
        self.skipframespeed_check.set(False)                        # skip frame to match actual speed
        
        self.gif_speed = 1.0
        
        self.enhanceall_check = tk.BooleanVar()
        self.is_enhanceall = False
        self.enhanceall_check.set(False)                        # apply enhance settings to all img in window, simple full, slide and photo album mode
        
        self.enhancecurrent_check = tk.BooleanVar()
        self.enhancecurrent_check.set(False)                        # apply enhance settings to current img in window, simple full, slide and photo album mode
        
        # simple fullscreen mode
        
        # slide mode and photo album mode
        self.default_timer = 5                              # timer for images
        self.gif_loop = 3                                   # times of gif loop for each slide
        
        # photo album mode
        self.timer_frame = 60                               # frame of image move
        
        # phto album mode and manga mode
        self.scroll_multiplier = 0.7                        # scroll distance, equal to half second
        
        # manga mode
        self.manga_resize = 1                               # width in manga mode
        self.auto_frame = 60                                # frame of auto manga
        self.auto_dis = 200                                 # distance of auto per second 
        
        self.setting_gifspeedstr = "Normal"
        self.setting_scrollstr = "Normal"
        self.setting_imagesizestr = "Fullscreen"
        self.setting_autospeedstr = "Normal"
        
        # Import config
        self.config = configparser.ConfigParser()
        
        exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
        self.config_path = os.path.join(exe_dir, "config.ini")
        self.config.read(self.config_path)
        
        #is_parent = str(getconfig("parent_check", is_parent)) # disable getting parent_check
        #parent_check.set(is_parent)
        self.is_natsort = self.getconfig("natsort_check", self.is_natsort) # disable getting parent_check
        self.natsort_check.set(self.is_natsort)
        self.random_gifloop = self.getconfig("randomgifloop_check", self.random_gifloop)
        self.randomgifloop_check.set(self.random_gifloop)
        self.is_alwayspreview = self.getconfig("alwayspreview_check", self.is_alwayspreview)
        self.alwayspreview_check.set(self.is_alwayspreview)
        self.random_gifspeed = self.getconfig("randomgifspeed_check", self.random_gifspeed)
        self.randomgifspeed_check.set(self.random_gifspeed)
        self.is_original = self.getconfig("original_check", self.is_original)
        self.original_check.set(self.is_original)
        self.is_storage = self.getconfig("storage_check", self.is_storage)
        self.storage_check.set(self.is_storage)
        self.is_skipframespeed = self.getconfig("skipframespeed_check", self.is_skipframespeed)
        self.skipframespeed_check.set(self.is_skipframespeed)
        self.is_enhanceall = self.getconfig("enhanceall_check", self.is_enhanceall) 
        self.enhanceall_check.set(self.is_enhanceall)
        self.gif_speed = float(self.getconfig("gif_speed", self.gif_speed))
        self.default_timer = int(self.getconfig("default_timer", self.default_timer))
        self.gif_loop = int(self.getconfig("gif_loop", self.gif_loop))
        self.scroll_multiplier = float(self.getconfig("scroll_multiplier", self.scroll_multiplier))
        self.manga_resize = float(self.getconfig("manga_resize", self.manga_resize))
        self.auto_dis = int(self.getconfig("auto_dis", self.auto_dis))
        self.setting_gifspeedstr = str(self.getconfig("setting_gifspeedstr", self.setting_gifspeedstr))
        self.setting_scrollstr = str(self.getconfig("setting_scrollstr", self.setting_scrollstr))
        self.setting_imagesizestr = str(self.getconfig("setting_imagesizestr", self.setting_imagesizestr))
        self.setting_autospeedstr = str(self.getconfig("setting_autospeedstr", self.setting_autospeedstr))
        self.window_width = str(self.getconfig("window_width", self.window_width))
        self.window_height = str(self.getconfig("window_height", self.window_height))
        self.window_x = str(self.getconfig("window_x", self.window_x))
        self.window_y = str(self.getconfig("window_y", self.window_y))
        self.window_state = str(self.getconfig("window_state", self.window_state))
        self.listbox_x = str(self.getconfig("listbox_x", self.listbox_x))
        self.listbox_y = str(self.getconfig("listbox_y", self.listbox_y))
        self.setting_x = str(self.getconfig("setting_x", self.setting_x))
        self.setting_y = str(self.getconfig("setting_y", self.setting_y))
        self.ie_x = str(self.getconfig("ie_x", self.ie_x))
        self.ie_y = str(self.getconfig("ie_y", self.ie_y))
        self.gif_con_x = str(self.getconfig("gif_con_x", self.gif_con_x))
        self.gif_con_y = str(self.getconfig("gif_con_y", self.gif_con_y))
        self.webcon_x = str(self.getconfig("webcon_x", self.webcon_x))
        self.webcon_y = str(self.getconfig("webcon_y", self.webcon_y))
        self.webpopup_x = str(self.getconfig("webpopup_x", self.webpopup_x))
        self.webpopup_y = str(self.getconfig("webpopup_y", self.webpopup_y))
        
        self.pre_original = self.is_original
        self.pre_storage = self.is_storage
        self.pre_manga_resize = self.manga_resize
    
    def setting_buttonclick(self):
        print("setting_buttonclick")
        logging.info("setting_buttonclick")
        
        try:    
            fulllevel.settings_button2.config(text = "Hide", command=self.setting_hide)
            fulllevel.settings_button3.config(text = "Hide", command=self.setting_hide)
            fulllevel.settings_button4.config(text = "Hide", command=self.setting_hide)
            fulllevel.popup.unbind("<Motion>", fulllevel.motion1)    # fullscreen mode 
            
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    fulllevel.photo_con.attributes('-topmost', True)
                    
                elif window.is_manga_mode:
                    fulllevel.manga_con.attributes('-topmost', True)
                
                else:
                    fulllevel.full_con.attributes('-topmost', True)
            
        except:
            print("failed to modify settings button or con")
            logging.info("failed to modify settings button or con")
        
        window.setting_button.config(text = "Hide", command=self.setting_hide)

        if not self.is_settingcreated:
            self.setting_create()
            
        self.parent.deiconify()
        self.parent.attributes('-topmost', True)
        self.parent.update()         # update for the position
    
    def setting_create(self):                          # in window and fullscreen mode
        print("setting_create") 
        logging.info("setting_create")
        
        self.is_settingcreated = True
        
        self.parent.resizable(False,False)
        self.parent.overrideredirect(1)
        self.parent.geometry('350x760+%d+%d' %(int(self.setting_x), int(self.setting_y)))    # re adjust list position
    
        self.setting_frame0 = tk.Frame(self.parent)             
        self.setting_frame0.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
          
        self.setting_frame1 = tk.Frame(self.parent, background='gray25')             
        self.setting_frame1.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame2 = tk.Frame(self.parent)             
        self.setting_frame2.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame3 = tk.Frame(self.parent)             
        self.setting_frame3.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame4 = tk.Frame(self.parent)             
        self.setting_frame4.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame5 = tk.Frame(self.parent)             
        self.setting_frame5.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame6 = tk.Frame(self.parent)             
        self.setting_frame6.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame00 = tk.Frame(self.parent, background='gray25')             
        self.setting_frame00.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame01 = tk.Frame(self.parent)             
        self.setting_frame01.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame02 = tk.Frame(self.parent)             
        self.setting_frame02.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame10 = tk.Frame(self.parent, background='gray25')             
        self.setting_frame10.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame11 = tk.Frame(self.parent)             
        self.setting_frame11.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame12 = tk.Frame(self.parent)             
        self.setting_frame12.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame13 = tk.Frame(self.parent)             
        self.setting_frame13.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame20 = tk.Frame(self.parent, background='gray25')             
        self.setting_frame20.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame21 = tk.Frame(self.parent)             
        self.setting_frame21.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame22 = tk.Frame(self.parent)             
        self.setting_frame22.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame30 = tk.Frame(self.parent, background='gray25')             
        self.setting_frame30.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame31 = tk.Frame(self.parent)             
        self.setting_frame31.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame32 = tk.Frame(self.parent)             
        self.setting_frame32.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame40 = tk.Frame(self.parent)             
        self.setting_frame40.pack(pady=5, side = tk.BOTTOM)
        
        self.setting_frame41 = tk.Frame(self.parent)             
        self.setting_frame41.pack(pady=5, side = tk.BOTTOM)
        
        self.setting_label0 = ttk.Label(self.setting_frame0, text = "" , style='fg.TLabel') # to enable frame0
        self.setting_label0.pack(pady=0, side= tk.LEFT)
        
        self.setting_label1 = ttk.Label(self.setting_frame1, text = "  General : " , style='fg.TLabel' , background='gray25')
        self.setting_label1.pack(pady=0, side= tk.LEFT)
        
        self.setting_label2 = ttk.Label(self.setting_frame2, text = "      Natural Sort : " , style='fg.TLabel')
        self.setting_label2.pack(pady=0, side= tk.LEFT)
        
        self.setting_label3 = ttk.Label(self.setting_frame3, text = "      Original Size : " , style='fg.TLabel')
        self.setting_label3.pack(pady=0, side= tk.LEFT)
        
        self.setting_label4 = ttk.Label(self.setting_frame4, text = "      GIF Speed : " , style='fg.TLabel')
        self.setting_label4.pack(pady=5, side= tk.LEFT)
        
        self.setting_label5 = ttk.Label(self.setting_frame5, text = "      Random GIF Speed : " , style='fg.TLabel')
        self.setting_label5.pack(pady=5, side= tk.LEFT)
        
        self.setting_label6 = ttk.Label(self.setting_frame6, text = "      Skip GIF Frame For Actual Speed : " , style='fg.TLabel')
        self.setting_label6.pack(pady=5, side= tk.LEFT)
        
        self.setting_label00 = ttk.Label(self.setting_frame00, text = "  Auto Cache : " ,style='fg.TLabel', background='gray25')
        self.setting_label00.pack(pady=0, side= tk.LEFT)
        
        self.setting_label01 = ttk.Label(self.setting_frame01, text = "      Enable Cache : " , style='fg.TLabel')
        self.setting_label01.pack(pady=0, side= tk.LEFT)
        
        self.setting_label02 = ttk.Label(self.setting_frame02, text = "      Clear Cache : " , style='fg.TLabel')
        self.setting_label02.pack(pady=0, side= tk.LEFT)
        
        self.setting_label10 = ttk.Label(self.setting_frame10, text = "  Slide mode / Photo Album mode : " ,style='fg.TLabel', background='gray25')
        self.setting_label10.pack(pady=0, side= tk.LEFT)
        
        self.setting_label11 = ttk.Label(self.setting_frame11, text = "      Image Timer (seconds): " , style='fg.TLabel')
        self.setting_label11.pack(pady=0, side= tk.LEFT)
        
        self.setting_label12 = ttk.Label(self.setting_frame12, text = "      GIF Loop (times): " , style='fg.TLabel')
        self.setting_label12.pack(pady=0, side= tk.LEFT)
        
        self.setting_label13 = ttk.Label(self.setting_frame13, text = "      Random GIF Loop : " , style='fg.TLabel')
        self.setting_label13.pack(pady=0, side= tk.LEFT)
        
        self.setting_label20 = ttk.Label(self.setting_frame20, text = "  Photo Album mode / Manga mode : " ,style='fg.TLabel', background='gray25')
        self.setting_label20.pack(pady=0, side= tk.LEFT)
        
        self.setting_label21 = ttk.Label(self.setting_frame21, text = "      Scroll : ", style='fg.TLabel' )
        self.setting_label21.pack(pady=0, side= tk.LEFT)
        
        self.setting_label22 = ttk.Label(self.setting_frame22, text = "      Always Show Preview : " , style='fg.TLabel')
        self.setting_label22.pack(pady=0, side= tk.LEFT)
        
        self.setting_label30 = ttk.Label(self.setting_frame30, text = "  Manga mode : " ,style='fg.TLabel', background='gray25')
        self.setting_label30.pack(pady=0, side= tk.LEFT)
        
        self.setting_label31 = ttk.Label(self.setting_frame31, text = "      Image Size : " , style='fg.TLabel')
        self.setting_label31.pack(pady=0, side= tk.LEFT)
        
        self.setting_label32 = ttk.Label(self.setting_frame32, text = "      Auto Speed : ", style='fg.TLabel' )
        self.setting_label32.pack(pady=0, side= tk.LEFT)
        
        self.setting_check2 = ttk.Checkbutton(self.setting_frame2, text="", var=self.natsort_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check2.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_check3 = ttk.Checkbutton(self.setting_frame3, text="", var=self.original_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check3.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_check5 = ttk.Checkbutton(self.setting_frame5, text="", var=self.randomgifspeed_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check5.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_check6 = ttk.Checkbutton(self.setting_frame6, text="", var=self.skipframespeed_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check6.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_check22 = ttk.Checkbutton(self.setting_frame22, text="", var=self.alwayspreview_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check22.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_check01 = ttk.Checkbutton(self.setting_frame01, text="", var=self.storage_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check01.pack(pady=0, padx = 0, side= tk.RIGHT)

        self.setting_button_clearcache = tk.Button(self.setting_frame02, text = "Clear", command=window.clear_all_cache, width=8)
        self.setting_button_clearcache.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_gifspeed = tk.StringVar()
        self.setting_gifspeed.set(self.setting_gifspeedstr)
        self.setting_scroll4 = tk.OptionMenu(self.setting_frame4, self.setting_gifspeed, "Very Fast", "Fast", "Normal", "Slow", "Very Slow")
        self.setting_scroll4["highlightthickness"] = 0                  # remove the option boundary
        self.setting_scroll4.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_entry11 = tk.Entry(self.setting_frame11, width=5, background='gray25')
        self.setting_entry11.insert(1, self.default_timer)
        self.setting_entry11.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_entry12 = tk.Entry(self.setting_frame12, width=5, background='gray25')
        self.setting_entry12.insert(1, self.gif_loop)
        self.setting_entry12.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_check13 = ttk.Checkbutton(self.setting_frame13, text="", var=self.randomgifloop_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check13.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_scroll = tk.StringVar()
        self.setting_scroll.set(self.setting_scrollstr)
        self.setting_scroll21 = tk.OptionMenu(self.setting_frame21, self.setting_scroll, "Fast", "Normal", "Slow")
        self.setting_scroll21["highlightthickness"] = 0
        self.setting_scroll21.pack(pady=0, padx = 10, side= tk.RIGHT)
 
        self.setting_imagesize = tk.StringVar()
        self.setting_imagesize.set(self.setting_imagesizestr)
        self.setting_scroll31 = tk.OptionMenu(self.setting_frame31, self.setting_imagesize, "Very Small", "Small", "Normal", "Large", "Fullscreen")
        self.setting_scroll31["highlightthickness"] = 0
        self.setting_scroll31.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_autospeed = tk.StringVar()
        self.setting_autospeed.set(self.setting_autospeedstr)
        self.setting_scroll32 = tk.OptionMenu(self.setting_frame32, self.setting_autospeed, "Very Fast", "Fast", "Normal", "Slow", "Very Slow")
        self.setting_scroll32["highlightthickness"] = 0
        self.setting_scroll32.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_error = tk.Label(self.setting_frame41, text = "", fg = "red", font = ("Arial", 10))
        self.setting_error.pack()
        
        self.setting_button_save = tk.Button(self.setting_frame40, text = "Save and Close", command=self.setting_ok,width=20)
        self.setting_button_save.pack(side =tk.LEFT, padx = 20)
        
        self.setting_button_quit = tk.Button(self.setting_frame40, text = "Cancel", command=self.setting_hide,width=20)
        self.setting_button_quit.pack(side =tk.RIGHT, padx = 20)
        
        # Setting Drag
        self.setting_offsetx = 0
        self.setting_offsety = 0
        self.setting_frame0.bind('<Button-1>', self.setting_predrag)
        self.setting_frame0.bind('<B1-Motion>', self.setting_drag)
 
    def setting_predrag(self, event):
        print("drag_setting")    
        logging.info("drag_setting")
        
        self.setting_offsetx = event.x
        self.setting_offsety = event.y
        
    def setting_drag(self, event):
        
        self.x = self.parent.winfo_x() + event.x - self.setting_offsetx
        self.y = self.parent.winfo_y() + event.y - self.setting_offsety
    
        self.parent.geometry('+{x}+{y}'.format(x = self.x, y = self.y))
    
    def setting_ok(self):
        print("setting_ok")
        logging.info("setting_ok")
        
        self.setting_error.config(text = "")
        
        # window mode
        self.is_parent = self.parent_check.get()
        self.is_original = self.original_check.get()
        self.is_natsort = self.natsort_check.get()
        self.random_gifspeed = self.randomgifspeed_check.get()
        self.is_skipframespeed = self.skipframespeed_check.get()
        
        # auto cache
        self.is_storage = self.storage_check.get()

        # simple fullscreen mode
        self.setting_gifspeedstr = self.setting_gifspeed.get()
        
        if self.setting_gifspeedstr == "Very Fast":       
            self.gif_speed = 0.4
        
        elif self.setting_gifspeedstr == "Fast":
            self.gif_speed = 0.7
        
        elif self.setting_gifspeedstr == "Normal":
            self.gif_speed = 1.0
            
        elif self.setting_gifspeedstr == "Slow":
            self.gif_speed = 1.25
        
        elif self.setting_gifspeedstr == "Very Slow":
            self.gif_speed = 1.5
        
        # slide mode and photo album mode
        try:
            self.default_timer = int(self.setting_entry11.get())                      # timer for images
        
        except ValueError:
            exception_settingswrongvalue()
      
        try:
            self.gif_loop = int(self.setting_entry12.get())                # times of gif loop for each slide
        
        except ValueError:
            exception_settingswrongvalue()
        
        self.random_gifloop = self.randomgifloop_check.get()
        
        # phto album mode and manga mode
        self.setting_scrollstr = self.setting_scroll.get()
        
        if self.setting_scrollstr == "Fast":       # scroll distance, equal to half second
            self.scroll_multiplier = 1.2
        
        elif self.setting_scrollstr == "Normal":
            self.scroll_multiplier = 0.9
        
        elif self.setting_scrollstr == "Slow":
            self.scroll_multiplier = 0.6
        
        pre_alwayspreview = self.is_alwayspreview
        self.is_alwayspreview = self.alwayspreview_check.get()
        
        # manga mode
        self.setting_imagesizestr = self.setting_imagesize.get()
        
        if self.setting_imagesizestr == "Fullscreen":        # width in manga mode
            self.manga_resize = 1
        
        elif self.setting_imagesizestr == "Large":
            self.manga_resize = 0.9
        
        elif self.setting_imagesizestr == "Normal":
            self.manga_resize = 0.75

        elif self.setting_imagesizestr == "Small":
            self.manga_resize = 0.6
            
        elif self.setting_imagesizestr == "Very Small":
            self.manga_resize = 0.45
        
        self.setting_autospeedstr = self.setting_autospeed.get()
        
        if self.setting_autospeedstr == "Very Fast":             # distance of auto per second 
            self.auto_dis = 320
        
        elif self.setting_autospeedstr == "Fast":   
            self.auto_dis = 270
            
        elif self.setting_autospeedstr == "Normal":             
            self.auto_dis = 220
        
        elif self.setting_autospeedstr == "Slow": 
            self.auto_dis = 170    
        
        elif self.setting_autospeedstr == "Very Slow": 
            self.auto_dis = 120
        
        if self.window_state == "normal":                     # not update if window zoomed
            self.window_width = window.parent.winfo_width()
            self.window_height = window.parent.winfo_height()
            self.window_x = window.parent.winfo_x()
            self.window_y = window.parent.winfo_y()
        
        self.listbox_x = listlevel.parent.winfo_x()
        self.listbox_y = listlevel.parent.winfo_y()
        
        #settinglevel.deiconify()
        #settinglevel.update()
        
        self.setting_x = self.parent.winfo_x()
        self.setting_y = self.parent.winfo_y()
        
        self.ie_x = self.ie.winfo_x()
        self.ie_y = self.ie.winfo_y()
        
        self.gif_con_x = window.gif_con.winfo_x()
        self.gif_con_y = window.gif_con.winfo_y()
        
        try:
            self.webcon_x = window.web_con.winfo_x()
            self.webcon_y = window.web_con.winfo_y()
            
            self.webpopup_x = window.web_popup.winfo_x()
            self.webpopup_y = window.web_popup.winfo_y()
        
        except:
            pass
        
        # Save config
        try:
            self.config_file = open(self.config_path, "w")
        
        except PermissionError:
            exception_settingnopermission()

        try:
            self.config.add_section("ImageViewer")
            
        except configparser.DuplicateSectionError:
            pass                                   # exception if already have config and section
        
        finally:
            self.config.set("ImageViewer", "parent_check", str(self.is_parent))
            self.config.set("ImageViewer", "natsort_check", str(self.is_natsort))
            self.config.set("ImageViewer", "original_check", str(self.is_original))
            self.config.set("ImageViewer", "storage_check", str(self.is_storage))
            self.config.set("ImageViewer", "randomgifspeed_check", str(self.random_gifspeed))
            self.config.set("ImageViewer", "alwayspreview_check", str(self.is_alwayspreview))
            self.config.set("ImageViewer", "skipframespeed_check", str(self.is_skipframespeed))
            self.config.set("ImageViewer", "enhanceall_check", str(self.is_enhanceall))
            self.config.set("ImageViewer", "gif_speed", str(self.gif_speed))
            self.config.set("ImageViewer", "default_timer", str(self.default_timer))
            self.config.set("ImageViewer", "gif_loop", str(self.gif_loop))
            self.config.set("ImageViewer", "randomgifloop_check", str(self.random_gifloop))
            self.config.set("ImageViewer", "setting_scrollstr", self.setting_scrollstr)
            self.config.set("ImageViewer", "scroll_multiplier", str(self.scroll_multiplier))
            self.config.set("ImageViewer", "setting_gifspeedstr", self.setting_gifspeedstr)
            self.config.set("ImageViewer", "setting_imagesizestr", self.setting_imagesizestr)
            self.config.set("ImageViewer", "manga_resize", str(self.manga_resize))
            self.config.set("ImageViewer", "setting_autospeedstr", self.setting_autospeedstr)
            self.config.set("ImageViewer", "auto_dis", str(self.auto_dis))
            self.config.set("ImageViewer", "listbox_x", str(self.listbox_x))
            self.config.set("ImageViewer", "listbox_y", str(self.listbox_y))
            self.config.set("ImageViewer", "setting_x", str(self.setting_x))
            self.config.set("ImageViewer", "setting_y", str(self.setting_y))
            self.config.set("ImageViewer", "ie_x", str(self.ie_x))
            self.config.set("ImageViewer", "ie_y", str(self.ie_y))
            self.config.set("ImageViewer", "gif_con_x", str(self.gif_con_x))
            self.config.set("ImageViewer", "gif_con_y", str(self.gif_con_y))
            self.config.set("ImageViewer", "webcon_x", str(self.webcon_x))
            self.config.set("ImageViewer", "webcon_y", str(self.webcon_y))
            self.config.set("ImageViewer", "webpopup_x", str(self.webpopup_x))
            self.config.set("ImageViewer", "webpopup_y", str(self.webpopup_y))
            self.config.set("ImageViewer", "window_width", str(self.window_width))
            self.config.set("ImageViewer", "window_height", str(self.window_height))
            self.config.set("ImageViewer", "window_x", str(self.window_x))
            self.config.set("ImageViewer", "window_y", str(self.window_y))
            self.config.set("ImageViewer", "window_state", self.window_state)
            
        self.config.write(self.config_file)
        self.config_file.close()
        
        # Hide
        self.setting_hide()
        
        # Reset storage and image after changing is_original
        if self.pre_original != self.is_original:
            print("Original setting changed")
            logging.info("Original setting changed")
            
            self.pre_original = self.is_original
            
            if window.is_full_mode:
                
                fulllevel.enter_full()
                fulllevel.stor.stop_storage(True)
                fulllevel.stor.create_reset_storage()
                
            else:
                window.go(window.fullfilelist)    # go() must be put at last, otherwise will stuck in ani

        if self.pre_storage != self.is_storage:     
            self.pre_storage = self.is_storage
            
            if settinglevel.is_storage:                       # from disable to enable cache
                print("Cache Enabled")
                logging.info("Cache Enabled")
                
                self.pre_storage = self.is_storage

                window.clear_all_cache()

                if not window.is_full_mode:             # window mode
                    window.go(window.fullfilelist) 
                    
                else:                                   # full mode
                    fulllevel.enter_full()
                
                    if window.is_manga_mode:            # manga mode
                        fulllevel.quit_manga()
                        fulllevel.start_manga()
            
            else:                                            # from enable to disable cache
                print("Cache Disabled")
                logging.info("Cache Disabled")
                
        # Reset manga storage after changing manga resize 
        if self.pre_manga_resize != self.manga_resize:
            print("Manga resize setting changed")
            logging.info("Manga resize setting changed")
            
            self.pre_manga_resize = self.manga_resize
            
            if window.is_manga_mode:
                fulllevel.manga.stop_storage(True)
                fulllevel.manga.create_reset_storage()
        
        # Apply Always Preview in Photo Album Mode
        if pre_alwayspreview != self.is_alwayspreview:
            if settinglevel.is_alwayspreview and window.is_photoalbum_mode or settinglevel.is_alwayspreview and window.is_manga_mode:
                fulllevel.photo_preview.attributes('-topmost', True)
                fulllevel.photo_preview_visible = True
            
            else:
                fulllevel.photo_preview.attributes('-topmost', False)
                fulllevel.photo_preview_visible = False
                       
    def setting_hide(self):                            # in windw and fullscreen mode
        print("setting_hide")
        logging.info("setting_hide")
        
        try:
            fulllevel.settings_button2.config(text = "Settings", command=settinglevel.setting_buttonclick)
            fulllevel.settings_button3.config(text = "Settings", command=settinglevel.setting_buttonclick)
            fulllevel.settings_button4.config(text = "Settings", command=settinglevel.setting_buttonclick)
            fulllevel.motion1 = fulllevel.popup.bind("<Motion>", fulllevel.motion)
            
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    fulllevel.photo_con.attributes('-topmost', False)
                    
                elif window.is_manga_mode:
                    fulllevel.manga_con.attributes('-topmost', False)
                
                else:
                    fulllevel.full_con.attributes('-topmost', False)
        
        except:
            print("failed to modify settings button or con")
            logging.info("failed to modify settings button or con")
        
        try:
            window.setting_button.config(text = "Settings", command=settinglevel.setting_buttonclick)
        
        except:
            print("failed to modify settings button")
            logging.info("failed to modify settings button")
        
        self.parent.attributes('-topmost', False)
        self.parent.withdraw()
    
    def enhancer_create(self):
        print("enhancer_create") 
        logging.info("enhancer_create")
        
        self.is_iecreated = True
        
        self.ie.resizable(False,False)
        self.ie.overrideredirect(1)
        self.ie.geometry('280x300+%d+%d' %(int(self.ie_x), int(self.ie_y)))
    
        self.ie_frame0 = tk.Frame(self.ie)             
        self.ie_frame0.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
         
        self.ie_frame10 = tk.Frame(self.ie)             
        self.ie_frame10.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.ie_frame11 = tk.Frame(self.ie)             
        self.ie_frame11.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.ie_frame20 = tk.Frame(self.ie)             
        self.ie_frame20.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.ie_frame21 = tk.Frame(self.ie)             
        self.ie_frame21.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.ie_frame22 = tk.Frame(self.ie)             
        self.ie_frame22.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.ie_frame23 = tk.Frame(self.ie)             
        self.ie_frame23.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.ie_frame30 = tk.Frame(self.ie)             
        self.ie_frame30.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.ie_label0 = ttk.Label(self.ie_frame0, text = "" , style='fg.TLabel') # to enable frame0
        self.ie_label0.pack(pady=0, side= tk.LEFT)
        
        self.ie_label10 = ttk.Label(self.ie_frame10, text = "  Apply to Current Image : " , style='fg.TLabel')
        self.ie_label10.pack(pady=0, side= tk.LEFT)

        self.ie_label11 = ttk.Label(self.ie_frame11, text = "  Apply to Next Image : " , style='fg.TLabel')
        self.ie_label11.pack(pady=0, side= tk.LEFT)
        
        self.ie_label20 = ttk.Label(self.ie_frame20, text = "  Brightness : " , style='fg.TLabel')
        self.ie_label20.pack(pady=0, side= tk.LEFT)
        
        self.ie_label21 = ttk.Label(self.ie_frame21, text = "  Contrast : " , style='fg.TLabel')
        self.ie_label21.pack(pady=0, side= tk.LEFT)
        
        self.ie_label22 = ttk.Label(self.ie_frame22, text = "  Sharpness : " , style='fg.TLabel')
        self.ie_label22.pack(pady=0, side= tk.LEFT)
        
        self.ie_label23 = ttk.Label(self.ie_frame23, text = "  Color : " , style='fg.TLabel')
        self.ie_label23.pack(pady=0, side= tk.LEFT)
        
        self.ie_check10 = ttk.Checkbutton(self.ie_frame10, text="", var=self.enhancecurrent_check, command=self.enhancer_click, style = "warning.Roundtoggle.Toolbutton")
        self.ie_check10.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.ie_check11 = ttk.Checkbutton(self.ie_frame11, text="", var=self.enhanceall_check, style = "warning.Roundtoggle.Toolbutton")
        self.ie_check11.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.ie_listbox20 = tk.Listbox(self.ie_frame20, width = 7 , height = 1, highlightthickness=1, font = ("Arial", 10))
        self.ie_listbox20.configure(background='gray20')
        self.ie_listbox20.pack(padx=10, side=tk.RIGHT)
        self.ie_listbox20.insert(5, "  %.2f" %window.brightness)  
        
        self.ie_listbox21 = tk.Listbox(self.ie_frame21, width = 7 , height = 1, highlightthickness=1, font = ("Arial", 10))
        self.ie_listbox21.configure(background='gray20')
        self.ie_listbox21.pack(padx=10, side=tk.RIGHT)
        self.ie_listbox21.insert(5, "  %.2f" %window.contrast)   
        
        self.ie_listbox22 = tk.Listbox(self.ie_frame22, width = 7 , height = 1, highlightthickness=1, font = ("Arial", 10))
        self.ie_listbox22.configure(background='gray20')
        self.ie_listbox22.pack(padx=10, side=tk.RIGHT)
        self.ie_listbox22.insert(5, "  %.2f" %window.sharpness) 
        
        self.ie_listbox23 = tk.Listbox(self.ie_frame23, width = 7 , height = 1, highlightthickness=1, font = ("Arial", 10))
        self.ie_listbox23.configure(background='gray20')
        self.ie_listbox23.pack(padx=10, side=tk.RIGHT)
        self.ie_listbox23.insert(5, "  %.2f" %window.color) 
        
        self.ie_button_decrease20 = tk.Button(self.ie_frame20, text = " - ", command=window.brightness_decrease,width=4)
        self.ie_button_decrease20.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_increase20 = tk.Button(self.ie_frame20, text = " + ", command=window.brightness_increase,width=4)
        self.ie_button_increase20.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_decrease21 = tk.Button(self.ie_frame21, text = " - ", command=window.contrast_decrease,width=4)
        self.ie_button_decrease21.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_increase21 = tk.Button(self.ie_frame21, text = " + ", command=window.contrast_increase,width=4)
        self.ie_button_increase21.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_decrease22 = tk.Button(self.ie_frame22, text = " - ", command=window.sharpness_decrease,width=4)
        self.ie_button_decrease22.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_increase22 = tk.Button(self.ie_frame22, text = " + ", command=window.sharpness_increase,width=4)
        self.ie_button_increase22.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_decrease23 = tk.Button(self.ie_frame23, text = " - ", command=window.color_decrease,width=4)
        self.ie_button_decrease23.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_increase23 = tk.Button(self.ie_frame23, text = " + ", command=window.color_increase,width=4)
        self.ie_button_increase23.pack(side =tk.RIGHT, padx = 5)
        
        self.ie_button_ok = tk.Button(self.ie_frame30, text = "Save and Close", command=self.enhancer_ok,width=15)
        self.ie_button_ok.pack(side =tk.LEFT, pady = 15, padx = 15)
        
        self.ie_button_reset = tk.Button(self.ie_frame30, text = "Reset", command=self.enhancer_reset,width=12)
        self.ie_button_reset.pack(side =tk.LEFT, pady = 15, padx = 15)

        # Enhancer Drag
        self.ie_offsetx = 0
        self.ie_offsety = 0
        self.ie_frame0.bind('<Button-1>', self.enhancer_predrag)
        self.ie_frame0.bind('<B1-Motion>', self.enhancer_drag)
        
    def enhancer_click(self,event=None):
        print("enhancer_click")
        logging.info("enhancer_click")
        
        enhance_current = self.enhancecurrent_check.get()
        
        if event is None:
            if enhance_current:
                window.ShowIMG_ImageEnhance(True)
                
            else:
                window.ShowIMG_ImageEnhance(False)
        
        else:
            if enhance_current:
                enhance_current = False
                settinglevel.enhancecurrent_check.set(False)   
                window.ShowIMG_ImageEnhance(False)
                
            else:
                enhance_current = True
                settinglevel.enhancecurrent_check.set(True)
                window.ShowIMG_ImageEnhance(True)
        
    def enhancer_predrag(self, event):
        print("enhancer_drag")    
        logging.info("enhancer_drag")
        
        self.ie_offsetx = event.x
        self.ie_offsety = event.y
        
    def enhancer_drag(self, event):
        
        self.ie_x = self.ie.winfo_x() + event.x - self.ie_offsetx
        self.ie_y = self.ie.winfo_y() + event.y - self.ie_offsety
    
        self.ie.geometry('+{x}+{y}'.format(x = self.ie_x, y = self.ie_y))

    def enhancer_show(self):
        print("enhancer_show")
        logging.info("enhancer_show")
        
        try:
            window.enhancer_button.config(text = "Hide", command=self.enhancer_hide)
            fulllevel.enhancer_button2.config(text = "Hide", command=self.enhancer_hide)
            fulllevel.enhancer_button3.config(text = "Hide", command=self.enhancer_hide)
        
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    fulllevel.photo_con.attributes('-topmost', True)
                
                else:
                    fulllevel.full_con.attributes('-topmost', True)
                    
        except:
            print("failed to modify enhancer button")
            logging.info("failed to modify enhancer button")
        
        if not self.is_iecreated:
            self.enhancer_create()

        self.ie.deiconify()
        self.ie.attributes('-topmost', True)
        self.ie.update()         # update for the position
    
    def enhancer_ok(self):
        print("enhancer_ok")
        logging.info("enhancer_ok")
        
        self.is_enhanceall = self.enhanceall_check.get()
        
        self.enhancer_hide()
    
    def enhancer_reset(self):
        print("enhancer_reset")
        logging.info("enhancer_reset")
        
        window.brightness = 1
        window.contrast = 1
        window.sharpness = 1
        window.color = 1
        
        settinglevel.ie_listbox20.delete(0)
        settinglevel.ie_listbox20.insert(5, "  %.2f" %window.brightness) 
        settinglevel.ie_listbox21.delete(0)
        settinglevel.ie_listbox21.insert(5, "  %.2f" %window.contrast) 
        settinglevel.ie_listbox22.delete(0)
        settinglevel.ie_listbox22.insert(5, "  %.2f" %window.sharpness) 
        settinglevel.ie_listbox23.delete(0)
        settinglevel.ie_listbox23.insert(5, "  %.2f" %window.color) 
        
        window.ShowIMG_ImageEnhance()
        
    def enhancer_hide(self):                            # in windw and fullscreen mode
        print("enhancer_hide")
        logging.info("enhancer_hide")
        
        try:
            window.enhancer_button.config(text = "Enhance", command=settinglevel.enhancer_show)
            fulllevel.enhancer_button2.config(text = "Enhance", command=settinglevel.enhancer_show)
            fulllevel.enhancer_button3.config(text = "Enhance", command=settinglevel.enhancer_show)
        
        except:
            print("failed to modify enhancer button")
            logging.info("failed to modify enhancer button")
        
        if window.is_full_mode:
            if window.is_photoalbum_mode:
                fulllevel.photo_con.attributes('-topmost', False)
            
            else:
                fulllevel.full_con.attributes('-topmost', False)
                
        self.ie.attributes('-topmost', False)
        self.ie.withdraw()

# In[Exception]

def exception_emptypath():
    
    window.error_label.config(text = "Please input file path")
    logging.warning("Empty file path")
    raise FileNotFoundError("Empty file path")
    
def exception_dirnotfound():
    
    window.error_label.config(text = "Directory not found")
    logging.warning("Directory not found")
    raise FileNotFoundError("Directory not found")
    
def exception_dirnosupportedfile_list():
    
    window.error_label.config(text = "No supported file in the list")
    logging.warning("No supported file in the list")
    raise FileNotFoundError("No supported file in the list") 

def exception_dirnosupportedfile():

    window.error_label.config(text = "No supported file in the directory")
    logging.warning("No supported file in the directory")
    raise FileNotFoundError("No supported file in the directory") 

def exception_dirnopermission():
    
    # including read image and write config
    window.error_label.config(text = "No read permission of the directory")
    logging.warning("No read permission of the directory")
    raise PermissionError("No read permission of the directory") 

def exception_dirtoolarge():
    
    window.error_label.config(text = "Timeout: 20 sec. Try limiting the number of directory searched")
    logging.warning("Timeout: 20 sec. Try limiting the number of directory searched")
    raise RuntimeWarning("Timeout: 20 seconds. Try limiting the number of directory searched") 

def exception_filenotfound():
    
    window.error_label.config(text = "No such file")
    logging.warning("No such file")    
    raise FileNotFoundError("No such file") 
    
def exception_formatnotsupported():
    
    window.error_label.config(text = "File format not supported")
    logging.warning("File format not supported")    
    raise FileNotFoundError("File format not supported") 

def exception_pathtoolong():
    
    window.error_label.config(text = "file path can't exceed 255 characters")
    logging.warning("file path can't exceed 255 characters")  
    raise FileNotFoundError("file path can't exceed 255 characters") 

def exception_settingswrongvalue():
    
    settinglevel.setting_error.config(text = "Not saved: Value must be integer")
    logging.warning("Not saved: Value must be integer")  
    raise ValueError("Value must be integer") 
    
def exception_settingnopermission():
    
    # including read image and write config
    settinglevel.setting_error.config(text = "No write permission of the directory")
    logging.warning("No write permission of the directory")
    raise PermissionError("No write permission of the directory") 

def exception_unidentifiedimage():
    
    # supported format but invalid file
    # PIL.UnidentifiedImageError: cannot identify image file
    logging.warning("PIL.UnidentifiedImageError: cannot identify image file")
    pass   # can't handle module exception
    
# In[Initial]

if __name__ == "__main__":
    # set winfo size to fit with screen size, but the running speed is much slower
    # current winfo size is 1536x864, instead of 1920x1080
    windll.shcore.SetProcessDpiAwareness(0) # your windows version should >= 8.1, otherwise it will raise exception.
    
    logging_create()
    
    default_recursion_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(3100)                           # set recursionlimit. can't be higher as it may crash
    #print("Recursion Limit : ", sys.getrecursionlimit())
    
    tk.Tk.report_callback_exception = exception_override  # override tkinter exception
    # t1 = time.perf_counter()
    
    style = Style(theme='darkly')                             # need manual modification of theme file
    style.configure("primary.TButton", font=("Helvetica", 11,"bold")) # letter button
    style.map("primary.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
    style.configure("window.TButton", font=("Helvetica", 11,"bold")) # letter button
    style.map("window.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
    style.map("my.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
    style.configure("second.TButton", font=("Helvetica", 19)) # unicode symbol button
    style_master = style.master                                         # create window by ttk

    window = WindowGUI(style_master, "window")

    setting = tk.Toplevel(window.parent)
    ie = tk.Toplevel(window.parent)
    settinglevel = SettingGUI(setting, ie, "settinglevel")
    settinglevel.import_settings()
    
    try:
        settinglevel.default_path = sys.argv[1]                 # sys.argv[1] is the image path
        
    except:
        settinglevel.default_path = ""  # if double-click the exe
    
    listbox = tk.Toplevel(window.parent)
    list_canva = tk.Toplevel(window.parent)
    listlevel = ListboxGUI(listbox, list_canva, "listlevel")
    
    full_screen = tk.Toplevel(window.parent)
    full_control = tk.Toplevel(window.parent)
    photoalbum_control = tk.Toplevel(window.parent)
    photoalbum_preview = tk.Toplevel(window.parent)
    manga_control = tk.Toplevel(window.parent)
    fulllevel = FullscreenGUI(full_screen, full_control, photoalbum_control, photoalbum_preview, manga_control, "fulllevel")
    
    listlevel.create_listbox()
    
    window.window_create()            # window gets created after running __init__, so can't call this directly in __init__
    
    listlevel.hide_listbox()          # hide_listbox must be after window_create due to the list button
    
    fulllevel.fullscreen_create()
    
    # t2 = time.perf_counter()
    # print("Open Time: ", t2-t1)
    
    window.mainloop()        # must add at the end to make it run
    
    # garbage collection 
    # https://www.gushiciku.cn/pl/pmzO/zh-tw
    
    listlevel = None
    settinglevel = None
    fulllevel = None
    full_control = None
    photoalbum_control = None
    manga_control = None
    window.gif_con = None
    window = None
    
    sys.setrecursionlimit(default_recursion_limit) # set back to default value
    
    gc.enable()
    
    logging_shutdown()
    
    time.sleep(0.5)              # sleep for 0.5 sec for garbage collection to complete
    #sys.exit()                  # kill main thread only
    os._exit(1)                  # kill all threads
    
# In[things to do]

r''' 
functionality:
manga reader (dm5)
settings tab
settings: download path
preview apply image enhance

optimization:
split into different files
random works before finishing filter
web mode oop
    
bug fix:
skip_chapter should update fullfilelist
fade out can't apply image enhance

known issue which can't be fixed:
[severity: low] some GIF can't get duration (note: replaced by constant 40 in try except)
[severity: minor] can't launch py by double click (note: not affecting usage in exe)
[severity: low] RecursionError: maximum recursion depth exceeded while calling a Python object (note: due to timer and gif. set recursion limit to 3200. can't be higher as it causes stack overflow)
                                - force quit slide mode and photo album mode
                                - manga mode and ani not fixed, suppose no issue if limit is high
                                - use method "after" to split process into other threads instead of one thread
[severity: low] when running gif -> keeping resizing window -> crash (note: has reduced frequency of resizing to minimize the issue)     
[severity: minor] storage can't get ico files (note: the image is shown in ShowIMG_legacy)    
[severity: low] original size incorrect due to dpi awareness (note: dpi set to 125% in windows control panel. it can be modified in dpi awareness, but it will greatly worsen the loading speed)                                                       
[severity: minor] nat sort doesn't work for dir {note: the sorted function does not work for dir in os.walk)
'''

# In[convert to exe]

'''
https://ithelp.ithome.com.tw/articles/10231524

1) Open Windows PowerShell
2) (One-time) Install Python (go to python website to install)
3) (One-time) Install module including tkinter, Pillow, configparser, auto-py-to-exe, pyinstaller, ttkbootstrap, opencv 4.5.3.56, imageio, numpy
4) open auto-py-to-exe
5) 
-- onedir
-- noconfirm
-- icon
-- ascii
-- paths: C:/ProgramData/Anaconda3/lib/site-packages/cv2:C:/ProgramData/Anaconda3/lib/site-packages/imageio
-- collect all: ttkbootstrap

pyinstaller --noconfirm --onedir --windowed --icon "C:/Users/simon/Practice/alpaca_ico.ico" --ascii --paths " C:/ProgramData/Anaconda3/lib/site-packages/cv2:C:/ProgramData/Anaconda3/lib/site-packages/imageio" --collect-all "ttkbootstrap"  "C:/Users/simon/Practice/SimonAlpaca Image Viewer.py"

6) replace imageio folder and ttkbootstrap folder
'''

# In[functionality summary]

'''

'''