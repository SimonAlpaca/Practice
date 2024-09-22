# -*- coding: utf-8 -*-
# author: SimonAlpaca
# project started on 25/8/2021, finished on 3/10/2021

import os
import sys
import traceback
from PIL import Image, ImageTk, ImageSequence, ImageFile
import imageio
import cv2
import numpy as np
import time
import configparser
import logging
import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk
from tkinter import filedialog
from ctypes import windll
import threading
import gc
import random

# In[Logging]

def logging_create():

    exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
    logging_path = os.path.join(exe_dir, "err_handling.log")
    logging.basicConfig(level = logging.DEBUG, filename = logging_path, filemode = "w")
    
def exception_override(self, *args):
    
    err = traceback.format_exception(*args)
    
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
            .ListStor[window.fileindex] = [Image]
            
            Ani:
            .ListStor[window.fileindex][0] = [gif_duration]
            .ListStor[window.fileindex][1] = is_cached  # True or None
            .ListStor[window.fileindex][2:] = [Image of each gif frame]
    '''
    def __init__(self, name):
        
        self.ListStor = []       # window.stor.ListStor or fulllevel.stor.ListStor or fulllevel.manga.ListStor
        self.backend_run = False
        self.pause_backend = False
        self.stop_backend = False
        self.last_index = None
        self.name = name
    
    def create_reset_storage(self):
        
        self.ListStor = [None] * len(window.fullfilelist)
        
    def write_storage(self, fileindex, resize_img):
        
        self.ListStor[fileindex] = resize_img         # write one file when open
        print("Cached: ", self.name, " - ", fileindex)
        logging.info("Cached: %s - %s", self.name, fileindex)
        
    def write_ani_storage(self, fileindex, gif_duration = None, img = None, cached = None):

        if gif_duration is not None:
            self.ListStor[fileindex] = [gif_duration]
            self.ListStor[fileindex].append(None)   # not done cached
        
        if img is not None:
            self.ListStor[fileindex].append(img)
        
        if cached is not None:
            self.ListStor[fileindex][1] = True       # done cached

    def backend_storage(self, fileindex):
        
        try:
            gc.disable()                                   # garbage collection in thread may cause instability
            self.backend_run = True                        # running thread
            storage_range = min(50 + 1, len(window.fullfilelist))
            
            for i in range(storage_range):
                
                while self.pause_backend:
                    time.sleep(0.05)
                
                if self.stop_backend:
                     raise StopIteration
                
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
                    
                    else:
                        self.img_storage(listindex)
    
            print("Auto storage done: ", self.name)         # finish running loop
            logging.info("Auto storage done: %s", self.name)
            self.last_index = listindex        # get last file index
            self.backend_run = False
            
        except StopIteration:                  # kill thread
            print("Auto storage stopped: ", self.name)
            logging.info("Auto storage stopped: %s", self.name)
            self.last_index = None
            self.backend_run = False 
        
        gc.enable()
        
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
                        
                        # simple full mode and slide mode
                        if window.full_w > 1 and window.full_h  > 1:  
                    
                            if settinglevel.is_original:
                                resize_scale = 1
                                
                            else:
                                resize_scale = min(window.full_w / img_w, window.full_h  / img_h)   # calculate the resize ratio, maintaining height-width scale
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
                
                del img
                del resize_img
       
        except StopIteration:                  # kill thread
            print("Auto storage stopped: ", self.name)
            logging.info("Auto storage stopped: %s", self.name)
            self.last_index = None
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
            
            for frame in iter:
                try:
                    frame_duration = frame.info['duration']
                    #if frame_duration < 40:
                     #   frame_duration = 40
                    gif_duration.append(frame_duration)
                
                except:
                    gif_duration.append(40)   # set to 40 if can't find duration

            #print(gif_duration)
            
            del pil_gif
            
            while self.pause_backend:
                time.sleep(0.05)
            
            if self.stop_backend:
                 raise StopIteration
                 
            if window.is_full_mode:
                    
                if window.full_w > 1 and window.full_h  > 1:
                
                    if settinglevel.is_original:
                        resize_scale = 1
                
                    else:
                        resize_scale = min(window.full_w / img_w, window.full_h  / img_h)   # calculate the resize ratio, maintaining height-width scale

            else:
                pic_w, pic_h = window.pic_canvas.winfo_width(), window.pic_canvas.winfo_height()
                
                if settinglevel.is_original:
                    resize_scale = 1
        
                else:
                    resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale

            w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            w_h = (w, h)
            
            cv_gif = imageio.mimread(pic_path, memtest=False)
            
            if self.stop_backend:
                raise StopIteration
                
            self.ListStor[listindex] = [gif_duration]
            self.ListStor[listindex].append(None)
            
            for img in cv_gif:
                img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                self.ListStor[listindex].append(img)
                
                while self.pause_backend:
                    time.sleep(0.05)
                
                if self.stop_backend:
                     raise StopIteration
            
            del img
            del cv_gif
            self.ListStor[listindex][1] = True
            print("Cached: ", self.name , " - ", listindex, " (Ani)")
            logging.info("Cached: %s - %s (Ani)", self.name , listindex)
            
        except StopIteration:                  # kill thread
            print("Auto storage stopped: ", self.name)
            logging.info("Auto storage stopped: %s ", self.name)
            self.last_index = None
            self.backend_run = False 
            
            img = None
            cv_gif = None
            
            try:
                del img
                del cv_gif
            
            except:
                pass
                
    def clear_one_storage(self, fileindex):
        
        self.ListStor[fileindex] = None     # clear one cache
        print("Cache Cleared ", self.name , " - ", fileindex)
        logging.info("Cache Cleared %s - %s ", self.name , fileindex)
        
    def stop_storage(self, is_delete):
        
        self.pause_backend = False
        self.stop_backend = True
        
        if self.backend_run:
            self.thread_storage.join(1)
            print("thread stopped")
            logging.info("thread stopped")
            
        if is_delete:
            self.ListStor = []
            print("Cache Cleared All: ", self.name)
            logging.info("Cache Cleared All: %s", self.name)
            print("garbage collected: ", gc.collect())     # garbage collection        
            logging.info("garbage collected: %s", gc.collect())     # garbage collection  
            
        self.stop_backend = False

# In[GUI]

class WindowGUI(tk.Frame):
    
    def __init__(self, parent):
        
        super().__init__()
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
        self.gc = 0
        self.event_resize_no = 0
        
        self.is_full_mode = False
        self.is_stop_ani = True
        self.zoom_factor = 1
        self.is_slide_check = False
        self.is_photoalbum_mode = False
        self.is_manga_mode = False
        self.is_auto_manga = False
        self.is_timer_pause = False
        
        # Supported format
        self.supported_img = [".jpg", ".jpeg", ".png", ".bmp", ".jfif", ".ico", ".webp"]
        self.supported_ani = [".gif"]
    
        self.supported_img = set(self.supported_img)      # create set
        self.supported_ani = set(self.supported_ani)
        
        self.gif_con = tk.Toplevel(self.parent)
        
    def window_create(self):
        print("window_create")
        logging.info("window_create")
    
        # Window
        self.parent.overrideredirect(True)                                  
        self.parent.geometry('500x580+300+150')                                 # window size  
        self.parent.resizable(width=True,height=True)                   # disallow window resize
        self.parent.title("SimonAlpaca Picture Viewer")                  # title
        self.parent.withdraw()
 
        # Top Frame
        self.top_frame = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.top_frame.pack(pady=1, side = tk.TOP, fill = "both")
        self.quit_button = ttk.Button(self.top_frame, text= "\u03A7", width=3, style='primary.Outline.TButton', command = self.quit)
        self.quit_button.pack(side =tk.RIGHT, padx = 10)
        
        self.max_button = ttk.Button(self.top_frame, text= "\u2587", width=3, style='primary.Outline.TButton', command = self.window_zoomed)
        self.max_button.pack(side =tk.RIGHT, padx = 0)
        
        self.anticlock_button = ttk.Button(self.top_frame, text= "\u2937", width=1, style='primary.TButton', command = self.anticlockwise)
        self.anticlock_button.pack(side =tk.LEFT, padx = 10)
        
        self.clock_button = ttk.Button(self.top_frame, text= "\u2936", width=1, style='primary.TButton', command = self.clockwise)
        self.clock_button.pack(side =tk.LEFT, padx = 5)
        
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)               # when close in taskbar
        
        # Program icon
        try:                                                   
            exe_dir = os.path.split(sys.argv[0])[0]            # sys.argv[0] is the exe path
            ico_path = os.path.join(exe_dir, "Alpaca_ico.ico")
            self.parent.iconbitmap(ico_path)                   # must be parent otherwise can't show program in taskbar   
        
        except:
            pass
        
        # Window Drag
        self.top_frame.bind('<Button-1>', self.window_predrag)
        self.top_frame.bind('<B1-Motion>', self.window_drag)

        # Canvas
        self.pic_canvas = tk.Canvas()
        self.pic_canvas.configure(background='black')
        self.pic_canvas.pack(side=tk.TOP, fill="both", expand=True, pady = 0, padx =10)
        self.pic_canvas.configure(scrollregion = self.pic_canvas.bbox("all"))
     
        # Bottom Button
        self.buttondown_frame = ttk.Frame(self.parent, style='Warning.TFrame')             # add frame first
        self.buttondown_frame.pack(pady=5, side = tk.BOTTOM)
        
        self.check_button = ttk.Checkbutton(self.buttondown_frame, text="Include Subfolder               ", var=settinglevel.parent_check, style = "warning.Roundtoggle.Toolbutton")
        self.check_button.pack(padx = 0, side= tk.RIGHT) 
        
        self.go_button = ttk.Button(self.buttondown_frame, text= "GO", width=12, style='primary.TButton', command= self.go)
        self.go_button.pack(side=tk.RIGHT,padx=10)              # padx means gap of x-axis
        
        self.listbox_button = ttk.Button(self.buttondown_frame, text= "Hide List", width=8, style='primary.TButton', command=listlevel.hide_listbox) # destory to quit
        self.listbox_button.pack(side=tk.LEFT,padx=10)

        self.setting_button = ttk.Button(self.buttondown_frame, text= "Settings", width=8, style='primary.TButton', command=settinglevel.setting_buttonclick) # destory to quit
        self.setting_button.pack(side=tk.LEFT,padx=10)
        
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
        self.browse_button = ttk.Button(self.folder_frame, text = 'Browse', width = 4.2, command=self.browse_file, style='primary.Outline.TButton')
        self.browse_button.pack(side=tk.RIGHT, padx = 2)
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
        
        #self.after(100, self.start)    # run def"start" first
        #self.after(1, self.set_appwindow)    # put window in taskbar
        self.set_appwindow()
        self.gif_con_create()
    
    def browse_file(self):
        print("browse_file")
        logging.info("browse_file")
        
        file_name = filedialog.askopenfilename(filetypes = (("Image files", list(self.supported_img) + list(self.supported_ani)), ("All files", "*")))
        if file_name != "":
        
            self.reset_entry()
            self.folder_entry.insert(1, str(file_name)) 
            
            self.go(file_name)
        
    def window_zoomed(self):
        print("window_zoomed")
        logging.info("window_zoomed")
        
        self.max_button.config(text = "\u2583", command = self.window_normal)
        self.parent.state("zoomed")
        
    def window_normal(self):
        print("window_normal")
        logging.info("window_normal")
        
        self.max_button.config(text = "\u2587", command = self.window_zoomed)
        self.parent.state("normal")
    
    def window_predrag(self, event):
        print("drag_window")    
        logging.info("drag_window")
        
        self.offsetx = event.x
        self.offsety = event.y
        
    def window_drag(self, event):
        
        x = self.parent.winfo_x() + event.x - self.offsetx
        y = self.parent.winfo_y() + event.y - self.offsety
    
        self.parent.geometry('+{x}+{y}'.format(x=x,y=y))
    
    def reset_entry(self):
        print("reset_entry")
        logging.info("reset_entry")
        
        self.folder_entry.delete(0, "end")
        listlevel.listbox1.delete(0, "end")
        self.fullfilelist = []
        
        self.is_stop_ani = True
        self.pic_canvas.delete("all")
        
        window.stor.stop_storage(True)
        fulllevel.stor.stop_storage(True)

    def set_appwindow(self):
        
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
        
        self.parent.state("zoomed")                    # fix bug of "can't bring to back before dragging the window"
        self.parent.state("normal")
        
        if settinglevel.window_state == "normal":
            self.window_normal()
        
        else:
            self.window_zoomed()
        
        self.parent.wm_deiconify()
        self.parent.attributes('-topmost', True)
        self.parent.geometry('%dx%d+%d+%d' %(int(settinglevel.window_width), int(settinglevel.window_height), int(settinglevel.window_x), int(settinglevel.window_y))) # re adjust window size
        self.parent.update()
        
        time.sleep(0.05)                          # perform better after sleep
        self.parent.attributes('-topmost', False)      # force window to the front but not always
    
    def gif_con_create(self):
        
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
        self.gif_offsetx = 0
        self.gif_offsety = 0
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
        
# In[Go Button]
    
    def go(self, file_browse=None):
        print("go")
        logging.info("go")
        
        window.is_full_mode = False
        window.is_stop_ani = True
        window.is_gif_pause = False
        window.zoom_factor = 1
        
        #timer_start = time.perf_counter()
        
        window.origX = window.pic_canvas.xview()[0]                # original canvas position for zoom and move
        window.origY = window.pic_canvas.yview()[0]
        
        window.pic_canvas.bind('<ButtonPress-1>', window.move_from)
        window.pic_canvas.bind('<B1-Motion>', window.move_to)
        
        listlevel.listbox1.delete(0,"end")                         # clear listbox

        filepath = str(window.folder_entry.get())
        #time1 = time.perf_counter()
        window.is_parent = settinglevel.parent_check.get()
        if not os.path.isdir(filepath):              # handle dir path
            filesplit = os.path.split(filepath)           # separate dir path and file name
        
        else:
            filesplit = [filepath, ""]
        
        window.fullfilelist = []
        filename = ""
        
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
                
                if file_ext in (window.supported_img | window.supported_ani):  #filter not support format
                    window.fullfilelist.append(fullpathname)    # full path in list
                
                #else:
                    #print("Not Supported : ", filename)
                    #logging.info("Not Supported : %s", filename)
        
        else:                                        # include sub folder
            file_walk = os.walk(filesplit[0])
            
            timeout_start = time.time()
            timeout = 20
            
            for root,dir,files in file_walk:
                dir.sort()

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
                    
                    if file_ext in (window.supported_img | window.supported_ani):    #filter not support format
                        window.fullfilelist.append(fullpathname)
                    
                    #else:
                     #   if len(file_ext) > 0:
                      #      print("Not Supported : ", file)
                       #     logging.info("Not Supported : %s", file)
        
        if len(window.fullfilelist) == 0:
            exception_dirnosupportedfile()
        
        for path in window.fullfilelist:
            filename = os.path.split(path)
            listlevel.listbox1.insert(tk.END, filename[1])                      # put file name in listbox
        
        window.parent.update()
        
        window.stor.stop_storage(True)
        fulllevel.stor.stop_storage(True)
        window.stor.create_reset_storage()
        fulllevel.stor.create_reset_storage()
        
        try:
            window.fileindex = window.fullfilelist.index(filepath)                 # 0 if filepath is dir
        
        except:
            window.fileindex = 0
        
        filepath = window.fullfilelist[window.fileindex]
        
        if file_browse is not None:                         # when selecting in browse
            filepath = file_browse
            
            if not os.path.splitext(file_browse)[1] in (self.supported_img | self.supported_ani):
                exception_formatnotsupported()
            
        file_ext = os.path.splitext(filepath)[1].lower()      # separate file name and extension
        
        window.folder_entry.delete(0,"end")
        window.folder_entry.insert(1, filepath)             # replace folder entry
        
        #time_diff = time.perf_counter() - timer_start
        window.stor.stop_backend = False
        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
        window.stor.thread_storage.start()
        
        #print(time_diff)
        #time2 = time.perf_counter()
        #print("time diff: ", time2-time1)

        if file_ext in window.supported_img:                 # show in window mode
            window.ShowIMG(filepath)
        
        elif file_ext in window.supported_ani:
            window.ShowANI(filepath)
    
    def nat_sort(self, file):
        
        file_ext = os.path.splitext(file)[1]
        
        if not file_ext in (self.supported_img | self.supported_ani):
            return ["ZZZ"]                                # return a list with any string 
        
        file_name = os.path.splitext(file)[0]             # ignore file ext
        file_name = file_name.lower()                     # ignore upper character

        file_name_list = list(file_name)
        symbols = r"!@#$%^&*()_+={}|<>?[]\"'"
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

        return file_name_list[:]                                  # return whole list. it can sort one by one

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
            fulllevel.stor.stop_storage(True)
            fulllevel.manga.stop_storage(True)
        
        except:
            pass
        
        try:
            del window.fullfilelist
            del window.stor.ListStor
            del fulllevel.stor.ListStor
            del fulllevel.manga.ListStor
        
        except:
            pass
        
        try:
            window.after_cancel(window.thread_resize)     # it can only cancel one resize thread
            
        except:
            pass
        
        window.gif_con.destroy()
        window.parent.destroy()                     # trigger window.mainloop() to end, but it is not necessary to be put at the end
        
# In[Forward Button]
    
    def forward(self, event=None):                                  # all modes except manga mode
        print("forward")
        logging.info("forward")
        
        self.is_stop_ani = True                             # stop previous ani
        self.zoom_factor = 1                             # reset zoom
        is_cached = False
        is_fullcached = False
        self.is_gif_pause = False
        self.rotate_degree = 0
        
        # garbage collection
        # garbage collection can't be put in thread as it may cause crash
        
        self.gc = self.gc + 1
        
        if self.gc > 30 and self.stor.backend_run == False and fulllevel.stor.backend_run == False:
            print("garbage collected: ", gc.collect())
            logging.info("garbage collected: %s", gc.collect())
            self.gc = 0
        
        # get fileindex
        self.fileindex = self.fileindex + 1                    # next file
    
        if self.fileindex == len(self.fullfilelist):           # back to start
            self.fileindex = 0
        
        try:
            nextpath = self.fullfilelist[self.fileindex]          # get path of next file
        
        except IndexError:
            exception_emptypath()
            
        self.cancel_move()    
        self.folder_entry.delete(0,"end")
        self.folder_entry.insert(1, nextpath)             # replace folder entry
        
        # check ext and assign def_ accordingly
        file_ext = os.path.splitext(nextpath)[1].lower()
        if file_ext in self.supported_img:                # img
            
        # check cache
            if self.stor.ListStor[self.fileindex] is not None:
                is_cached = True
            
            if fulllevel.stor.ListStor[self.fileindex] is not None:
                is_fullcached = True  
                          
            if self.is_full_mode:
                
                if self.is_photoalbum_mode:
                    self.ShowIMG_FullPhotoalbum(nextpath)  # Photo Album mode
                
                else:   
                    self.ShowIMG_Full(nextpath, is_fullcached)            # slide mode or simple fullscreen
                    
                    # check if thread should run
                    if fulllevel.stor.last_index is not None and fulllevel.stor.backend_run == False:
                        if abs(fulllevel.stor.last_index - self.fileindex) <= 10 or fulllevel.stor.last_index - window.fileindex + len(window.fullfilelist) <= 10:
                            
                            fulllevel.stor.pause_backend = False
                            
                            print("start fulllevel thread")
                            logging.info("start fulllevel thread")
                            fulllevel.stor.thread_storage = threading.Thread(target = fulllevel.stor.backend_storage, args = (window.fileindex,))
                            
                            fulllevel.stor.stop_backend = False
                            fulllevel.stor.thread_storage.start()
                    
            else:
                self.ShowIMG(nextpath, is_cached)                    # window mode
                
                if window.stor.last_index is not None and window.stor.backend_run == False:
                    if abs(window.stor.last_index - self.fileindex) <= 10 or window.stor.last_index - window.fileindex + len(window.fullfilelist) <= 10:
                        
                        window.stor.pause_backend = False
                        
                        print("start window thread")
                        logging.info("start window thread")
                        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
                        
                        window.stor.stop_backend = False
                        window.stor.thread_storage.start()
                
        else:                                       # gif
            # check cache
            try:
                if self.stor.ListStor[self.fileindex][1] is not None:
                    is_cached = True
            
            except TypeError:
                is_cached = False
            
            try:
                if fulllevel.stor.ListStor[self.fileindex][1] is not None:
                    is_fullcached = True  
           
            except TypeError:
                is_fullcached = False
                
            if self.is_full_mode:
                if fulllevel.stor.last_index is not None and fulllevel.stor.backend_run == False:
                    if abs(fulllevel.stor.last_index - self.fileindex) <= 10 or fulllevel.stor.last_index - window.fileindex + len(window.fullfilelist) <= 10:
                        
                        fulllevel.stor.pause_backend = False
                        
                        print("start fulllevel thread")
                        logging.info("start fulllevel thread")
                        fulllevel.stor.thread_storage = threading.Thread(target = fulllevel.stor.backend_storage, args = (window.fileindex,))
                        
                        fulllevel.stor.stop_backend = False
                        fulllevel.stor.thread_storage.start()
                
                time.sleep(0.05)
                self.ShowANI_Full(nextpath, is_fullcached)             # simple fullscreen, slide mode, Photo Album mode
            
            else:
                if window.stor.last_index is not None and window.stor.backend_run == False:
                    if abs(window.stor.last_index - self.fileindex) <= 10 or window.stor.last_index - window.fileindex + len(window.fullfilelist) <= 10:
                        
                        window.stor.pause_backend = False
                        
                        print("start window thread")
                        logging.info("start window thread")
                        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
                        
                        window.stor.stop_backend = False
                        window.stor.thread_storage.start()
               
                self.ShowANI(nextpath, is_cached)
                
# In[Backward Button]
    
    def backward(self, event=None):                               # all modes except manga mode
        print("backward")
        logging.info("backward")
        
        self.is_stop_ani = True                            # stop previous ani
        self.zoom_factor = 1                            # reset zoom
        is_cached = False
        is_fullcached = False
        self.is_gif_pause = False
        self.rotate_degree = 0
        
        self.fileindex = self.fileindex - 1                  # previous file
        if self.fileindex < 0:                          # back to end
            self.fileindex = len(self.fullfilelist) - 1
        
        try:
            filepath = self.fullfilelist[self.fileindex]         # get path of previous file
        
        except IndexError:
            exception_emptypath()
        
        self.cancel_move()
        
        self.folder_entry.delete(0,"end")
        self.folder_entry.insert(1, filepath)           # replace folder entry
        

            
        file_ext = os.path.splitext(filepath)[1].lower()
        if file_ext in self.supported_img:                 # img
           
            # check cache
            if self.stor.ListStor[self.fileindex] is not None:
                is_cached = True
                
            if fulllevel.stor.ListStor[self.fileindex] is not None:
                is_fullcached = True 
                                         
            if self.is_full_mode:
                
                if self.is_photoalbum_mode:
                    self.ShowIMG_FullPhotoalbum(filepath)   # Photo Album mode
                
                else:   
                    self.ShowIMG_Full(filepath, is_fullcached)            # simple fullscreen or slide mode
            
            else:
                self.ShowIMG(filepath, is_cached)                     # window mode 
                
        else:                                         # gif  
           
            # check cache
            try:
                if self.stor.ListStor[self.fileindex][1] is not None:
                    is_cached = True
            
            except TypeError:
                is_cached = False
            
            try:
                if fulllevel.stor.ListStor[self.fileindex][1] is not None:
                    is_fullcached = True  
            
            except TypeError:
                is_fullcached = False 
                                                           
            if self.is_full_mode:                  
                self.ShowANI_Full(filepath, is_fullcached)                # simple fullscreen, slide mode, Photo Album mode
            
            else:
                self.ShowANI(filepath, is_cached)                     # window mode

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
                
            self.pic_canvas.image = ImageTk.PhotoImage(resize_img)
            self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = self.pic_canvas.image)
            
            self.parent.focus_set()
            
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
            pass  
        
        if not is_cached:
            
            img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            
            try:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            except:
                self.ShowIMG_legacy(pic_path)
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
                
                if self.rotate_degree == 0 and self.zoom_factor == 1:
                    self.stor.write_storage(self.fileindex, resize_img)
                
                del img
                
        else:
            resize_img = self.stor.ListStor[self.fileindex]

        #time_diff = time.perf_counter() - timer_start
        #print("time diff: ", time_diff)
        
        try:      # fix TypeError: Cannot handle this data type: (1, 1, 3), <u2
            self.pic_canvas.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
        
        except TypeError:
            self.ShowIMG_legacy(pic_path)       # change to legacy function and exit this function
            
        self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = self.pic_canvas.image)
        
        self.parent.update()
        self.parent.focus_set()
        
        self.stor.pause_backend = False
        
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
        
        except FileNotFoundError:
            exception_filenotfound()
            
        img_w, img_h = img.size
        
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
            
        fulllevel.pic_canvas.image = ImageTk.PhotoImage(resize_img)
        fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2, anchor="center", image = fulllevel.pic_canvas.image)
        
        img.close()
        resize_img.close()
        del img
        del resize_img
    
        if window.is_slide_check:
            fulllevel.countdown_timer()

    def ShowIMG_Full(self, pic_path, is_fullcached = False):                     # full screen mode
        print("ShowIMG_Full")
        logging.info("ShowIMG_Full")    
        
        #timer_start = time.perf_counter()
        
        fulllevel.stor.pause_backend = True
        window.is_stop_ani = True
        window.error_label.config(text = "")
        
        fulllevel.anticlock_button2.config(state=tk.NORMAL)
        fulllevel.clock_button2.config(state=tk.NORMAL)
        
        self.gif_con.attributes('-topmost', False)
        self.gif_con.withdraw()
        
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        
        if not is_fullcached:
            
            img = cv2.imdecode(np.fromfile(pic_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
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

                if window.rotate_degree == 0 and window.zoom_factor == 1:
                    fulllevel.stor.write_storage(window.fileindex, resize_img)
                
                del img
                
        else:
            resize_img = fulllevel.stor.ListStor[window.fileindex]
        

        #time_diff = time.perf_counter() - timer_start
        #print("time diff: ", time_diff)
        
        try:      # fix TypeError: Cannot handle this data type: (1, 1, 3), <u2
            fulllevel.pic_canvas.image = ImageTk.PhotoImage(image = Image.fromarray(resize_img))
        
        except TypeError:
            self.ShowIMG_Full_legacy(pic_path)
            
        fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2, anchor="center", image = fulllevel.pic_canvas.image)
        
        fulllevel.popup.update()
        
        fulllevel.stor.pause_backend = False
        
        del resize_img
    
        if window.is_slide_check:
            fulllevel.countdown_timer()
    
    # Show Image in Photo Album Mode
    
    def ShowIMG_FullPhotoalbum(self, pic_path):          # Photo Album mode
        print("ShowIMG_FullPhotoalbum")
        logging.info("ShowIMG_FullPhotoalbum")
    
        window.is_stop_ani = True
        window.gif_con.attributes('-topmost', False)
        window.gif_con.withdraw()
        
        fulllevel.anticlock_button3.config(state=tk.NORMAL)
        fulllevel.clock_button3.config(state=tk.NORMAL)
        
        img = Image.open(pic_path)
                
        if window.rotate_degree != 0:                          # skip rotate if haven't clicked rotate
            img = img.rotate(window.rotate_degree, expand = True)
            
        fulllevel.img_w, fulllevel.img_h = img.size

        if window.full_w / fulllevel.img_w >= window.full_h / fulllevel.img_h:                    # if the image is narrower than screen
            resize_scale = window.full_w / fulllevel.img_w                    # calculate the resize ratio, maintaining height-width scale
            w, h = int(fulllevel.img_w * resize_scale), int(fulllevel.img_h * resize_scale)
    
            try:
                resize_img = img.resize((w, h))  
            
            except OSError:                               # fix OSError: image file is truncated
                print("OSError: image file is truncated")
                logging.info("OSError: image file is truncated")      
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                resize_img = img.resize((w, h)) 
                
            fulllevel.pic_canvas.image = ImageTk.PhotoImage(resize_img)
            fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(0, 0, anchor="nw", image = fulllevel.pic_canvas.image) # final pic
            
            img.close()
            resize_img.close()
            del img
            del resize_img
            
            h_diff = h - window.full_h                               # diff between final pic height and full screen height
            fulllevel.move_diff = (h_diff / fulllevel.timer / settinglevel.timer_frame) * -1      # move distance per frame

            time_adj = 0                                    # for timer accurancy
            #time0 = time.perf_counter() + 100
            while window.is_slide_check:
                
                while window.check_timer_pause():            # pause
                    fulllevel.popup.update()
              
                fulllevel.slide_timer = float(fulllevel.check_timer(False))
                #print(fulllevel.slide_timer)

                fulllevel.pic_canvas.move(fulllevel.zoom_pic, 0, fulllevel.move_diff)     # move vertically
                fulllevel.popup.update()
                
                if fulllevel.slide_timer >= settinglevel.default_timer + 2 and window.is_slide_check:
                    fulllevel.fullbackward()
                
                if fulllevel.slide_timer < 0 and window.is_slide_check:  # forward
                    fulllevel.fullforward()
                
                #time_adj = max(0, time.perf_counter() - time0)
                #print("time adj: ", time_adj)
                #print(max(0.001, 1 / settinglevel.timer_frame - time_adj))
                time.sleep(max(0.001, 1 / settinglevel.timer_frame - time_adj))
                #time0 = time.perf_counter()
                
        else:                                                            # if the image is wider than screen
            resize_scale = window.full_h / fulllevel.img_h                    # calculate the resize ratio, maintaining height-width scale
            w, h = int(fulllevel.img_w * resize_scale), int(fulllevel.img_h * resize_scale)
            resize_img = img.resize((w, h))   
            fulllevel.pic_canvas.image = ImageTk.PhotoImage(resize_img)
            fulllevel.zoom_pic = fulllevel.pic_canvas.create_image(0, 0, anchor="nw",image = fulllevel.pic_canvas.image) # final pic
            
            img.close()
            resize_img.close()
            del img
            del resize_img
            
            w_diff = w - window.full_w                            # diff between final pic width and full screen width
            fulllevel.move_diff = (w_diff / fulllevel.timer / settinglevel.timer_frame) * -1   # move distance per frame
            time_adj = 0           # for timer accurancy
            #time0 = time.perf_counter() + 100
            while window.is_slide_check:
                
                while window.check_timer_pause():            # pause
                    fulllevel.popup.update()
                    
                fulllevel.slide_timer = float(fulllevel.check_timer(False))
                #print(fulllevel.slide_timer)
                 
                fulllevel.pic_canvas.move(fulllevel.zoom_pic, fulllevel.move_diff, 0)     # move horizontally
                fulllevel.popup.update()
                
                if fulllevel.slide_timer >= settinglevel.default_timer + 2 and window.is_slide_check: # backward
                    fulllevel.fullbackward()
                
                if fulllevel.slide_timer < 0 and window.is_slide_check:  # forward
                    fulllevel.fullforward()
                
                #time_adj = time.perf_counter() - time0
                #print("time adj: ", time_adj)  
                #print(max(0.001, 1 / settinglevel.timer_frame - time_adj))
                time.sleep(max(0.001, 1 / settinglevel.timer_frame - time_adj))
                #time0 = time.perf_counter()
                
    def check_timer_pause(self):                                 # check if it is paused in zoom-slide mode
        
        if window.is_timer_pause:
            time.sleep(0.1)
            return True
        
        else:
            return False  
        
    def anticlockwise(self, event=None):
        print("anticlockwise")    
        logging.info("anticlockwise")
        
        fulllevel.timer = settinglevel.default_timer                             # reset timer in slide mode
        
        window.rotate_degree = (window.rotate_degree + 90) % 360                  # anti-clockwise
        
        #window.stor.clear_one_storage(window.fileindex)
        
        filepath = window.fullfilelist[window.fileindex]
        
        file_ext = os.path.splitext(filepath)[1].lower()      
        
        if file_ext in window.supported_img:  
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    window.ShowIMG_FullPhotoalbum(filepath)
                
                else:
                    window.ShowIMG_Full(filepath)
            
            else:
                window.ShowIMG(filepath)
        
    def clockwise(self, event=None):
        print("clockwise")    
        logging.info("clockwise")
        
        fulllevel.timer = settinglevel.default_timer                             # reset timer in slide mode
        
        window.rotate_degree = (window.rotate_degree - 90) % 360                  # clockwise
        
        #window.stor.clear_one_storage(window.fileindex)
        
        filepath = window.fullfilelist[window.fileindex]
        
        file_ext = os.path.splitext(filepath)[1].lower()      
        
        if file_ext in window.supported_img:  
            if window.is_full_mode:
                if window.is_photoalbum_mode:
                    window.ShowIMG_FullPhotoalbum(filepath)
                
                else:
                    window.ShowIMG_Full(filepath)
            
            else:
                window.ShowIMG(filepath)
             
# In[Show Animation]
    
    def ShowANI_legacy(self, pic_path, is_cached = False):                       # window mode
        print("ShowANI")
        logging.info("ShowANI")
    
        self.is_stop_ani = False                         # enable running animation
        self.pic_canvas.delete("all")                 # remove existing image
        gif_img = []                             # create list to store frames of gif
        window.gif_speed2 = 1
        window.gif_speed3 = 1
        #self.is_ani_ready = False
        #self.ani_frame = 0
        self.error_label.config(text = "")
        
        self.gif_con.attributes('-topmost', True)
        self.gif_con.focus_set()
        self.gif_con.deiconify()
        
        if len(pic_path) > 255:
            exception_pathtoolong()
        
        #thread_ani_backend = threading.Thread(target = self.ShowANI_backend, args=(pic_path,))
        #thread_ani_backend.start()
        
        try:
            gif_img = Image.open(pic_path)
        
        except FileNotFoundError:
            exception_filenotfound()
        
        iter = ImageSequence.Iterator(gif_img)
        iter_length = len(list(iter))                  # get number of frame of iter
        #print(iter_length)
        del iter
        
        self.parent.update()
        self.parent.focus_set()

        pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()
    
        while not window.is_stop_ani and not window.is_full_mode:          # loop gif until stop
            
            #if not self.is_ani_ready:

                        
            #logging.info("time_check3: %s", time.perf_counter())
            #timer_start2 = time.perf_counter()
            iter = ImageSequence.Iterator(gif_img)   # create iterator to get frames
            i = 0
            
            #if pic_w > 1 and pic_h > 1:    
            img_w, img_h = iter[0].size
            
            if settinglevel.is_original:
                resize_scale = 1

            else:
                resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
            w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            
            #time_diff2 = time.perf_counter() - timer_start2
            #print("time diff start: ", time_diff2)
            #logging.info("time_diff_start: %s", time_diff2)
            total_time_diff = 0
            for frame in iter:
                timer_start = time.perf_counter()
                
                if not window.is_stop_ani: # stop animation controlled by other def
                    i = i + 1
                    #print(i)
                    #logging.info(i)
                    
                    gif_speed = window.check_gifspeed()
                    resize_img = frame.resize((w, h)) 
                    pic = ImageTk.PhotoImage(resize_img)
                    self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = pic)  # create image frame by frame
                    
                    self.parent.update()
                    
                    try:
                        gif_duration = gif_img.info['duration']
                        #print("duration: ", gif_duration)
                            
                    except:
                        gif_duration = 40     # set to 40 if can't find duration
                    
                    if i != iter_length:    # skip sleep for last frame to reduce gif lag issue in exe
                        
                        time_diff = time.perf_counter() - timer_start
                        #print("time diff: ", time_diff)
                           
                        sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.008))
                        sleep_time = min(1, sleep_time)
                        #print("sleep : ", sleep_time)
                    
                        time.sleep(sleep_time)
                    
                    if i == iter_length:
                        #print("Total time diff: " ,total_time_diff)
                        total_time_diff = 0
                    else:
                        total_time_diff = total_time_diff + time_diff

                    resize_img.close()
                    del pic
                    del resize_img
                    
                    #else:
                        #print("sleep : skipped for last frame")
                        
                    #logging.info("time_check1: %s", time.perf_counter())
                    '''
                    if not window.is_stop_ani:
                        logging.info("duration: %s", gif_duration)
                        
                        if i != iter_length:
                            logging.info("time_diff: %s", time_diff)
                            logging.info("sleep : %s", sleep_time)
                        
                        else: 
                            logging.info("sleep : skipped for last frame")
                            '''

                    #logging.info("time_check2: %s", time.perf_counter())
                else:
                    break
        '''    
        else:
            self.ShowANI_2(gif_duration, iter_length)
            '''
                        
                    
        del iter
        del gif_img
        
    def ShowANI(self, pic_path, is_cached = False):                       # window mode
        print("ShowANI")
        logging.info("ShowANI")

        gc.disable()                                     # disable garbage collection
        #time0 = time.perf_counter()
        self.anticlock_button.config(state=tk.DISABLED)
        self.clock_button.config(state=tk.DISABLED)

        self.is_stop_ani = False                         # enable running animation
        self.stor.pause_backend = True
        self.pic_canvas.delete("all")                 # remove existing image
        self.error_label.config(text = "")
        window.gif_speed2 = 1
        window.gif_speed3 = 1
        window.frame_skip = False
        self.gif_con.attributes('-topmost', True)
        self.gif_con.deiconify()

        pic_w, pic_h = self.pic_canvas.winfo_width(), self.pic_canvas.winfo_height()
        
        if is_cached:
            gif_duration = self.stor.ListStor[window.fileindex][0]
            gif_frame = []
            gif_frame = self.stor.ListStor[window.fileindex][2:]
            gif_len = len(gif_frame)

        else:
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
                    gif_duration.append(frame_duration)
                    print(gif_duration)
                except:
                    gif_duration.append(40)   # set to 40 if can't find duration

            #print(gif_duration)

            del pil_gif

            if settinglevel.is_original:
                resize_scale = 1
    
            else:
                resize_scale = min(pic_w / img_w, pic_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
            w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            w_h = (w, h)
            
            cv_gif = imageio.mimread(pic_path, memtest=False)
            
            gif_len = len(cv_gif)
            
            gif_frame = []
            
            self.stor.write_ani_storage(window.fileindex, gif_duration)
            
            for img in cv_gif:
                img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                gif_frame.append(img)
                self.stor.write_ani_storage(window.fileindex, None, img)
            
            self.stor.write_ani_storage(window.fileindex, None, None, True)
            print("Cached: window - ", window.fileindex, " (Ani)")
            logging.info("Cached: window - %s (Ani) ", window.fileindex)
            
            del cv_gif
            
            #self.parent.update()
            #self.parent.focus_set()
            
        #time1 = time.perf_counter()
        #time_diff1 = time1 - time0
        #print("time_diff2: ", time_diff1)
        
        #total_time_diff = 0
        i = 0
        self.stor.pause_backend = False
        while not window.is_stop_ani and not window.is_full_mode:          # loop gif until stop
            
            if window.frame_skip > 0:                                 # skip frame if gif_speed2 is low
               if i % window.frame_skip == 0 and i != gif_len - 1 and i != 0:
                   #print("Skipped :", i)
                   i = (i + 1) % gif_len
                   continue
        
            timer_start = time.perf_counter()

            gif_speed = window.check_gifspeed()
            
            pic = ImageTk.PhotoImage(image = Image.fromarray(gif_frame[i]))
            self.pic_canvas.create_image(pic_w / 2, pic_h / 2, anchor="center", image = pic)  # create image frame by frame
            
            while window.is_gif_pause:               # pause gif
                time.sleep(0.1)
                self.parent.update()
            
            self.parent.update()
            
            #if i != gif_len:    # skip sleep for last frame to reduce gif lag issue in exe
                
            time_diff = time.perf_counter() - timer_start

            #print("time diff: ", time_diff)

            sleep_time = max(0.01, gif_duration[i]/1000 * gif_speed  - (time_diff + 0.008))
            #print("sleep : ", sleep_time)
            sleep_time = min(1, sleep_time)
            
            time.sleep(sleep_time)
            
            if i == gif_len - 1:     # random gif speed
                if settinglevel.random_gifspeed:
                    rad = random.random()
                    window.gif_speed3 = (rad - 0.5) * 0.5 + 1
                    #print(window.gif_speed3)
                

                
            i = (i + 1) % gif_len
            '''
            if i == 0:
                print("Total time diff: " ,total_time_diff)
                total_time_diff = 0
                
            else:
                total_time_diff = total_time_diff + time_diff
            '''
            del pic
        
        del gif_frame
        gc.enable()

# Show Animation in Fullscreen, Slide mode and Photo Album mode
    
    def ShowANI_Full_legacy(self, pic_path):
        print("showANI_Full")
        logging.info("showANI_Full")
        
        window.is_stop_ani = False                         # enable running animation
        window.is_skip_ani = False
        window.gif_speed2 = 1
        window.gif_speed3 = 1
        
        self.gif_con.attributes('-topmost', True)
        self.gif_con.focus_set()
        self.gif_con.deiconify()
        
        window.error_label.config(text = "")
        fulllevel.pic_canvas.delete("all")                 # remove existing image
        
        if window.is_slide_check:
    
            fulllevel.timer = settinglevel.gif_loop     # get timer
        
        gif_img2 = []                             # create list to store frames of gif
        
        if len(pic_path) > 255:
            exception_pathtoolong()
            
        try:
            gif_img2 = Image.open(pic_path)
        
        except FileNotFoundError:
            exception_filenotfound()
        
        iter = ImageSequence.Iterator(gif_img2)
        iter_length = len(list(iter))               # get number of frame of iter
        del iter
        total_time_diff = 0
        while not window.is_stop_ani and window.is_full_mode:          # loop gif until stop
            #timer_start2 = time.perf_counter()
            iter = ImageSequence.Iterator(gif_img2)   # create iterator to get frames
            i = 0
            
            img_w, img_h = iter[0].size
            
            if settinglevel.is_original:
                resize_scale = 1
    
            else:
                resize_scale = min(window.full_w / img_w, window.full_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
            w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            
            #time_diff2 = time.perf_counter() - timer_start2
            #print("time diff start: ", time_diff2)
            #logging.info("time_diff_start: %s", time_diff2)
            
            for frame in iter:
                timer_start = time.perf_counter()
                
                if not window.is_stop_ani: # stop animation controlled by other def
                    i = i + 1
                    #print(i)
                    #logging.info(i)
                    
                    if window.is_skip_ani:                         # skip ani in slide mode
                        fulllevel.timer = fulllevel.check_timer(True)                 # control timer and countdown
                
                        if fulllevel.timer <= 0 and window.is_slide_check:
                            fulllevel.fullforward()                        # forward
                        
                        if fulllevel.timer > settinglevel.default_timer and window.is_slide_check:
                            fulllevel.fullbackward()                        # forward
                    
                    gif_speed = window.check_gifspeed()
                    resize_img = frame.resize((w, h))
                    pic = ImageTk.PhotoImage(resize_img)
                    fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2,anchor="center",image = pic)  # create image frame by frame
                    
                    while window.is_gif_pause:               # pause gif
                        time.sleep(0.1)
                        fulllevel.popup.update()
                    
                    fulllevel.popup.update()
                    
                    try:
                        gif_duration = gif_img2.info['duration']
                        
                    except:
                        gif_duration = 40
                    
                    if i != iter_length:    # skip sleep for last frame to reduce gif lag issue in exe
                        time_diff = time.perf_counter() - timer_start
                        #print("time diff: ", time_diff)
                        
                        sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.008))
                        #print("sleep : ", sleep_time)
                        sleep_time = min(1, sleep_time)
                        while window.is_gif_pause:
                            time.sleep(sleep_time)
                            
                    else:
                        if settinglevel.random_gifspeed:
                            rad = random.random()
                            window.gif_speed3 = (rad - 0.5) * 0.4 + 1
                            print(window.gif_speed3)
                        
                    if i == iter_length:
                        print("Total time diff: " ,total_time_diff)
                        total_time_diff = 0
                    else:
                        total_time_diff = total_time_diff + time_diff
                    
                    #else:
                        #print("sleep : skipped for last frame")
                    '''    
                    if not window.is_stop_ani:
                        logging.info("duration: %s", gif_duration)
                        
                        if i != iter_length:
                            logging.info("time_diff: %s", time_diff)
                            logging.info("sleep : %s", sleep_time)
                        
                        else: 
                            logging.info("sleep : skipped for last frame")
                            '''
                else:
                    break
                
            if window.is_slide_check:
                fulllevel.timer = fulllevel.check_timer(True)                 # control timer and countdown
    
                if fulllevel.timer <= 0 and window.is_slide_check:
                    fulllevel.fullforward()                        # forward
                
                if fulllevel.timer > settinglevel.gif_loop and window.is_slide_check:
                    fulllevel.fullbackward()                        # backward
        
        del iter
        del gif_img2
        del pic
        del resize_img
    
    def ShowANI_Full(self, pic_path, is_fullcached = False):                       # window mode
        print("showANI_Full")
        logging.info("showANI_Full")
        
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
        self.gif_con.attributes('-topmost', True)
        self.gif_con.deiconify()

        window.error_label.config(text = "")
        fulllevel.pic_canvas.delete("all")                 # remove existing image
        
        if window.is_slide_check:
            fulllevel.timer = settinglevel.gif_loop     # get timer
        
        if is_fullcached:
            gif_duration = fulllevel.stor.ListStor[window.fileindex][0]
            gif_frame = []
            gif_frame = fulllevel.stor.ListStor[window.fileindex][2:]
            gif_len = len(gif_frame)
            
        else:
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
                    gif_duration.append(frame_duration)
                
                except:
                    gif_duration.append(40)   # set to 40 if can't find duration

            #print(gif_duration)
                
            del pil_gif
            
            if settinglevel.is_original:
                resize_scale = 1
    
            else:
                resize_scale = min(window.full_w / img_w, window.full_h / img_h)   # calculate the resize ratio, maintaining height-width scale
            
            w, h = int(img_w * resize_scale), int(img_h * resize_scale)
            w_h = (w, h)
            
            cv_gif = imageio.mimread(pic_path, memtest=False)
            
            gif_len = len(cv_gif)
            
            self.stor.write_ani_storage(window.fileindex, gif_duration)
            
            gif_frame = []
            
            for img in cv_gif:
                img = cv2.resize(img, w_h, interpolation = cv2.INTER_AREA)
                gif_frame.append(img)
                self.stor.write_ani_storage(window.fileindex, None, img)
                
            self.stor.write_ani_storage(window.fileindex, None, None, True)
            print("Cached: full - ", window.fileindex, " (Ani)")
            logging.info("Cached: full - %s (Ani) ", window.fileindex)
            
            del cv_gif
        self.stor.pause_backend = False
        
        #total_time_diff = 0
        i = 0
        while not window.is_stop_ani and window.is_full_mode:          # loop gif until stop
            
            if window.frame_skip > 0:                                  # skip frame if gif_speed2 is low
                if i % window.frame_skip == 0 and i != gif_len - 1 and i != 0:
                    #print("Skipped :", i)
                    i = (i + 1) % gif_len
                    continue
                
            timer_start = time.perf_counter()    
            
            gif_speed = window.check_gifspeed()

            pic = ImageTk.PhotoImage(image = Image.fromarray(gif_frame[i]))
            fulllevel.pic_canvas.create_image(window.full_w / 2, window.full_h / 2,anchor="center",image = pic)  # create image frame by frame
            
            while window.is_gif_pause:               # pause gif
                time.sleep(0.1)
                fulllevel.popup.update()
                
            fulllevel.popup.update()
            
            #if i != gif_len:    # skip sleep for last frame to reduce gif lag issue in exe
                
            time_diff = time.perf_counter() - timer_start

            #print("time diff: ", time_diff)
               
            sleep_time = max(0.001, gif_duration[i]/1000 * gif_speed - (time_diff + 0.008))
            #print("sleep : ", sleep_time)

            if window.is_slide_check and settinglevel.random_gifloop and i == gif_len - 1: # min 2.5 sec sleep for last frame in random gif loop, otherwise 1 sec
                sleep_time = min(2.5, sleep_time)
            
            else:
                sleep_time = min(1, sleep_time)
                
            time.sleep(sleep_time)
            
            if i == gif_len - 1:     # Random gif speed
                if settinglevel.random_gifspeed:
                    rad = random.random()
                    window.gif_speed3 = (rad - 0.5) * 0.5 + 1
                    
            i = (i + 1) % gif_len
            
            if window.is_skip_ani:                         # skip ani in slide mode
                fulllevel.timer = fulllevel.check_timer(True, gif_duration[gif_len - 1])                 # control timer and countdown
        
                if fulllevel.timer <= 0 and window.is_slide_check:
                    fulllevel.fullforward()                        # forward
                
                if fulllevel.timer > settinglevel.gif_loop and window.is_slide_check:
                    fulllevel.fullbackward()                        # backward
            
            if i == 0 and window.is_slide_check:
                fulllevel.timer = fulllevel.check_timer(True, gif_duration[gif_len - 1])                 # control timer and countdown
    
                if fulllevel.timer <= 0 and window.is_slide_check:
                    fulllevel.fullforward()                        # forward
                
                if fulllevel.timer > settinglevel.gif_loop and window.is_slide_check:
                    fulllevel.fullbackward()                        # backward
            '''
            if i == 0:
                print("Total time diff: " ,total_time_diff)
                total_time_diff = 0
           
            else:
                total_time_diff = total_time_diff + time_diff
            '''
            del pic
        
        del gif_frame  
        gc.enable()
        
    def check_gifspeed(self):
        
        # gif_speed : gif speed in settings
        # gif_speed2 : manually controlled gif speed
        # gif_speed3 : random generated after checking random gif speed
        # print(settinglevel.gif_speed)
        # print(window.gif_speed2)
        # print(window.gif_speed3)
        
        return settinglevel.gif_speed * window.gif_speed2 * window.gif_speed3

    def gif_speedup(self, event=None):
        
        window.gif_speed2 = round(max(0.1, window.gif_speed2 - 0.15), 2)
        
        if window.gif_speed2 == 0.55:
            window.frame_skip = 8
        
        elif window.gif_speed2 == 0.4:
            window.frame_skip = 5

        elif window.gif_speed2 == 0.25:
            window.frame_skip = 3

        elif window.gif_speed2 == 0.1:
            window.frame_skip = 2
            
        else:
            window.frame_skip = False
            
        #print("Gif Speed Up: ", window.gif_speed2, "; Frame Skip : ", window.frame_skip)
        logging.info("Gif Speed Up: %.2f", window.gif_speed2)
    
    def gif_speeddown(self, event=None):
        
        window.gif_speed2 = round(min(2.5, window.gif_speed2 + 0.15), 2)
        
        if window.gif_speed2 == 0.55:
            window.frame_skip = 8
        
        elif window.gif_speed2 == 0.4:
            window.frame_skip = 5

        elif window.gif_speed2 == 0.25:
            window.frame_skip = 3

        elif window.gif_speed2 == 0.1:
            window.frame_skip = 2
            
        else:
            window.frame_skip = False
            
        #print("Gif Speed Down: ", window.gif_speed2, "; Frame Skip : ", window.frame_skip)
        logging.info("Gif Speed Down: %.2f", window.gif_speed2)
        
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
        
        window.stor.stop_storage(False)       
        fulllevel.stor.stop_storage(False)  
        
        window.stor.stop_backend = True        # force stop backend to avoid crash 
        fulllevel.stor.stop_backend = True
        
        x1 = self.parent.winfo_pointerx()
        y1 = self.parent.winfo_pointery()
        x0 = self.parent.winfo_rootx()
        y0 = self.parent.winfo_rooty()
       
        self.parent.geometry("%sx%s" % ((x1-x0),(y1-y0))) # for resizing the window
        
    def event_resize(self, event=None):          # window mode
        
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
    
                    filepath = str(self.folder_entry.get())
                    file_ext = os.path.splitext(filepath)[1].lower()              # separate file name and extension
                    
                    if file_ext in self.supported_img:
                        self.ShowIMG(filepath)
                    
                    #elif file_ext in supported_ani:
                     #   ShowANI(filepath)                # can't resize ani
                    
                    time.sleep(0.05)                      # reduce the frequency of event_resize
                    self.time_resize = time.perf_counter()
                    self.thread_resize = self.after(3000, self.thread_AfterResize) # trigger thread restart after 3 sec
        
        window.stor.stop_backend = False
        fulllevel.stor.stop_backend = False
    
    def thread_AfterResize(self):
        print("After: ", time.perf_counter()- self.time_resize)
        logging.info("After: %s", time.perf_counter()- self.time_resize)
        
        if time.perf_counter() - self.time_resize >= 3:
            if not window.stor.backend_run and len(window.fullfilelist) > 0:
                window.stor.stop_backend = False
                window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
                window.stor.thread_storage.start()
        
# In[When Zoom]
    
    def event_zoom(self, event):                  # window mode or full screen mode         
        print("event_zoom")
        logging.info("event_zoom")
        
        x = self.pic_canvas.canvasx(event.x)
        y = self.pic_canvas.canvasy(event.y)
            
        if event.delta > 1:                           # scroll up
            window.zoom_factor = window.zoom_factor + 0.2
        
        else:                                         # scroll down
            window.zoom_factor = max(window.zoom_factor - 0.2, 1)
        
        filepath = str(window.folder_entry.get())
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext in window.supported_img:                 # skip gif
            if window.is_full_mode:                            
                self.ShowIMG_Full(filepath)
        
            else:                                             # move in window mode only
                self.ShowIMG(filepath)
       
            try:
                self.pic_canvas.scale(tk.ALL, x, y, window.zoom_factor, window.zoom_factor) 
            
            except:
                pass                                    # exception when slide mode -> zoom -> quit
            
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
        
    def move_from(self, event):
            
        self.pic_canvas.scan_mark(event.x, event.y)
    
    def move_to(self, event):
        
        self.pic_canvas.scan_dragto(event.x, event.y, gain=1)
    
# In[fullscreen mode]

class FullscreenGUI(WindowGUI):
    
    def __init__(self, popup, full_con, photo_con, manga_con):
        
        self.popup = popup
        self.full_con = full_con
        self.photo_con = photo_con
        self.manga_con = manga_con
        self.popup.withdraw()         # to avoid extra window pop up
        self.full_con.withdraw()        # to avoid extra window pop up
        self.photo_con.withdraw()       # to avoid extra window pop up
        self.manga_con.withdraw()       # to avoid extra window pop up
        self.is_fullcreated = False
        self.stor = Storage("fulllevel")
        
        window.is_slide_check = False
        window.is_photoalbum_mode = False
        
    def enter_full(self):
        
        window.is_full_mode = True
        window.is_stop_ani = True

        if not self.is_fullcreated:
            self.fullscreen_create()
            
        self.photo_con.deiconify()
        self.manga_con.deiconify()
        self.full_con.deiconify()
        self.popup.deiconify()
        self.popup.geometry("%dx%d+0+0" % (window.full_w, window.full_h))
        
        window.parent.attributes('-topmost', False)
        self.popup.focus_set()    
        
        try:
            settinglevel.setting_hide()
        
        except:
            pass
        
        listlevel.hide_listbox()
        
        if len(window.fullfilelist) == 0:
            exception_emptypath()
        
        window.stor.stop_storage(False)       

        self.stor.thread_storage = threading.Thread(target = self.stor.backend_storage, args = (window.fileindex,))
        
        self.stor.stop_backend = False
        self.stor.thread_storage.start()    
        
        filepath = window.fullfilelist[window.fileindex] 
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if not window.is_manga_mode and not window.is_photoalbum_mode:
            if file_ext in window.supported_img:                     # full screen mode
                window.ShowIMG_Full(filepath)
            
            else:
                window.ShowANI_Full(filepath) 
        
    def fullscreen_create(self):
        print("fullscreen")
        logging.info("fullscreen")
        
        self.is_fullcreated = True
        
        # GUI of Fullscreen
        self.popup.resizable(False,False)
        self.popup.overrideredirect(1)

        self.button_esc = self.popup.bind("<Escape>", self.quit_full)
        self.button1 = self.popup.bind("<Button-1>", self.fullforward)
        self.button3 = self.popup.bind("<Button-3>", self.fullbackward)
        self.wheel = self.popup.bind("<MouseWheel>", self.event_zoom)            # trigger zoom event
        self.popup.bind("<Up>", self.gif_speedup)
        self.popup.bind("<Down>", self.gif_speeddown)
        self.button_forward = self.popup.bind("<Right>", self.fullforward)
        self.button_backward = self.popup.bind("<Left>", self.fullbackward)
        self.p_button = self.popup.bind("<p>", window.gif_pause)
        self.s_button = self.popup.bind("<s>", fulllevel.start_slide)
        self.a_button = self.popup.bind("<a>", fulllevel.start_photoalbum)
        self.m_button = self.popup.bind("<m>", fulllevel.start_manga)
    
        self.pic_canvas = tk.Canvas(self.popup, width = window.full_w, height = window.full_h, highlightthickness = 0)
        self.pic_canvas.pack()
        self.pic_canvas.configure(background='black')
        self.pic_canvas.configure(scrollregion = self.pic_canvas.bbox("all"))
        
        # Controller in fullscreen
        s = ttk.Style()
        s.configure('my.TButton', font=('Arial', 13))
        
        self.full_con.resizable(False,False)
        self.full_con.overrideredirect(1)
        self.full_con.geometry("950x50+%d+%d" % (window.full_w / 2- 950 /2, window.full_h - 64))
        
        self.listbox_button2 = ttk.Button(self.full_con, text = "List", style='primary.TButton', command = listlevel.show_listbox, width=8)
        self.listbox_button2.pack(side =tk.LEFT, padx = 5)
        
        self.settings_button2 = ttk.Button(self.full_con, text = "Settings", style='primary.TButton', command = settinglevel.setting_buttonclick, width=8)
        self.settings_button2.pack(side=tk.LEFT,padx= 25)

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
        self.photo_con.geometry("650x50+%d+%d" % (window.full_w / 2 - 650/2, window.full_h - 64))
        
        self.listbox_button3 = ttk.Button(self.photo_con, text = "List", style='primary.TButton', command = listlevel.show_listbox, width=8)
        self.listbox_button3.pack(side =tk.LEFT, padx = 5)
        
        self.settings_button3 = ttk.Button(self.photo_con, text = "Settings", style='primary.TButton', command = settinglevel.setting_buttonclick, width=8)
        self.settings_button3.pack(side=tk.LEFT,padx= 15)

        self.anticlock_button3 = ttk.Button(self.photo_con, text= "\u2937", width=3, command= window.anticlockwise, style='my.TButton')
        self.anticlock_button3.pack(side =tk.LEFT, padx = 5)
        
        self.clock_button3 = ttk.Button(self.photo_con, text= "\u2936", width=3, command= window.clockwise, style='my.TButton')
        self.clock_button3.pack(side =tk.LEFT, padx = 10)
        
        self.backward_button3 = ttk.Button(self.photo_con, text= u"\u2B98", width=3, command= self.fullbackward, style='my.TButton')
        self.backward_button3.pack(side =tk.LEFT, padx = 10)
        
        self.forward_button3 = ttk.Button(self.photo_con, text= u"\u2B9A", width=3, command= self.fullforward, style='my.TButton')
        self.forward_button3.pack(side =tk.LEFT, padx = 5)
        
        self.quit_button3 = ttk.Button(self.photo_con, text= "\u03A7", width=3, style='my.TButton', command = self.quit_photoalbum)
        self.quit_button3.pack(side =tk.RIGHT, padx = 5)
        
        self.auto_button3 = ttk.Button(self.photo_con, text= "\u23ef", width=6, style='my.TButton', command = self.pause_auto)
        self.auto_button3.pack(side =tk.RIGHT, padx = 15)
        
        # Controller in manga mode
        self.manga_con.resizable(False,False)
        self.manga_con.overrideredirect(1)
        self.manga_con.geometry("650x50+%d+%d" % (window.full_w / 2- 650 /2, window.full_h - 64))
        
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
        
        self.quit_button4 = ttk.Button(self.manga_con, text= "\u03A7", width=3, style='my.TButton', command = self.quit_manga)
        self.quit_button4.pack(side =tk.RIGHT, padx = 5)
        
        self.auto_button4 = ttk.Button(self.manga_con, text= "\u23ef", width=6, style='my.TButton', command = self.auto_scrollmanga)
        self.auto_button4.pack(side =tk.RIGHT, padx = 15)
        
        self.motion1 = self.popup.bind("<Motion>", self.motion)                          # control appearance controller
   
    def fullforward(self, event=None):                           # full screen mode
        print("fullforward")    
        logging.info("fullforward")
        
        self.pic_canvas.delete("all")
        
        self.timer = settinglevel.default_timer 
        
        try:
            window.forward()
        
        except RecursionError as e:                           # force quit slide or photoalbum to fix recursion error
            print("RecursionError : ", e)
            logging.error("RecursionError: maximum recursion depth exceeded while calling a Python object")
            
            if window.is_slide_check and not window.is_photoalbum_mode:
                self.quit_slide()
                window.forward()
            
            elif window.is_slide_check and window.is_photoalbum_mode:
                self.quit_photoalbum()
    
    def fullbackward(self, event=None):                           # full screen mode
        print("fullbackward")  
        logging.info("fullbackward")
        
        self.pic_canvas.delete("all")
    
        self.timer = settinglevel.default_timer
        
        window.backward()
        
    def back_simple_full(self):           # from slide mode, Photo Album, manga to simple fullscreen
        print("back_simple_full")
        logging.info("back_simple_full")
        
        try:
            self.popup.unbind("<s>",fulllevel.s_button2)
        
        except:
            pass
        
        self.s_button = self.popup.bind("<s>", fulllevel.start_slide)
        self.a_button = self.popup.bind("<a>", fulllevel.start_photoalbum)
        self.m_button = self.popup.bind("<m>", fulllevel.start_manga)
        
        window.is_slide_check = False
        window.is_photoalbum_mode = False
        window.is_manga_mode = False
        window.is_auto_manga = False
        fulllevel.timer = settinglevel.default_timer                       # reset timer
        
        fulllevel.pic_canvas.delete("all")                    # remove existing image
        
        pic_path = window.fullfilelist[window.fileindex]
        
        file_ext = os.path.splitext(pic_path)[1].lower()      # separate file name and extension
            
        if file_ext in window.supported_img:     
            window.ShowIMG_Full(pic_path)                    # back to simple full screen
        
        elif file_ext in window.supported_ani:
            window.ShowANI_Full(pic_path)                    # back to simple full screen
    
    def quit_full(self, event=None):                              # from full screen mode to window mode
        print("quit_full")
        logging.info("quit_full")    
    
        window.is_slide_check = False 
        window.is_full_mode = False
        
        fulllevel.popup.withdraw()                                 # close full screen and controller
        fulllevel.full_con.withdraw()
        
        try:
            settinglevel.setting_hide()
        
        except:
            pass
        
        try:
            fulllevel.quit_slide()
            
        except:
            pass
        
        listlevel.hide_listbox()
        
        filepath = str(window.folder_entry.get())              # refresh root window
        file_ext = os.path.splitext(filepath)[1].lower()                  
        
        if file_ext in window.supported_img:
            window.ShowIMG(filepath)
        
        elif file_ext in window.supported_ani:
            window.ShowANI(filepath)                
        
        fulllevel.stor.stop_storage(False)  
        
        window.stor.thread_storage = threading.Thread(target = window.stor.backend_storage, args = (window.fileindex,))
        
        window.stor.stop_backend = False
        window.stor.thread_storage.start()
        
    def motion(self, event):                      # simple full screen or slide mode
        
        y = event.y                          # mouse pointer location
        
        if y > window.full_h - 70:
            if window.is_photoalbum_mode:
                self.photo_con.focus_set()                          # show controller
                print("show photo_con")
            
            elif window.is_manga_mode:
                self.manga_con.focus_set()                          # show controller
            
            else:
                self.full_con.focus_set()                          # show controller
            
        if y < window.full_h - 70:
            self.popup.focus_set()                           # hide controller
    
# In[Auto slide mode]
    
    def start_slide(self, event=None):                        # slide mode or Photo Album mode
        print("start_slide")
        logging.info("start_slide")

        self.slide_button2.config(text = "Stop Slide", command=self.quit_slide)
        self.photoalbum_button2.config(state=tk.DISABLED)
        self.manga_button2.config(state=tk.DISABLED)
        self.popup.unbind("<m>", self.m_button)
        self.popup.unbind("<a>", self.a_button)
        self.popup.unbind("<s>", self.s_button)
        self.s_button2 = self.popup.bind("<s>", self.quit_slide)

        
        window.is_slide_check = True
        window.is_timer_pause = False
        
        self.timer = settinglevel.default_timer
        
        filepath = window.fullfilelist[window.fileindex] 
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if not window.is_photoalbum_mode:                          # slide mode
            self.popup.unbind("<Button-1>", self.button1)
            self.popup.unbind("<Button-3>", self.button3)
            self.left_slide_button = self.popup.bind("<Button-1>", self.leftclick_slide)
            self.right_slide_button = self.popup.bind("<Button-3>", self.rightclick_slide)
            
            if file_ext in window.supported_img:                    
                window.ShowIMG_Full(filepath)
            
            else:
                window.ShowANI_Full(filepath)
    
    def leftclick_slide(self, event):
        
        self.timer = self.timer - settinglevel.default_timer - settinglevel.gif_loop
        window.is_skip_ani = True
        
    def rightclick_slide(self, event):
        
        self.timer = self.timer + settinglevel.default_timer + settinglevel.gif_loop + 2
        window.is_skip_ani = True
    
    def countdown_timer(self):                       # ShowIMG_full only, to fix "crash in slide mode when click fast for 200+ times"
        print("countdown_timer")
        logging.info("countdown_timer")
        time0 = time.perf_counter() + 100            # make negative value for first frame

        while self.check_timer(False) >= 0 and window.is_slide_check: # check and control timer
            self.popup.update()

            if self.timer > settinglevel.default_timer and window.is_slide_check:    # forward
                self.fullbackward()
            
            time_adj = max(0, time.perf_counter() - time0)
            
            try:
                time.sleep(1 / settinglevel.timer_frame - time_adj)                     # maintain frame
            
            except ValueError:        # no sleep if negative value
                pass
                
        time0 = time.perf_counter()
            
        if self.timer < 0 and window.is_slide_check:    # forward
            self.fullforward()
            
    def check_timer(self, is_ani, duration=None):                                  # timer in slide mode or Photo Album mode   
        
        #print("timer:", format(timer, ".3f"), end= " ")
        #logging.info("timer: %s", timer)
        
        if not is_ani:                                            # from ShowIMG_Full and ShowIMG_Fullphotoalbum
            self.timer = self.timer - 1 / settinglevel.timer_frame
            #print(self.timer)
            return self.timer
            
        else:                                                      # from ShowANI_Full
            if settinglevel.random_gifloop:                         # forward if last frame's duration is at least 1000
                if duration >= 1000:
                    self.timer = 0
                
                else:
                    rad = random.random()
                    percentage = 0.15
                    
                    # timer = gif_loop
                    if rad > (1 - percentage):                                      # 20% -2; 60% -1; 20% -0
                        self.timer = max(0, self.timer - 2)                   
                        
                    elif rad > percentage:
                        self.timer = self.timer - 1
                        
                    else:
                        self.timer = self.timer - 0
                
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

        try:
            settinglevel.setting_hide()
        
        except:
            pass
        
        listlevel.hide_listbox()

        self.popup.unbind("<Escape>", self.button_esc)
        self.popup.unbind("<MouseWheel>", self.wheel)
        self.popup.unbind("<Button-1>", self.button1)
        self.popup.unbind("<Button-3>", self.button3)
        self.popup.unbind("<Right>", self.button_forward)
        self.popup.unbind("<Left>", self.button_backward)
        
        self.pause_button = self.popup.bind("<Button-1>", self.pause_auto)
        self.updown_wheel = self.popup.bind("<MouseWheel>", self.wheel_photoalbum)
        self.esc_quit_photoalbum = self.popup.bind("<Escape>", self.quit_photoalbum)
        self.backward_button_photoalbum = self.popup.bind("<Up>", self.backward_photoalbum)
        self.forward_button_photoalbum = self.popup.bind("<Down>", self.forward_photoalbum)
        self.clockwise_button_photoalbum = self.popup.bind("<Right>", window.clockwise)
        self.anticlockwise_button_photoalbum = self.popup.bind("<Left>", window.anticlockwise)
        
        fulllevel.stor.pause_backend = True
        window.is_photoalbum_mode = True
        window.is_slide_check = True
        
        self.timer = settinglevel.default_timer
        
        self.popup.focus_set()
        
        self.pic_canvas.delete("all") 
        
        self.start_slide()                                 # use common definition as slide mode
        
        self.popup.unbind("<s>", self.s_button2)
        
        pic_path = window.fullfilelist[window.fileindex]
        file_ext = os.path.splitext(pic_path)[1].lower()      # separate file name and extension
        
        if file_ext in window.supported_img:
            self.ShowIMG_FullPhotoalbum(pic_path)           # Photo Album mode
        
        elif file_ext in window.supported_ani:
            self.ShowANI_Full(pic_path)                    # same as full mode for gif
           
    def quit_photoalbum(self, event=None):                          # Photo Album mode
        print("quit_photoalbum")    
        logging.info("quit_photoalbum")
 
        self.popup.unbind("<Button-1>", self.pause_button)
        self.popup.unbind("<MouseWheel>", self.updown_wheel)
        self.popup.unbind("<Escape>", self.esc_quit_photoalbum)
        self.popup.unbind("<Up>", self.backward_button_photoalbum)
        self.popup.unbind("<Down>", self.forward_button_photoalbum)
        self.popup.unbind("<Right>", self.clockwise_button_photoalbum)
        self.popup.unbind("<Left>", self.anticlockwise_button_photoalbum)

        #self.motion1 = self.popup.bind("<Motion>", self.motion)                          # control appearance controller 
        self.button_esc = self.popup.bind("<Escape>", self.quit_full)
        self.wheel = self.popup.bind("<MouseWheel>", self.event_zoom)  
        self.button_forward = self.popup.bind("<Right>", self.fullforward)
        self.button_backward = self.popup.bind("<Left>", self.fullbackward)
        
        settinglevel.setting_hide()
        listlevel.hide_listbox()
        fulllevel.photo_con.attributes('-topmost', False)  

        fulllevel.stor.pause_backend = False
        
        self.quit_slide()
        
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
        
        fulllevel.slide_timer = -1

    def backward_photoalbum(self, event=None):
        print("backward_photoalbum")
        logging.info("backward_photoalbum")
        
        fulllevel.slide_timer = settinglevel.default_timer + 100
        
# In[Manga Mode]
    
    def start_manga(self, event=None):
        print("start_manga")
        logging.info("start_manga")

        try:
            settinglevel.setting_hide()
        
        except:
            pass
        
        listlevel.hide_listbox()
        
        self.popup.unbind("<a>", self.a_button)
        self.popup.unbind("<m>", self.m_button)
        self.popup.unbind("<s>", self.s_button)
        self.popup.unbind("<Button-1>", self.button1)
        self.popup.unbind("<Button-3>", self.button3)
        self.popup.unbind("<Escape>", self.button_esc)
        self.popup.unbind("<MouseWheel>", self.wheel)
        self.popup.unbind("<Right>", self.button_forward)
        self.popup.unbind("<Left>", self.button_backward)
        
        self.auto_button = self.popup.bind("<Button-1>", self.auto_scrollmanga)
        self.updown_wheel_manga = self.popup.bind("<MouseWheel>", self.scroll_manga)
        self.esc_quit_manga = self.popup.bind("<Escape>", self.quit_manga)
        self.backward_button_manga = self.popup.bind("<Up>", self.backward_manga)
        self.forward_button_manga = self.popup.bind("<Down>", self.forward_manga)
        
        window.is_stop_ani = True
        window.is_manga_mode = True
        window.is_auto_manga = False
        fulllevel.stor.pause_backend = True
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
        h1                                                     
          [manga_top] resized_h1 |  pre_mangaindex                 
        h2                                                   0             full_w
          [manga_mid] resized_h2 |  mangaindex                 [pic_canvas]
        h3                                               full_h
          [manga_bot] resized_h3 |  next_mangaindex
        h4  
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
        resize_img = img.resize((self.resized_w2, self.resized_h2))   
        globals()['image_%s' % window.fileindex] = ImageTk.PhotoImage(resize_img)
        self.w2 = int((1- settinglevel.manga_resize) / 2 * window.full_w)
        globals()['manga_%s' % window.fileindex] = self.pic_canvas.create_image(self.w2, self.h2,anchor="nw",image=globals()['image_%s' % window.fileindex])
        
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
        
        try:
            
            if event.delta > 1:                      # manual scroll
                scroll = "up"
            
            else:
                scroll = "down"
        
        except:                                      
            if forward_backward >= 0:                 # auto scroll and forward
                scroll = "up"
            
            else:                                     # backward
                scroll = "down"
                
        if scroll == "up":                           # scroll up, move up
            self.pic_canvas.move(globals()['manga_%s' % window.pre_mangaindex], 0, scroll_dis * -1)
            self.pic_canvas.move(globals()['manga_%s' % window.fileindex], 0, scroll_dis * -1)     
            
            try:                                # for multi-thread in auto scroll
                self.pic_canvas.move(globals()['manga_%s' % window.next_mangaindex], 0, scroll_dis * -1)
            
            except:
                pass
            
            self.h1 = self.h1 - scroll_dis
            self.h2 = self.h2 - scroll_dis
            self.h3 = self.h3 - scroll_dis
            self.h4 = self.h4 - scroll_dis

        if scroll == "down":                         # scroll down, move down      
            self.pic_canvas.move(globals()['manga_%s' % window.pre_mangaindex], 0, scroll_dis * 1)
            self.pic_canvas.move(globals()['manga_%s' % window.fileindex], 0, scroll_dis * 1)     
            self.pic_canvas.move(globals()['manga_%s' % window.next_mangaindex], 0, scroll_dis * 1)
            
            self.h1 = self.h1 + scroll_dis
            self.h2 = self.h2 + scroll_dis
            self.h3 = self.h3 + scroll_dis
            self.h4 = self.h4 + scroll_dis

        if self.h3 < 0:                             # scroll up, forward

            while True:
                window.fileindex = window.fileindex + 1
                
                if window.fileindex == len(window.fullfilelist):
                    window.fileindex = 0
                    
                pic_path = window.fullfilelist[window.fileindex]
                file_ext = os.path.splitext(pic_path)[1].lower()
                if file_ext in window.supported_img:
                    break

            self.h1 = self.h2
            self.h2 = self.h3
            self.h3 = self.h4
            
            self.show_manga_bot()
            '''
            if auto == 0:                       # manual scroll, multi thread can't work well if moving fast
                self.show_manga_bot()
            
            else:                               # auto scroll, multi thread to prevent lag
                thread1 = threading.Thread(target = self.show_manga_bot)
                thread1.start()
                '''
            # check if thread should run
            if self.manga.last_index is not None and self.manga.backend_run == False:
                if abs(self.manga.last_index - window.fileindex) <= 10 or self.manga.last_index - window.fileindex + len(window.fullfilelist) <= 10:
                    
                    self.manga.pause_backend = False
                    
                    print("start manga thread")
                    logging.info("start manga thread")
                    self.manga.thread_storage = threading.Thread(target = self.manga.backend_storage, args = (window.fileindex,))
                    
                    self.manga.stop_backend = False
                    self.manga.thread_storage.start()
            
            self.pic_canvas.delete(globals()['manga_%s' % window.pre_mangaindex])
            del globals()['manga_%s' % window.pre_mangaindex]               # del to release resource
            del globals()['image_%s' % window.pre_mangaindex]
            print("Remove: ",  ['manga_%s' % window.pre_mangaindex])
            logging.info("Remove: %s",  ['manga_%s' % window.pre_mangaindex])
            
            self.h4 = self.h3 + self.resized_h3
            
            while True:
                window.pre_mangaindex = window.pre_mangaindex + 1
                
                if window.pre_mangaindex == len(window.fullfilelist):           # back to start
                    window.pre_mangaindex = 0
                
                pic_path = window.fullfilelist[window.pre_mangaindex]
                file_ext = os.path.splitext(pic_path)[1].lower()
                
                if file_ext in window.supported_img:
                    break
            
        if self.h2 > window.full_h:                            # full_h = 865

            while True:
                window.fileindex = window.fileindex - 1
                
                if window.fileindex < 0:                          # back to end
                    window.fileindex = len(window.fullfilelist) - 1
                    
                pic_path = window.fullfilelist[window.fileindex]
                file_ext = os.path.splitext(pic_path)[1].lower()
                
                if file_ext in window.supported_img:
                    break
                       
            self.h4 = self.h3
            self.h3 = self.h2
            self.h2 = self.h1
            
            self.show_manga_top()
            
            self.pic_canvas.delete(globals()['manga_%s' % window.next_mangaindex])
            del globals()['manga_%s' % window.next_mangaindex]              # del to release resource
            del globals()['image_%s' % window.next_mangaindex]
            print("Remove: ",  ['manga_%s' % window.next_mangaindex])
            logging.info("Remove: %s",  ['manga_%s' % window.next_mangaindex])
            
            self.h1 = self.h2 - self.resized_h1
            
            while True:
                window.next_mangaindex = window.next_mangaindex - 1           # scroll down, backward
                
                if window.next_mangaindex < 0:                          # back to end
                    window.next_mangaindex = len(window.fullfilelist) - 1
                
                pic_path = window.fullfilelist[window.next_mangaindex]
                file_ext = os.path.splitext(pic_path)[1].lower()
                
                if file_ext in window.supported_img:
                    break
    
    def auto_scrollmanga(self, event=None):                         # auto scroll
        print("auto_manga")
        logging.info("auto_manga")
        
        if window.is_auto_manga:
            window.is_auto_manga = False
        
        else:
            window.is_auto_manga = True
            
        while window.is_auto_manga:
            self.scroll_manga(None, settinglevel.auto_dis)
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

        self.popup.unbind("<Button-1>", self.auto_button)
        self.popup.unbind("<MouseWheel>", self.updown_wheel_manga)
        self.popup.unbind("<Escape>", self.esc_quit_manga)
        self.popup.unbind("<Up>", self.backward_button_manga)
        self.popup.unbind("<Down>", self.forward_button_manga)
        self.button_forward = self.popup.bind("<Right>", self.fullforward)
        self.button_backward = self.popup.bind("<Left>", self.fullbackward)
        
        #self.motion1 = self.popup.bind("<Motion>", self.motion)                          # control appearance controller 
        self.button_esc = self.popup.bind("<Escape>", self.quit_full)
        self.button1 = self.popup.bind("<Button-1>", self.fullforward)
        self.button3 = self.popup.bind("<Button-3>", self.fullbackward)
        self.wheel = self.popup.bind("<MouseWheel>",self.event_zoom) 
        
        del globals()['manga_%s' % window.pre_mangaindex]               # del to release resource
        del globals()['manga_%s' % window.fileindex]                   # del to release resource
        del globals()['manga_%s' % window.next_mangaindex]             # del to release resource
        del globals()['image_%s' % window.pre_mangaindex]               # del to release resource
        del globals()['image_%s' % window.fileindex]                   # del to release resource
        del globals()['image_%s' % window.next_mangaindex]              # del to release resource
        
        print("garbage collected: ", gc.collect()) # return no. of unreachable object which will be collected
        logging.info("garbage collected: %s", gc.collect()) 
        
        filepath = window.fullfilelist[window.fileindex]
        window.folder_entry.delete(0,"end")
        window.folder_entry.insert(1, filepath)               # reset folder entry
        
        fulllevel.stor.pause_backend = False
        
        settinglevel.setting_hide()
        listlevel.hide_listbox()
        fulllevel.manga_con.attributes('-topmost', False)  
       
        self.back_simple_full()
    
# In[Listbox]
class ListboxGUI():
    
    def __init__(self, parent):
        self.parent = parent
        
    def create_listbox(self):
        print("create_listbox")    
        logging.info("create_listbox")

        self.parent.resizable(False,False)
        self.parent.overrideredirect(1)
        self.parent.geometry('250x550+%d+%d' %(int(settinglevel.listbox_x), int(settinglevel.listbox_y)))    # re adjust list position
        
        self.listbox_scroll = ttk.Scrollbar(self.parent, orient='vertical', style="Vertical.TScrollbar") 
        self.listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.w, self.h = self.parent.winfo_screenwidth(), self.parent.winfo_screenheight()
        self.listbox1 = tk.Listbox(self.parent, width = self.w - 80, height = self.h, highlightthickness=5, selectmode = tk.SINGLE, yscrollcommand = self.listbox_scroll.set)
        self.listbox1.configure(background='black')
        self.listbox1.pack(side=tk.LEFT)
        
        self.listbox_scroll.config(command = self.listbox1.yview)
        
        self.listbox1.bind("<Double-Button-1>", self.select_listbox)
        
        # Listbox Drag
        self.list_offsetx = 0
        self.list_offsety = 0
        self.listbox1.bind('<Button-1>', self.listbox_predrag)
        self.listbox1.bind('<B1-Motion>', self.listbox_drag)
    
    def listbox_predrag(self, event):
        print("drag_listbox")    
        logging.info("drag_listbox")
        
        self.list_offsetx = event.x
        self.list_offsety = event.y
        
    def listbox_drag(self, event):
        
        self.x = self.parent.winfo_x() + event.x - self.list_offsetx
        self.y = self.parent.winfo_y() + event.y - self.list_offsety
    
        self.parent.geometry('+{x}+{y}'.format(x=self.x,y=self.y))
    
    def show_listbox(self):                          # in window and fullscreen mode
        print("show_listbox")    
        logging.info("show_listbox")
        
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
        
        self.parent.attributes('-topmost', True)
        window.listbox_button.config(text = "Hide List", command=self.hide_listbox)
        self.parent.deiconify()
        self.listbox1.focus_set()
        
    def select_listbox(self, event):
        print("select_listbox")
        logging.info("select_listbox")
        
        is_cached = False
        is_fullcached = False
        window.is_gif_pause = False
        window.stor.pause_backend = True
        window.fileindex = self.listbox1.curselection()[0]     # select on listbox, return integer
        filepath = window.fullfilelist[window.fileindex]
        window.folder_entry.delete(0,"end")
        window.folder_entry.insert(1, filepath)           # replace folder entry
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
        
        if file_ext in window.supported_img:
            if window.stor.ListStor[window.fileindex] is not None:
                is_cached = True
            window.ShowIMG(filepath, is_cached)
        
        elif file_ext in window.supported_ani:
            try:
                if window.stor.ListStor[window.fileindex][1] is not None:
                    is_cached = True
            except TypeError:
                is_cached = False
            

            window.ShowANI(filepath, is_cached)   
    
    def select_full_mode(self, filepath, file_ext, is_fullcached):
       
        fulllevel.stor.stop_storage(False)  
        
        fulllevel.stor.thread_storage = threading.Thread(target = fulllevel.stor.backend_storage, args = (window.fileindex,))
        
        fulllevel.stor.stop_backend = False
        fulllevel.stor.thread_storage.start()
        
        if file_ext in window.supported_img:
            if fulllevel.stor.ListStor[window.fileindex] is not None:
                is_fullcached = True
            window.ShowIMG_Full(filepath, is_fullcached)
        
        elif file_ext in window.supported_ani:
            
            try:
                if fulllevel.stor.ListStor[window.fileindex][1] is not None:
                    is_fullcached = True  
            except TypeError:
                is_fullcached = False
                
            window.ShowANI_Full(filepath, is_fullcached) 
    
    def select_photo_mode(self, filepath, file_ext):
        
        if file_ext in window.supported_img:
            window.ShowIMG_FullPhotoalbum(filepath)  # Photo Album mode
    
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
        
        self.parent.attributes('-topmost', False)
        
        try:
            window.listbox_button.config(text = "List", command=self.show_listbox)
        
        except:
            pass
        
        self.parent.withdraw()

# In[Settings]
class SettingGUI():
    
    def __init__(self, parent):
        self.parent = parent
        self.is_settingcreated = False
        
        self.parent.withdraw()
        
    def import_settings(self):
        print("import_settings") 
        logging.info("import_settings")
        
        # Default Settings
        # window mode
        self.window_width = 500
        self.window_height = 580
        self.window_x = 300
        self.window_y = 150
        self.window_state = "normal"
    
        self.listbox_x = 50
        self.listbox_y = window.full_h - 700
        
        self.setting_x = window.full_w - 350 - 100
        self.setting_y = window.full_h - 500 - 150
        
        self.gif_con_x = window.full_w - 1500
        self.gif_con_y = window.full_h - 200
        
        self.parent_check = tk.BooleanVar()
        self.is_parent = False
        self.parent_check.set(False)                        # include subfolder
        
        self.natsort_check = tk.BooleanVar()
        self.is_natsort = False
        self.natsort_check.set(False)                       # natural sort
        
        self.original_check = tk.BooleanVar()
        self.is_original = False
        self.original_check.set(False)                        # original size
        
        self.randomgifspeed_check = tk.BooleanVar()
        self.random_gifspeed = False
        self.randomgifspeed_check.set(False)                        # original size
        
        self.randomgifloop_check = tk.BooleanVar()
        self.random_gifloop = False
        self.randomgifloop_check.set(False)                        # original size
        
        self.gif_speed = 1.0
        
        # simple fullscreen mode
        
        # slide mode and photo album mode
        self.default_timer = 5                              # timer for images
        self.gif_loop = 3                                   # times of gif loop for each slide
        
        # photo album mode
        self.timer_frame = 50                               # frame of image move
        
        # phto album mode and manga mode
        self.scroll_multiplier = 0.7                        # scroll distance, equal to half second
        
        # manga mode
        self.manga_resize = 1                               # width in manga mode
        self.auto_frame = 50                                # frame of auto manga
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
        self.random_gifspeed = self.getconfig("randomgifspeed_check", self.random_gifspeed)
        self.randomgifspeed_check.set(self.random_gifspeed)
        self.is_original = self.getconfig("original_check", self.is_original)
        self.original_check.set(self.is_original)
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
        self.gif_con_x = str(self.getconfig("gif_con_x", self.gif_con_x))
        self.gif_con_y = str(self.getconfig("gif_con_y", self.gif_con_y))
        
        self.pre_original = self.is_original
        self.pre_manga_resize = self.manga_resize

    def getconfig(self, column, var):
        
        try:
            if self.config.get("ImageViewer", str(column)) == "False":
                return False                   # return boolean as all strings are deemed True
            
            else:
                return self.config.get("ImageViewer", str(column))
        
        except:
            return var
    
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
            pass
        
        window.setting_button.config(text = "Hide", command=self.setting_hide)

        if self.is_settingcreated == False:
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
        self.parent.geometry('350x600+%d+%d' %(int(self.setting_x), int(self.setting_y)))    # re adjust list position
    
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
        self.setting_frame5.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
        
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
        self.setting_frame21.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
        
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
        self.setting_scroll31 = tk.OptionMenu(self.setting_frame31, self.setting_imagesize, "Normal", "Large", "Fullscreen")
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
            
        # manga mode
        self.setting_imagesizestr = self.setting_imagesize.get()
        if self.setting_imagesizestr == "Fullscreen":        # width in manga mode
            self.manga_resize = 1
        
        elif self.setting_imagesizestr == "Large":
            self.manga_resize = 0.85
        
        elif self.setting_imagesizestr == "Normal":
            self.manga_resize = 0.7
        
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
        
        self.gif_con_x = window.gif_con.winfo_x()
        self.gif_con_y = window.gif_con.winfo_y()
        
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
            self.config.set("ImageViewer", "randomgifspeed_check", str(self.random_gifspeed))
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
            self.config.set("ImageViewer", "gif_con_x", str(self.gif_con_x))
            self.config.set("ImageViewer", "gif_con_y", str(self.gif_con_y))
            
            if window.parent.state() == "zoomed":
                self.window_state = "zoomed"
                self.config.set("ImageViewer", "window_state", self.window_state)
                
            else:
                self.window_state = "normal"
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
                fulllevel.stor.stop_storage(True)
                fulllevel.stor.create_reset_storage()
                
                fulllevel.enter_full()
                
            else:
                window.go()                                # go() must be put at last, otherwise will stuck in ani
        
        # Reset manga storage after changing manga resize 
        if self.pre_manga_resize != self.manga_resize:
            print("Manga resize setting changed")
            logging.info("Manga resize setting changed")
            
            self.pre_manga_resize = self.manga_resize
            
            if window.is_manga_mode:
                fulllevel.manga.stop_storage(True)
                fulllevel.manga.create_reset_storage()
                       
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
            pass
        
        try:
            window.setting_button.config(text = "Settings", command=settinglevel.setting_buttonclick)
        
        except:
            pass
        
        self.parent.attributes('-topmost', False)
        self.parent.withdraw()
 
# In[Exception]

def exception_emptypath():
    
    window.error_label.config(text = "Please input file path")
    logging.warning("Empty file path")
    raise FileNotFoundError("Empty file path")
    
def exception_dirnotfound():
    
    window.error_label.config(text = "Directory not found")
    logging.warning("Directory not found")
    raise FileNotFoundError("Directory not found")

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
        
    logging_create()
    
    sys.setrecursionlimit(3100)                           # set recursionlimit. can't be higher as it may crash
    #print("Recursion Limit : ", sys.getrecursionlimit())
    
    tk.Tk.report_callback_exception = exception_override  # override tkinter exception
    #t1 = time.perf_counter()
    
    style = Style(theme='darkly')                             # need manual modification of theme file
    style.configure("primary.TButton", font=("Helvetica", 11,"bold")) # letter button
    style.map("primary.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
    style.map("my.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
    style.configure("second.TButton", font=("Helvetica", 19)) # unicode symbol button
    style_master = style.master                                         # create window by ttk

    window = WindowGUI(style_master)
    
    setting = tk.Toplevel(window.parent)
    settinglevel = SettingGUI(setting)
    settinglevel.import_settings()
    
    try:
        settinglevel.default_path = sys.argv[1]                 # sys.argv[1] is the image path
        
    except:
        settinglevel.default_path = ""  # if double-click the exe
    
    listbox = tk.Toplevel(window.parent)
    listlevel = ListboxGUI(listbox)
    
    full_screen = tk.Toplevel(window.parent)
    full_control = tk.Toplevel(window.parent)
    photoalbum_control = tk.Toplevel(window.parent)
    manga_control = tk.Toplevel(window.parent)
    fulllevel = FullscreenGUI(full_screen, full_control, photoalbum_control, manga_control)
    
    window.window_create()            # window gets created after running __init__, so can't call this directly in __init__

    listlevel.create_listbox()
    listlevel.hide_listbox()
    
    filepath = str(window.folder_entry.get())
        
    if filepath != "":
        window.go()
        
    #t2 = time.perf_counter()
    
    #print("Open Time: ", t2-t1)
    window.mainloop()        # must add at the end to make it run
    
    # garbage collection 
    # https://www.gushiciku.cn/pl/pmzO/zh-tw
    
    listlevel = None
    settinglevel = None
    fulllevel = None
    window = None
    
    gc.enable()
    
    logging_shutdown()
    
    time.sleep(0.5)              # sleep for 0.5 sec for garbage collection to complete
    #sys.exit()                  # kill main thread only
    os._exit(1)                  # kill all threads
    
# In[things to do]

r''' 
functionality:
    
optimization:
faster open program after clicking pic
check object name and optimize oop
more accurate timer (need more testing)

bug fix:

known bugs which can't be fixed:
[severity: low] GIF can't be resized upon window resize
[severity: low] some GIF can't get duration (note: replaced by constant 40 in try except)
[severity: minor] can't launch py by double click (note: not affecting usage in exe)
[severity: low] RecursionError: maximum recursion depth exceeded while calling a Python object (note: due to timer and gif. set recursion limit to 3200. can't be higher as it causes stack overflow)
                                - force quit slide mode and photo album mode
                                - manga mode and ani not fixed, suppose no issue if limit is high                                                                
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