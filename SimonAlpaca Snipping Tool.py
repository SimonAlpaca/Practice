# -*- coding: utf-8 -*-
# Project started on 5/11/2022

import os
import sys
import time
import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk, filedialog
from ctypes import windll
import mss
import cv2
import numpy as np
import PIL
import imageio
from io import BytesIO
import win32clipboard
import configparser
import win32gui
import threading
import screeninfo
import logging
import traceback

# In[GUI]
class WindowGUI(tk.Frame):
    
    def __init__(self, parent):
        print("window.__init__")
        logging.info("window.__init__")
        
        super().__init__()
        self.parent = parent
        self.to_dir = ""
        
        self.select_range = None
        self.image_mode = False
        self.video_mode = False
        self.is_hidden = False
        self.temp_img = None
        self.temp_vid = None
        self.top = None
        self.mouse_pointer = []
        
        # get width and height of all screens
        list_monitors = screeninfo.get_monitors()     # generate list of each monitor
        # print(list_monitors)
        
        self.bottom_right_x = 0
        self.bottom_right_y = 0
        
        self.top_left_x = list_monitors[0].x
        self.top_left_y = list_monitors[0].y
        
        for monitor in list_monitors:
            
            self.bottom_right_x =  max(self.bottom_right_x, monitor.x + monitor.width)
            self.bottom_right_y =  max(self.bottom_right_y, monitor.y + monitor.height)
        
        self.total_width = self.bottom_right_x - self.top_left_x
        self.total_height = self.bottom_right_y - self.top_left_y
        
        # print(top_left_x)
        # print(top_left_y)
        # print(bottom_right_x)
        # print(bottom_right_y)
        
         # GUI of Settings and Import
        self.import_settings()
        self.setting_create()
        
        # GUI of Parent Window
        self.window_create()
        
        # GUI of Select Area
        self.select_area_create()
        
        # GUI of Select Area Controller
        self.select_controller_create()
        
        # GUI of Video Cap
        self.video_create()
    
    def window_create(self):
        print("window_create")
        logging.info("window_create")
        
        style.configure("primary.TButton", font=("Helvetica", 9,"bold")) # letter button
        style.map("primary.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
        
        self.parent.overrideredirect(True)                                  
        self.parent.geometry('330x90+%s+%s' %(self.window_x, self.window_y))                                 # window size  
        self.parent.resizable(width=False,height=False)                   # disallow window resize
        self.parent.title("SimonAlpaca Snipping Tool")                  # title
        self.parent.withdraw()
        
        self.frame_top1 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_top1.pack(pady=1, side = tk.TOP, fill = "both")
        self.quit_button = ttk.Button(self.frame_top1, text= "\u03A7", width=3, style='primary.Outline.TButton', command = self.quit)
        self.quit_button.pack(side =tk.RIGHT, padx = 10)
        self.progress_text = tk.Text(self.frame_top1, height=1, width=25, background='gray25')
        self.progress_text.pack(side=tk.LEFT, padx = 10, pady = 5)
        
        self.frame_mid1 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_mid1.pack(pady=1, side = tk.TOP, fill = "both")
        
        self.frame_bot = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_bot.pack(pady=1, side = tk.TOP, fill = "both")
        self.frame_bot2 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_bot2.pack(pady=0, side = tk.TOP, fill = "both")
        
        self.image_button = ttk.Button(self.frame_mid1, text= "Image", width=10, style='primary.TButton', command= self.image_button_click)
        self.image_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")              # padx means gap of x-axis
        self.vid_button = ttk.Button(self.frame_mid1, text= "Video/GIF", width=10, style='primary.TButton', command= self.video_button_click)
        self.vid_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")              # padx means gap of x-axis
        self.settings_button = ttk.Button(self.frame_mid1, text= "Settings", width=10, style='primary.TButton', command= self.setting_buttonclick)
        self.settings_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")  
        self.save_button = ttk.Button(self.frame_mid1, text= "Save", width=10, style='primary.TButton', command= self.save_button_click)
        self.save_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")  
        self.copy_button = ttk.Button(self.frame_mid1, text= "Copy", width=10, style='primary.TButton', command= self.copy_canvas)
        self.copy_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")  
        
        self.preview_canvas = tk.Canvas(self.frame_bot, width=900,height=600,scrollregion=(0,0,self.total_width + 20, self.total_height + 20), highlightthickness = 5)
        self.preview_canvas.pack(side=tk.LEFT)
        self.preview_canvas.configure(background='black')
        
        self.parent.bind('<Control-c>', self.copy_canvas)
        
        self.preview_scroll_y = ttk.Scrollbar(self.frame_bot, orient='vertical', command=self.preview_canvas.yview)
        self.preview_scroll_y.pack(side=tk.RIGHT, fill='y')
        self.preview_canvas['yscrollcommand'] = self.preview_scroll_y.set
        
        self.preview_scroll_x = ttk.Scrollbar(self.frame_bot2, orient='horizontal', command=self.preview_canvas.xview)
        self.preview_scroll_x.pack(side=tk.BOTTOM, fill='x')
        self.preview_canvas['xscrollcommand'] = self.preview_scroll_x.set
        
        # Window Drag
        self.frame_top1.bind('<Button-1>', self.window_predrag)
        self.frame_top1.bind('<B1-Motion>', self.window_drag)
                
        # Program icon
        try:                                                   
            exe_dir = os.path.split(sys.argv[0])[0]            # sys.argv[0] is the exe path
            ico_path = os.path.join(exe_dir, "g12-snipping_97305.ico")
            self.parent.iconbitmap(ico_path)                   # must be parent otherwise can't show program in taskbar   
        
        except:
            pass
        
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)               # when close in taskbar
        
        self.parent.update()

    def window_changesize(self, width, height):
        print("window_changesize")
        logging.info("window_changesize")
        
        adj_width = 560 + max(0, min(800, width - 560))
        adj_height = 90 + 30 + max(0, min(500, height))      # 30 for the scrollbar
        
        adj_canva_width = 560 - 30 + max(0, min(800, width - 560))
        adj_canva_height = 0 + max(0, min(500, height))
        
        self.parent.geometry('%sx%s+200+150' %(adj_width, adj_height))           # window size  
        self.preview_canvas.configure(width = adj_canva_width, height = adj_canva_height)
        
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
        self.after(100, self.show_appwindow)
    
    def show_appwindow(self):
        print("show_appwindow")
        logging.info("show_appwindow")
        
        self.parent.state("zoomed")                    # fix bug of "can't bring to back before dragging the window"
        self.parent.state("normal")
        
        self.parent.wm_deiconify()
        self.parent.attributes('-topmost', True)
        
        self.parent.update()
        
        time.sleep(0.05)                          # perform better after sleep
        self.parent.attributes('-topmost', False)      # force window to the front but not always 
        
    def window_predrag(self, event):
        
        self.offsetx = event.x
        self.offsety = event.y
        
    def window_drag(self, event):
        
        x = self.parent.winfo_x() + event.x - self.offsetx
        y = self.parent.winfo_y() + event.y - self.offsety
    
        self.parent.geometry('+{x}+{y}'.format(x=x,y=y))
    
    def window_hide(self):
        print("window_hide")
        logging.info("window_hide")
        
        if not self.is_hidden:       # not update value if hidden
            self.window_x = self.parent.winfo_x()
            self.window_y = self.parent.winfo_y()
            
        self.is_hidden = True
        self.parent.geometry('+{x}+{y}'.format(x=-1500,y=-1500))
        
        self.parent.update()
        
    def window_unhide(self):
        print("window_unhide")
        logging.info("window_unhide")
        
        self.is_hidden = False
        
        self.parent.geometry('+{x}+{y}'.format(x= self.window_x ,y= self.window_y))
        
        self.parent.update()
        
    def video_predrag(self, event):
        
        self.video_offsetx = event.x
        self.video_offsety = event.y
        
    def video_drag(self, event):
        
        x = self.video.winfo_x() + event.x - self.video_offsetx
        y = self.video.winfo_y() + event.y - self.video_offsety
    
        self.video.geometry('+{x}+{y}'.format(x=x,y=y))
            
    def quit(self):
        print("quit")
        logging.info("quit")
        
        self.cancel_vid = True     # end the loop in ShowANI first
        
        self.clear_temp_files()
        
        try:
            self.setting_ok()
            
        except:
            print("Settings Not Saved")   # force quit even if error
            
        self.parent.destroy()

# In[Select Area]

    def select_area_create(self):
        print("select_area_create")
        logging.info("select_area_create")
        
        self.select_area = tk.Toplevel(self.parent)
        self.select_area.resizable(False,False)
        self.select_area.overrideredirect(1)
        
        self.select_area.geometry("%dx%d+%d+%d" % (self.total_width, self.total_height, self.top_left_x, self.top_left_y))
        self.area_canvas = tk.Canvas(self.select_area, width = self.total_width, height = self.total_height, highlightthickness = 0)
        self.area_canvas.pack()
        
        self.select_area.attributes("-alpha", 0.1)

        self.select_area.bind("<Button-3>", self.area_cancel)
        self.select_area.bind('<Button-1>', self.area_predrag)
        self.select_area.bind('<B1-Motion>', self.area_drag)
        self.select_area.bind('<ButtonRelease-1>', self.button_release)
        
        self.select_area.withdraw()
    
    def select_controller_create(self):
        print("select_controller_create")
        logging.info("select_controller_create")
        
        self.select_con = tk.Toplevel(self.parent)
        self.select_con.resizable(False,False)
        self.select_con.overrideredirect(1)
        
        self.select_con.geometry("155x290+%s+%s" %(self.select_con_x, self.select_con_y))
        
        self.select_frame = tk.Frame(self.select_con, highlightthickness = 7, highlightbackground="gray10")          
        self.select_frame.pack(pady=0, side = tk.TOP, fill=tk.BOTH)

        self.select_frame00 = tk.Frame(self.select_frame)             
        self.select_frame00.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
        
        self.select_frame01 = tk.Frame(self.select_frame)             
        self.select_frame01.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.select_frame02 = tk.Frame(self.select_frame)             
        self.select_frame02.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.select_frame03 = tk.Frame(self.select_frame)             
        self.select_frame03.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.select_frame04 = tk.Frame(self.select_frame)             
        self.select_frame04.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
        self.select_frame10 = tk.Frame(self.select_frame)             
        self.select_frame10.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.select_label00 = ttk.Label(self.select_frame00, text = "           " , style='fg.TLabel')
        self.select_label00.pack(pady=0, side= tk.LEFT)
        
        self.select_label01 = ttk.Label(self.select_frame01, text = " X : " , style='fg.TLabel')
        self.select_label01.pack(pady=0, side= tk.LEFT)
        
        self.select_label02 = ttk.Label(self.select_frame02, text = " Y : " , style='fg.TLabel')
        self.select_label02.pack(pady=0, side= tk.LEFT)
        
        self.select_label03 = ttk.Label(self.select_frame03, text = " Width : " , style='fg.TLabel')
        self.select_label03.pack(pady=0, side= tk.LEFT)
        
        self.select_label04 = ttk.Label(self.select_frame04, text = " Height : " , style='fg.TLabel')
        self.select_label04.pack(pady=0, side= tk.LEFT)

        self.select_text01 = tk.Text(self.select_frame01, height=1, width=5, background='gray25')
        self.select_text01.pack(side=tk.RIGHT, padx = 5)
        
        self.select_text02 = tk.Text(self.select_frame02, height=1, width=5, background='gray25')
        self.select_text02.pack(side=tk.RIGHT, padx = 5)
        
        self.select_text03 = tk.Text(self.select_frame03, height=1, width=5, background='gray25')
        self.select_text03.pack(side=tk.RIGHT, padx = 5)
        
        self.select_text04 = tk.Text(self.select_frame04, height=1, width=5, background='gray25')
        self.select_text04.pack(side=tk.RIGHT, padx = 5)
        
        self.select_frame00.bind('<Button-1>', self.select_con_predrag)
        self.select_frame00.bind('<B1-Motion>', self.select_con_drag)
        
        self.select_button_hide = tk.Button(self.select_frame00, text = "-", command=self.select_con_hide,width=2)
        self.select_button_hide.pack(side =tk.RIGHT, padx = 5, pady = 10)
        
        self.select_button_quit = tk.Button(self.select_frame10, text = "Cancel", command=self.area_cancel,width=10)
        self.select_button_quit.pack(padx = 0, pady = 10)
        
        self.select_con.withdraw()
        
    def area_enter(self):
        print("area_enter")
        logging.info("area_enter")
        
        self.window_hide()
        
        self.select_area.deiconify()
        self.select_area.focus_set()
        self.select_area.attributes('-topmost', True)
        self.select_area.update()

        self.select_con.deiconify()
        self.select_con.attributes('-topmost', True)
        self.select_con.update()
        
        self.motion1 = self.select_area.bind('<Motion>', self.area_motion)
        
        self.i = 0
    
    def area_cancel(self, event=None):
        print("area_cancel")
        logging.info("area_cancel")
        
        self.area_quit()
    
        self.window_unhide()
        self.parent.focus_set()
        self.parent.attributes('-topmost', True)
        self.parent.update()
        self.parent.attributes('-topmost', False)

        self.image_mode = False
        self.video_mode = False
        
    def area_quit(self, event=None):
        print("area_quit")
        logging.info("area_quit")
        
        if self.i != 0 :
            self.area_canvas.delete(globals()["rect_%s" %self.i])
        
        self.i = 0
        
        self.select_area.update()
        self.select_area.withdraw()
        self.select_area.attributes('-topmost', False)
        
        self.select_con.withdraw()
        self.select_con.attributes('-topmost', False)
    
    def area_motion(self, event):
        left = event.x
        top = event.y
       
        self.select_text01.delete("1.0","2.0")
        self.select_text01.insert("1.0", left) 

        self.select_text02.delete("1.0","2.0")
        self.select_text02.insert("1.0", top) 
              
        self.select_text03.delete("1.0","2.0")
        self.select_text04.delete("1.0","2.0")
        
        # Draw Area
        # pre_i = self.i
        # self.i = self.i + 1
    
        # globals()["rect_%s" %self.i] = self.area_canvas.create_rectangle(self.left, self.top, self.width, self.height, fill='white')
        
        # if pre_i != 0 :
        #     self.area_canvas.delete(globals()["rect_%s" %pre_i])
    
    def area_predrag(self, event):
        print("area_predrag")
        logging.info("area_predrag")
        
        self.select_area.unbind('<Motion>', self.motion1)
        
        self.left = event.x
        self.top = event.y
        
        self.width = event.x + 1          # for fixing crash when clicking without dragging
        self.height = event.y + 1         # for fixing crash when clicking without dragging
        
        self.select_text01.delete("1.0","2.0")
        self.select_text01.insert("1.0", event.x) 
        
        self.select_text02.delete("1.0","2.0")
        self.select_text02.insert("1.0", event.y) 
    
    def area_drag(self, event):

        self.width = event.x
        self.height = event.y
        
        # update controller
        width = self.width - self.left
        height = self.height - self.top

        if width < 0:
            left = self.left + width
            width = -1 * width            
            self.select_text01.delete("1.0","2.0")
            self.select_text01.insert("1.0", left) 
            
        else:
            left = self.left
            width = self.width - self.left
            self.select_text01.delete("1.0","2.0")
            self.select_text01.insert("1.0", left) 
        
        if height < 0:
            top = self.top + height
            height = -1 * height         
            self.select_text02.delete("1.0","2.0")
            self.select_text02.insert("1.0", top) 
        
        else:
            top = self.top
            height = self.height - self.top
            self.select_text02.delete("1.0","2.0")
            self.select_text02.insert("1.0", top) 
            
        self.select_text03.delete("1.0","2.0")
        self.select_text03.insert("1.0", width) 
        
        self.select_text04.delete("1.0","2.0")
        self.select_text04.insert("1.0", height) 
        
        # Draw Area
        pre_i = self.i
        self.i = self.i + 1
    
        globals()["rect_%s" %self.i] = self.area_canvas.create_rectangle(self.left, self.top, self.width, self.height, fill='white')
        
        if pre_i != 0 :
            self.area_canvas.delete(globals()["rect_%s" %pre_i])

    def button_release(self, event=None):
        print("button_release")
        logging.info("button_release")
        
        if self.image_mode:
            if self.delay > 0:
                self.delay_img()
                
            self.area_quit()
            
            width, height, img = self.cap_image()
            self.temp_img = img
            self.window_changesize(width, height)
        
            self.ShowIMG(img)
            self.copy_button.config(state=tk.NORMAL)
            self.window_unhide()
            self.parent.focus_set()
            self.parent.attributes('-topmost', True)
            self.parent.attributes('-topmost', False)
            
            self.image_mode = False
            
        if self.video_mode:
            self.area_quit()
            
            self.video.deiconify()
            self.video.attributes('-topmost', True)
            
            width = self.width - self.left
            height = self.height - self.top
            
            self.video_text.delete('1.0', '2.0')
            self.video_text.insert("1.0", "Width: %s, Height: %s" %(width, height))
            
            self.video_mode = False
            
    def select_con_predrag(self, event):
        
        self.select_con_offsetx = event.x
        self.select_con_offsety = event.y
        
    def select_con_drag(self, event):
        
        x = self.select_con.winfo_x() + event.x - self.select_con_offsetx
        y = self.select_con.winfo_y() + event.y - self.select_con_offsety
    
        self.select_con.geometry('+{x}+{y}'.format(x=x,y=y))
        
    def select_con_hide(self):
        
        self.select_con.withdraw()
    
# In[Delay]
    
    def delay_img(self):
        print("delay_img")
        logging.info("delay_img")
        
        self.select_button_hide.config(state=tk.DISABLED)
        self.select_button_quit.config(state=tk.DISABLED)
        
        for i in range(self.delay):
            self.select_label00.config(text = " In %s Sec     " %(self.delay - i))
            self.select_con.update()
            time.sleep(1)
    
        self.select_button_hide.config(state=tk.NORMAL)
        self.select_button_quit.config(state=tk.NORMAL)
        self.select_label00.config(text = "           ")
    
    def delay_vid(self):
        print("delay_vid")
        logging.info("delay_vid")
        
        self.start_button.config(state=tk.DISABLED)
        self.finish_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        
        for i in range(self.delay):

            self.video_text.insert("1.0", "In %s Sec \n" %(self.delay - i))
            self.video.update()
            
            time.sleep(1)
            self.video_text.delete('1.0', '2.0')
        
        self.start_button.config(state=tk.NORMAL)
        self.finish_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)
            
# In[Image Cap]
    
    def image_button_click(self):
        print("image_button_click")
        logging.info("image_button_click")
        
        self.image_mode = True
        self.temp_vid = None
        self.temp_img = None
        
        self.progress_text.delete('1.0', '2.0')
        self.preview_canvas.delete("all")   
        
        self.clear_temp_files()
        
        if self.is_skiparea and self.top is not None:
            self.button_release()
        
        else:    
            self.area_enter()
    
    def cap_image(self):
        print("cap_image")
        logging.info("cap_image")
        
        top = self.top
        left = self.left
        width = self.width - self.left
        height = self.height - self.top
        
        if width == 0:
            width = 1                     # fix the bug that mss can't handle 0 value
        
        elif width < 0:
            left = self.left + width
            width = -1 * width            # fix the bug that mss can't handle negative value
        
        if height == 0:
            height = 1                    # fix the bug that mss can't handle 0 value
        
        elif height < 0:
            top = self.top + height
            height = -1 * height          # fix the bug that mss can't handle negative value
        
        with mss.mss() as mss_instance:
            image_position = mss_instance.monitors[1]           # whole screen
            image_position = {"top": top, "left": left, "width": width, "height": height}
            # print(image_position)
            screenshot = mss_instance.grab(image_position)
            
        screenshot = PIL.Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")  # Convert to PIL.Image
        img_np = np.array(screenshot)
        img = cv2.cvtColor(np.array(img_np), cv2.COLOR_RGB2BGR)
        
        # output_path = r"C:\Users\simon\Practice\test.jpg"
        # cv2.imwrite(output_path, img)
        
        return width, height, img
            
# In[Video Cap]

    def video_create(self):
        print("video_create")
        logging.info("video_create")
        
        self.video = tk.Toplevel(self.parent)
        self.video.resizable(False,False)
        self.video.overrideredirect(1)
        
        self.video.geometry("230x80+%s+%s" %(self.video_x, self.video_y))
        style.configure("secondary.TButton", font=("Helvetica", 8,"bold")) # letter button
        style.map("secondary.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
        
        self.frame_videotop = ttk.Frame(self.video,style='Warning.TFrame')             # add frame first
        self.frame_videotop.pack(pady=1, side = tk.TOP, fill = "both")
        self.frame_videobot = ttk.Frame(self.video,style='Warning.TFrame')             # add frame first
        self.frame_videobot.pack(pady=1, side = tk.TOP, fill = "both")
        
        self.video_text = tk.Text(self.frame_videotop, height=1, width=25, background='gray25')
        self.video_text.pack(side=tk.LEFT, padx = 5)
        
        self.start_button = ttk.Button(self.frame_videobot, text= "Start", width=6, style='secondary.TButton', command= self.start_button_click)
        self.start_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")              # padx means gap of x-axis
        self.finish_button = ttk.Button(self.frame_videobot, text= "Finish", width=6, style='secondary.TButton', command= self.finish_button_click)
        self.finish_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")              # padx means gap of x-axis
        self.cancel_button = ttk.Button(self.frame_videobot, text= "X", width=3, style='secondary.TButton', command= self.cancel_button_click)
        self.cancel_button.pack(side=tk.RIGHT, padx = 5, pady = 5, fill = "both")  
        
        self.video.bind('<Button-1>', self.video_predrag)
        self.video.bind('<B1-Motion>', self.video_drag)
        
        self.video.deiconify()
        self.video.attributes('-topmost', True)

        self.video.withdraw()
        
    def video_button_click(self):
        print("video_button_click")
        logging.info("video_button_click")
        
        self.video_mode = True
        self.pause_vid = False
        self.stop_vid = False
        self.is_recording = False
        self.temp_vid = None
        self.temp_img = None
        self.video.withdraw()
        
        self.progress_text.delete('1.0', '2.0')
        self.preview_canvas.delete("all") 
        
        self.clear_temp_files()
        
        if self.is_skiparea and self.top is not None:
            self.area_enter()
            self.button_release()
        
        else:
            self.area_enter()
        
        self.finish_button.config(state=tk.DISABLED)
        
    def start_button_click(self):
        print("start_button_click")
        logging.info("start_button_click")
        
        self.start_button.configure(text= "Pause", command= self.pause_button_click)
        self.finish_button.config(state=tk.NORMAL)
        self.video.update()
        
        self.pause_vid = False
        self.cancel_vid = False
        
        if not self.is_recording:
            
            if self.delay > 0:
                self.delay_vid()
                
            top, left, width, height, preview_frame = self.cap_video()
            
            if preview_frame is not None:           # None if cancel
                self.temp_vid = preview_frame
                self.copy_button.config(state=tk.DISABLED)
                self.window_changesize(width, height)
                self.window_unhide()
                self.parent.focus_set()
                self.parent.attributes('-topmost', True)
                self.parent.attributes('-topmost', False)
                self.ShowANI(preview_frame, top, left, width, height)

    def pause_button_click(self):
        print("pause_button_click")
        logging.info("pause_button_click")
        
        self.start_button.configure(text= "Start", command= self.start_button_click)
        self.video.update()
        
        self.pause_vid = True
        
    def finish_button_click(self):
        print("finish_button_click")
        logging.info("finish_button_click")
        
        self.stop_vid = True
        self.start_button.configure(text= "Start", command= self.start_button_click)
        self.video.withdraw()
        
        self.parent.attributes('-topmost', True)
        self.parent.attributes('-topmost', False)
        
    def cancel_button_click(self):
        print("cancel_button_click")
        logging.info("cancel_button_click")
        
        self.is_recording = False
        self.cancel_vid = True
        self.video_mode = True
        self.temp_vid = None
        self.video.withdraw()
        
        self.start_button.configure(text= "Start", command= self.start_button_click)
        self.video.update()
        
        if self.is_skiparea and self.top is not None:
            self.area_enter()
            self.area_cancel()
        
        else:
            self.area_enter()
        
    def cap_video(self):
        print("cap_video")
        logging.info("cap_video")
        
        self.is_recording = True
        self.mouse_pointer = []
        self.frame = 0
        self.temp_vid_number = 0
        
        top = self.top
        left = self.left
        width = self.width - self.left
        height = self.height - self.top
        # output = r"C:\Users\simon\Practice\video.avi"
        fps = self.frame_rate
        
        if width == 0:
            width = 1                     # fix the bug that mss can't handle 0 value
        
        elif width < 0:
            left = self.left + width
            width = -1 * width            # fix the bug that mss can't handle negative value
        
        if height == 0:
            height = 1                    # fix the bug that mss can't handle 0 value
        
        elif height < 0:
            top = self.top + height
            height = -1 * height          # fix the bug that mss can't handle negative value
        
        cap_area = {"top": top, "left": left, "width": width, "height": height}
        
        print(cap_area)
        # Define the codec and create VideoWriter object

        preview_frame = []
        
        while True:
            self.video.update()
            
            while self.pause_vid and not self.cancel_vid and not self.stop_vid:
                time.sleep(0.01)
                self.video.update()
            
            if self.stop_vid:
                break
            
            if self.cancel_vid:
                return None, None, None, None, None
            
            time_start = time.perf_counter()
            
            with mss.mss() as mss_instance:
                screenshot = mss_instance.grab(cap_area)
                globals()["temp_png_%s" %self.frame] = threading.Thread(target = self.temp_png, args=(screenshot, self.frame))
                globals()["temp_png_%s" %self.frame].start()
                
            if self.frame % 300 == 0 and self.frame > 0:
                start = self.temp_vid_number * 300
                end = (self.temp_vid_number + 1) * 300
                self.temp_vid_number = self.temp_vid_number + 1
                
                globals()["temp_avi_%s" %self.temp_vid_number] = threading.Thread(target = self.temp_avi, args=(start, end, self.temp_vid_number))
                globals()["temp_avi_%s" %self.temp_vid_number].start()
            
            if self.frame < 300:                    # max preview frame is 300
                preview_frame.append(screenshot)
            
            if self.is_cursor:
                self.mouse_pointer.append(win32gui.GetCursorPos())
            
            # print(self.mouse_pointer)
            
            time_spent = time.perf_counter() - time_start
            print(time_spent)
            logging.info("%s : %s" %(self.frame, time_spent))
            time.sleep(max(1/fps - time_spent, 0))
            
            self.frame = self.frame + 1
        
        self.is_recording = False
        
        return top, left, width, height, preview_frame
    
    def temp_png(self, screenshot, number):
        output_file = "temp_" + str(number).rjust(7, "0") + ".png"
        output_path = os.path.join(self.temp_dir_png, output_file)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=output_path)

    def temp_avi(self, start, end, temp_vid_number):
        print("temp_avi : %s - %s" %(start,end))
        logging.info("temp_avi : %s - %s" %(start,end))
        
        width = self.width - self.left
        height = self.height - self.top
        width = max(1, abs(width))
        height = max(1, abs(height))
        output_dir = self.temp_dir_vid
        fps = self.frame_rate
        
        output_file = "temp_vid_" + str(temp_vid_number).rjust(4, "0") + ".avi"
        output_path = os.path.join(output_dir, output_file)
                
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        mouse_pointer_vid = [None] * end
        
        for i in range(start, end):

            file = "temp_" + str(i).rjust(7, "0") + ".png"
            png_path = os.path.join(self.temp_dir_png, file)
            frame = PIL.Image.open(png_path)
            
            # adjustment of mouse pointer position
            if self.is_cursor:
                x, y = self.mouse_pointer[i]
                x = x - self.left
                y = y - self.top
                
                if x > width:
                    x = None
                    
                if y > height:
                    y = None
                
                mouse_pointer_vid[i] = (x,y)
                
                frame = self.add_mouse_pointer(frame, mouse_pointer_vid[i])
                
            frame = np.array(frame)
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            out.write(frame)
            
            os.remove(png_path)
            i = i + 1
            
        out.release()
        cv2.destroyAllWindows()
        
        print("finish temp_vid : ", output_file)
        
    def add_mouse_pointer(self, img, mouse_position):
        
        x , y = mouse_position
        
        if x is not None and y is not None:
            exe_dir = os.path.split(sys.argv[0])[0]            # sys.argv[0] is the exe path
            cursor_path = os.path.join(exe_dir, "cursor.png")
              
            # Opening the secondary image (overlay image)
            img_cursor = PIL.Image.open(cursor_path)
              
            # Pasting img2 image on top of img1 
            # starting at coordinates (0, 0)
            img.paste(img_cursor, mouse_position, mask = img_cursor)
          
        return img
    
    def clear_temp_files(self):
        print("clear_temp_files")
        logging.info("clear_temp_files")
        
        temp_png = os.listdir(self.temp_dir_png)
        for file in temp_png:
            file_path = os.path.join(self.temp_dir_png, file)
            os.remove(file_path)
        
        temp_vid = os.listdir(self.temp_dir_vid)
        for file in temp_vid:
            file_path = os.path.join(self.temp_dir_vid, file)
            os.remove(file_path)
    
# In[Preview]

    def ShowIMG(self, img):
        print("ShowIMG")
        logging.info("ShowIMG")
        
        self.parent.update()                                 # update pic_w, pic_h for fullscreen resize 
        self.preview_canvas.delete("all")                        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.preview_canvas.image = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
        self.preview_canvas.create_image(10,10, anchor="nw", image = self.preview_canvas.image)
        
        self.parent.update()

    def ShowANI(self, preview_frame, top, left, width, height) :     
        print("ShowANI")
        logging.info("ShowANI")
        
        print("Generating Preview")
        logging.info("Generating Preview")
        self.progress_text.insert("1.0", "Generating Preview")
        self.image_button.config(state=tk.DISABLED)
        self.vid_button.config(state=tk.DISABLED)
        self.settings_button.config(state=tk.DISABLED)
        self.parent.update()
        
        ani_preview = []
        mouse_pointer_gif = [None] * 300
        fps = self.frame_rate
        
        i = 0
        for frame in preview_frame:            # set the max frame of preview to 300 frames
            frame = PIL.Image.frombytes("RGB", frame.size, frame.bgra, "raw", "BGRX")  # Convert to PIL.Image
            
            # adjustment of mouse pointer position
            if self.is_cursor:
                x, y = self.mouse_pointer[i]
                x = x - left
                y = y - top
                
                if x > width:
                    x = None
                    
                if y > height:
                    y = None
                
                mouse_pointer_gif[i] = (x,y)
                
                frame = self.add_mouse_pointer(frame, mouse_pointer_gif[i])
                
            frame = np.array(frame)
            ani_preview.append(frame)
            i = i + 1
            
        i = 0
        
        gif_len = len(ani_preview)
        
        del preview_frame
        
        print("Preview Generated")
        logging.info("Preview Generated")
        self.progress_text.delete('1.0', '2.0')
        self.image_button.config(state=tk.NORMAL)
        self.vid_button.config(state=tk.NORMAL)
        self.settings_button.config(state=tk.NORMAL)
        self.parent.update()
        
        while True:          # loop gif until stop
            timer_start = time.perf_counter()
            
            if self.image_mode or self.video_mode or self.cancel_vid:       # stop ShowANI when clicking image or video or cancel video
                break
            
            gif_dur = 1 / fps
                
            self.preview_canvas.delete("all")                 # remove existing image
            # img = PIL.ImageTk.PhotoImage(ani_preview[i])
            img = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(ani_preview[i]))
            self.preview_canvas.create_image(10,10, anchor="nw", image = img)  # create image frame by frame
            
            self.parent.update()
                
            time_diff = time.perf_counter() - timer_start

            sleep_time = max(0, gif_dur  - (time_diff + 0.0))
            sleep_time = min(1, sleep_time)
            
            time.sleep(sleep_time)
            
            timer_start = time.perf_counter()
                
            i = (i + 1) % gif_len
        
        del ani_preview
        
    def copy_canvas(self, event=None):
        print("copy_canvas")
        logging.info("copy_canvas")
        
        if self.temp_img is not None:
            img = self.temp_img
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = PIL.Image.fromarray(img)
    
            output = BytesIO()
            img.save(output, "BMP")
            data = output.getvalue()[14:]

            output.close()
        
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            
        if self.temp_vid is not None:
            # path = r"D:\Downloads\Anime_Comic\GIF_VID\[Milk Factory] Motto! Haramase! Honoo no Oppai Isekai Ero Mahou Gakuen! [Animated] [Decensored]\02_mv_a01r5.gif"
            # urls = qt.QUrl.fromLocalFile(path)
            # # urls = self.temp_vid
            # # if not urls:
            # #     return
            # mime = qt.QMimeData()
            # mime.setUrls(urls)
            # clipboard = qt.QtWidgets.QApplication.clipboard()
            # clipboard.setMimeData(mime) 
            pass         # can't copy gif so far
        
# In[Save]

    def save_button_click(self):
        print("save_button_click")
        logging.info("save_button_click")

        if self.temp_vid is not None:
            if self.vid_saveas == ".avi":
                self.save_avi()
            
            elif self.vid_saveas == ".gif":
                self.save_gif()
        
        if self.temp_img is not None:
            self.save_img()
        
    def save_img(self):
        print("save_img")
        logging.info("save_img")
        
        output_dir = self.save_path
        i = 1
        while True:
            output_file = "img_" + str(i).rjust(4, "0") + ".jpg"
            output_path = os.path.join(output_dir, output_file)
            if os.path.exists(output_path):
                i = i + 1
                
            else:
                break
        
        cv2.imwrite(output_path, self.temp_img)
        print("Img Generated")
        self.progress_text.delete('1.0', '2.0')
        self.progress_text.insert("1.0", "Image Generated")
        
    def save_avi(self):
        print("save_avi")
        logging.info("save_avi")
        
        width = self.width - self.left
        height = self.height - self.top
        width = max(1, abs(width))
        height = max(1, abs(height))
        output_dir = self.save_path
        fps = self.frame_rate
        
        print("Generating Video")
        logging.info("Generating Video")
        self.progress_text.delete('1.0', '2.0')
        self.progress_text.insert("1.0", "Generating Video")
        self.image_button.config(state=tk.DISABLED)
        self.vid_button.config(state=tk.DISABLED)
        self.settings_button.config(state=tk.DISABLED)
        self.parent.update()
        
        i = 1
        while True:
            output_file = "vid_" + str(i).rjust(4, "0") + ".avi"
            output_path = os.path.join(output_dir, output_file)
            if os.path.exists(output_path):
                i = i + 1
                
            else:
                break
            
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        start = self.temp_vid_number * 300
        end = self.frame
            
        mouse_pointer_vid = [None] * end
        
        for i in range(start,end):
            # progress_percentage = int(round((i - start)/(end - start), 2) * 100)
            # self.progress_text.delete('1.0', '2.0')
            # self.progress_text.insert("1.0", "Generating Video (%s%%)" %progress_percentage)
            self.parent.update()

            # frame = PIL.Image.frombytes("RGB", frame.size, frame.bgra, "raw", "BGRX")  # Convert to PIL.Image
            file = "temp_" + str(i).rjust(7, "0") + ".png"
            png_path = os.path.join(self.temp_dir_png, file)
            frame = PIL.Image.open(png_path)
            
            # adjustment of mouse pointer position
            if self.is_cursor:
                x, y = self.mouse_pointer[i]
                x = x - self.left
                y = y - self.top
                
                if x > width:
                    x = None
                    
                if y > height:
                    y = None
                
                mouse_pointer_vid[i] = (x,y)
                
                frame = self.add_mouse_pointer(frame, mouse_pointer_vid[i])
                
            frame = np.array(frame)
            frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
            out.write(frame)
            
            os.remove(png_path)
            i = i + 1
            
        out.release()
        cv2.destroyAllWindows()
        
        # wait for all threads to finish
        if self.temp_vid_number > 0:
            for i in range(self.temp_vid_number):
                globals()["temp_avi_%s" %self.temp_vid_number].join()
        
        # combine all temp vid into one temp vid
        if self.temp_vid_number > 0:
            
            vid_series = []
            for i in range(self.temp_vid_number):
                temp_vid_name = "temp_vid_" + str(i + 1).rjust(4, "0") + ".avi"
                temp_vid_path = os.path.join(self.temp_dir_vid, temp_vid_name)
                
                vid_series.append(temp_vid_path)
            
            temp_lastvid_path = os.path.join(output_dir, "temp_final.avi") 
            os.rename(output_path, temp_lastvid_path)  # rename the current output file, which is the last part
            
            vid_series.append(temp_lastvid_path)
            print(vid_series)
            
            combined_video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_no = 0
            for temp_video in vid_series:

                curr_v = cv2.VideoCapture(temp_video)
                while curr_v.isOpened():
                    r, frame = curr_v.read()    # Get return value and curr frame of curr video
                    if not r:
                        break
                    
                    frame_no = frame_no + 1
                    progress_percentage = int(round((frame_no)/(self.frame), 2) * 100)
                    self.progress_text.delete('1.0', '2.0')
                    self.progress_text.insert("1.0", "Generating Video (%s%%)" %progress_percentage)
                    self.parent.update()
                    
                    combined_video.write(frame)          # Write the frame
            
            combined_video.release()                     # Save the video
            curr_v.release()
            cv2.destroyAllWindows()
            
            os.remove(temp_lastvid_path)
            self.clear_temp_files()           # clear all temp files
        
        print("Vid Generated")
        logging.info("Vid Generated")
        self.progress_text.delete('1.0', '2.0')
        self.progress_text.insert("1.0", "Video Generated")
        self.image_button.config(state=tk.NORMAL)
        self.vid_button.config(state=tk.NORMAL)
        self.settings_button.config(state=tk.NORMAL)
        self.parent.update()
        
    def save_gif(self):
        print("save_gif")
        logging.info("save_gif")
        
        width = self.width - self.left
        height = self.height - self.top
        width = max(1, abs(width))
        height = max(1, abs(height))
        output_dir = self.save_path
        fps = self.frame_rate
        
        print("Generating Gif")
        logging.info("Generating Gif")
        self.progress_text.delete('1.0', '2.0')
        self.progress_text.insert("1.0", "Generating Gif")
        self.image_button.config(state=tk.DISABLED)
        self.vid_button.config(state=tk.DISABLED)
        self.settings_button.config(state=tk.DISABLED)
        self.parent.update()
        
        i = 1
        while True:
            output_file = "gif_" + str(i).rjust(4, "0") + ".gif"
            output_path = os.path.join(output_dir, output_file)
            if os.path.exists(output_path):
                i = i + 1
                
            else:
                break

        with imageio.get_writer(output_path, mode='I', fps= fps, format='GIF-FI', quantizer='nq', palettesize=256) as writer:
            i = 0
            
            for frame in self.temp_vid:  
                progress_percentage = int(round(i/len(self.temp_vid), 2) * 100)
                self.progress_text.delete('1.0', '2.0')
                self.progress_text.insert("1.0", "Generating Gif (%s%%)" %progress_percentage)
                self.parent.update()
                
                frame = PIL.Image.frombytes("RGB", frame.size, frame.bgra, "raw", "BGRX")  # Convert to PIL.Image
                    
                frame = np.array(frame)

                writer.append_data(frame)
                
                i = i + 1

        print("Gif Generated")
        logging.info("Gif Generated")
        self.progress_text.delete('1.0', '2.0')
        self.progress_text.insert("1.0", "Gif Generated")
        self.image_button.config(state=tk.NORMAL)
        self.vid_button.config(state=tk.NORMAL)
        self.settings_button.config(state=tk.NORMAL)
        self.parent.update()
        
# In[Settings]
    
    def import_settings(self):
        print("import_settings")
        logging.info("import_settings")
        
        # Default Settings
        # window mode
        self.window_x = 300
        self.window_y = 150
        
        self.setting_x = 500
        self.setting_y = 200
        
        self.video_x = 100
        self.video_y = 800
        
        self.select_con_x = 100
        self.select_con_y = 800
        
        self.skiparea_check = tk.BooleanVar()
        self.is_skiparea = False
        self.skiparea_check.set(False)                        # include subfolder
        
        self.cursor_check = tk.BooleanVar()
        self.is_cursor = False
        self.cursor_check.set(False)                        # include subfolder
        
        self.predefine_check = tk.BooleanVar()
        self.is_predefine = False
        self.predefine_check.set(False)                        # include subfolder
        
        exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
        self.save_path = os.path.join(exe_dir, "output")
        self.temp_dir_png = os.path.join(exe_dir, r"temp\png")
        self.temp_dir_vid = os.path.join(exe_dir, r"temp\vid")
        
        # Add dir to avoid error
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
            
        if not os.path.exists(self.temp_dir_png):
            os.makedirs(self.temp_dir_png)
            
        if not os.path.exists(self.temp_dir_vid):
            os.makedirs(self.temp_dir_vid)
        
        self.vid_saveas = ".avi"
        
        self.delay = 0
        
        self.predefine_w = 512
        self.predefine_h = 512
        
        self.frame_rate = 30
        
        # Import config
        self.config = configparser.ConfigParser()
        
        self.config_path = os.path.join(exe_dir, "config.ini")
        self.config.read(self.config_path)
        
        #is_parent = str(getconfig("parent_check", is_parent)) # disable getting parent_check
        #parent_check.set(is_parent)
        self.is_skiparea = self.getconfig("skiparea_check", self.is_skiparea) # disable getting parent_check
        self.skiparea_check.set(self.is_skiparea)
        self.is_cursor = self.getconfig("cursor_check", self.is_cursor) # disable getting parent_check
        self.cursor_check.set(self.is_cursor)
        self.is_predefine = self.getconfig("predefine_check", self.is_predefine) 
        self.predefine_check.set(self.is_predefine)
        self.predefine_w = str(self.getconfig("predefine_w", self.predefine_w))
        self.predefine_h = str(self.getconfig("predefine_h", self.predefine_h))
        self.vid_saveas = str(self.getconfig("vid_saveas", self.vid_saveas))
        self.save_path = str(self.getconfig("save_path", self.save_path))
        self.delay = str(self.getconfig("delay", self.delay))
        self.frame_rate = int(self.getconfig("frame_rate", self.frame_rate))
        self.window_x = str(self.getconfig("window_x", self.window_x))
        self.window_y = str(self.getconfig("window_y", self.window_y))
        self.setting_x = str(self.getconfig("setting_x", self.setting_x))
        self.setting_y = str(self.getconfig("setting_y", self.setting_y))
        self.video_x = str(self.getconfig("video_x", self.video_x))
        self.video_y = str(self.getconfig("video_y", self.video_y))
        self.select_con_x = str(self.getconfig("select_con_x", self.select_con_x))
        self.select_con_y = str(self.getconfig("select_con_y", self.select_con_y))
        
        self.delay = int(self.delay)
        
    def getconfig(self, column, var):
        
        try:
            if self.config.get("SnippingTool", str(column)) == "False":
                return False                   # return boolean as all strings are deemed True
            
            elif self.config.get("SnippingTool", str(column)) == "True":
                return True                   # return boolean as all strings are deemed True
            
            else:
                return self.config.get("SnippingTool", str(column))
        
        except:
            return var
    
    def setting_buttonclick(self):
        print("setting_buttonclick")
        logging.info("setting_buttonclick")
          
        window.settings_button.config(text = "Hide", command=self.setting_hide)
            
        self.settings.deiconify()
        self.settings.attributes('-topmost', True)
        self.settings.update()         # update for the position
    
    def setting_create(self):
        print("setting_create")
        logging.info("setting_create")
        
        self.settings = tk.Toplevel(self.parent)
        
        self.settings.resizable(False,False)
        self.settings.overrideredirect(1)
        self.settings.geometry('650x570+%d+%d' %(int(self.setting_x), int(self.setting_y)))    # re adjust list position

        self.setting_frame_top = tk.Frame(self.settings)             
        self.setting_frame_top.pack(pady=0, side = tk.TOP, fill=tk.BOTH)

        self.setting_frame00 = tk.Frame(self.settings, background='gray25')             
        self.setting_frame00.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame01 = tk.Frame(self.settings)             
        self.setting_frame01.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame02 = tk.Frame(self.settings)             
        self.setting_frame02.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame03 = tk.Frame(self.settings)             
        self.setting_frame03.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame04 = tk.Frame(self.settings)             
        self.setting_frame04.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame05 = tk.Frame(self.settings)             
        self.setting_frame05.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame06 = tk.Frame(self.settings)             
        self.setting_frame06.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame07 = tk.Frame(self.settings)             
        self.setting_frame07.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame10 = tk.Frame(self.settings, background='gray25')             
        self.setting_frame10.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame11 = tk.Frame(self.settings)             
        self.setting_frame11.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame12 = tk.Frame(self.settings)             
        self.setting_frame12.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame13 = tk.Frame(self.settings)             
        self.setting_frame13.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
        
        self.setting_frame40 = tk.Frame(self.settings)             
        self.setting_frame40.pack(pady=5, side = tk.BOTTOM)
        
        self.setting_frame41 = tk.Frame(self.settings)             
        self.setting_frame41.pack(pady=5, side = tk.BOTTOM)

        self.setting_label_top = ttk.Label(self.setting_frame_top, text = "              " , style='fg.TLabel')
        self.setting_label_top.pack(pady=0, side= tk.LEFT)
        
        self.setting_label00 = ttk.Label(self.setting_frame00, text = " General : " , style='fg.TLabel' , background='gray25')
        self.setting_label00.pack(pady=0, side= tk.LEFT)
        
        self.setting_label01 = ttk.Label(self.setting_frame01, text = "    Save Path : " , style='fg.TLabel')
        self.setting_label01.pack(pady=0, side= tk.LEFT)
        
        self.setting_label10 = ttk.Label(self.setting_frame10, text = " Video / Gif : " , style='fg.TLabel' , background='gray25')
        self.setting_label10.pack(pady=0, side= tk.LEFT)
        
        self.setting_button02 = tk.Button(self.setting_frame02, text = "Browse", command=self.browse_file, width=10)
        self.setting_button02.pack(side =tk.RIGHT, padx = 5)

        self.setting_entry02 = tk.Entry(self.setting_frame02, width=60, background='gray25')
        self.setting_entry02.insert(1, self.save_path)
        self.setting_entry02.pack(pady=0, padx = 15, side= tk.RIGHT)
        
        self.setting_entry06 = tk.Entry(self.setting_frame06, width=6, background='gray25')
        self.setting_entry06.insert(1, self.predefine_w)
        self.setting_entry06.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_entry07 = tk.Entry(self.setting_frame07, width=6, background='gray25')
        self.setting_entry07.insert(1, self.predefine_h)
        self.setting_entry07.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_entry13 = tk.Entry(self.setting_frame13, width=6, background='gray25')
        self.setting_entry13.insert(1, self.frame_rate)
        self.setting_entry13.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_label03 = ttk.Label(self.setting_frame03, text = "    Delay (Sec) : " , style='fg.TLabel')
        self.setting_label03.pack(pady=0, side= tk.LEFT)
        
        self.setting_label04 = ttk.Label(self.setting_frame04, text = "    Skip Area Selection : " , style='fg.TLabel')
        self.setting_label04.pack(pady=0, side= tk.LEFT)
        
        self.setting_label05 = ttk.Label(self.setting_frame05, text = "    Pre-defined Width/Height : " , style='fg.TLabel')
        self.setting_label05.pack(pady=0, side= tk.LEFT)
        
        self.setting_label06 = ttk.Label(self.setting_frame06, text = "    Pre-defined Width : " , style='fg.TLabel')
        self.setting_label06.pack(pady=0, side= tk.LEFT)
        
        self.setting_label07 = ttk.Label(self.setting_frame07, text = "    Pre-defined Height : " , style='fg.TLabel')
        self.setting_label07.pack(pady=0, side= tk.LEFT)
        
        self.setting_label11 = ttk.Label(self.setting_frame11, text = "    Video Save As : " , style='fg.TLabel')
        self.setting_label11.pack(pady=0, side= tk.LEFT)
        
        self.setting_label12 = ttk.Label(self.setting_frame12, text = "    Video with Mouse Cursor : " , style='fg.TLabel')
        self.setting_label12.pack(pady=0, side= tk.LEFT)
        
        self.setting_label13 = ttk.Label(self.setting_frame13, text = "    Video Frame Rate (Max 60) : " , style='fg.TLabel')
        self.setting_label13.pack(pady=0, side= tk.LEFT)
        
        self.setting_check04 = ttk.Checkbutton(self.setting_frame04, text="", var=self.skiparea_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check04.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_check05 = ttk.Checkbutton(self.setting_frame05, text="", var=self.predefine_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check05.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.setting_check12 = ttk.Checkbutton(self.setting_frame12, text="", var=self.cursor_check, style = "warning.Roundtoggle.Toolbutton")
        self.setting_check12.pack(pady=0, padx = 0, side= tk.RIGHT)
        
        self.delaystr = tk.StringVar()
        self.delaystr.set(self.delay)
        self.setting_option03 = tk.OptionMenu(self.setting_frame03, self.delaystr, "0", "1", "2", "3")
        self.setting_option03["highlightthickness"] = 0                  # remove the option boundary
        self.setting_option03.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.vid_saveasstr = tk.StringVar()
        self.vid_saveasstr.set(self.vid_saveas)
        self.setting_option11 = tk.OptionMenu(self.setting_frame11, self.vid_saveasstr, ".avi", ".gif")
        self.setting_option11["highlightthickness"] = 0                  # remove the option boundary
        self.setting_option11.pack(pady=0, padx = 10, side= tk.RIGHT)
        
        self.setting_error = tk.Label(self.setting_frame41, text = "", fg = "red", font = ("Arial", 10))
        self.setting_error.pack()
        
        self.setting_button_save = tk.Button(self.setting_frame40, text = "Save and Close", command=self.setting_ok,width=20)
        self.setting_button_save.pack(side =tk.LEFT, padx = 20, pady = 10)
        
        self.setting_button_quit = tk.Button(self.setting_frame40, text = "Cancel", command=self.setting_hide,width=20)
        self.setting_button_quit.pack(side =tk.RIGHT, padx = 20, pady = 10)
        
        # Setting Drag
        self.setting_offsetx = 0
        self.setting_offsety = 0
        self.setting_frame_top.bind('<Button-1>', self.setting_predrag)
        self.setting_frame_top.bind('<B1-Motion>', self.setting_drag)
 
        self.settings.withdraw()
        
    def setting_predrag(self, event):
        print("drag_setting")    
        logging.info("drag_setting")
        
        self.setting_offsetx = event.x
        self.setting_offsety = event.y
        
    def setting_drag(self, event):
        
        self.setting_x = self.settings.winfo_x() + event.x - self.setting_offsetx
        self.setting_y = self.settings.winfo_y() + event.y - self.setting_offsety
    
        self.settings.geometry('+{x}+{y}'.format(x = self.setting_x, y = self.setting_y))

    def browse_file(self):
        print("browse_file")
        logging.info("browse_file")
        
        folder_name = filedialog.askdirectory()
        if folder_name != "":
        
            self.setting_entry02.delete(0,"end")
            self.setting_entry02.insert(1, str(folder_name)) 
    
    def setting_ok(self):
        print("setting_ok")
        logging.info("setting_ok")
        
        self.setting_error.config(text = "")
        
        self.is_skiparea = self.skiparea_check.get()
        
        self.is_cursor = self.cursor_check.get()
        
        self.is_predefine = self.predefine_check.get()

        self.vid_saveas = self.vid_saveasstr.get()
        
        self.delay = int(self.delaystr.get())

        self.save_path = str(self.setting_entry02.get())
    
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)          # create dir to avoid error
        
        try:
            self.frame_rate = int(self.setting_entry13.get())
        
        except:
            self.setting_error.config(text = "Not saved: Value must be integer")
            raise ValueError("Value must be integer") 

        try:
            self.predefine_w = int(self.setting_entry06.get())
        
        except:
            self.setting_error.config(text = "Not saved: Value must be integer")
            raise ValueError("Value must be integer") 
            
        try:
            self.predefine_h = int(self.setting_entry07.get())
        
        except:
            self.setting_error.config(text = "Not saved: Value must be integer")
            
            raise ValueError("Value must be integer")
            
        if self.frame_rate > 60:
            self.frame_rate = 60
            self.setting_entry13.delete(0, tk.END)
            self.setting_entry13.insert(1, self.frame_rate)
        
        if self.frame_rate < 1:
            self.frame_rate = 1
            self.setting_entry13.delete(0, tk.END)
            self.setting_entry13.insert(1, self.frame_rate)
            
        if self.predefine_w < 1:
            self.predefine_w = 1
            self.setting_entry06.delete(0, tk.END)
            self.setting_entry06.insert(1, self.predefine_w)
            
        if self.predefine_h < 1:
            self.predefine_h = 1
            self.setting_entry07.delete(0, tk.END)
            self.setting_entry07.insert(1, self.predefine_h)
        
        # except ValueError:
        #     exception_settingswrongvalue()
        
        if not self.is_hidden:    # not saved if hidden
            self.window_x = self.parent.winfo_x()
            self.window_y = self.parent.winfo_y()
        
        self.video_x = self.video.winfo_x()
        self.video_y = self.video.winfo_y()
        
        self.setting_x = self.settings.winfo_x()
        self.setting_y = self.settings.winfo_y()
        
        self.select_con_x = self.select_con.winfo_x()
        self.select_con_y = self.select_con.winfo_y()
        
        # Save config
        # try:
        self.config_file = open(self.config_path, "w")
        
        # except PermissionError:
        #     exception_settingnopermission()
        
        try:
            self.config.add_section("SnippingTool")
            
        except configparser.DuplicateSectionError:
            pass                                   # exception if already have config and section
        
        finally:
            self.config.set("SnippingTool", "skiparea_check", str(self.is_skiparea))
            self.config.set("SnippingTool", "cursor_check", str(self.is_cursor))
            self.config.set("SnippingTool", "predefine_check", str(self.is_predefine))
            self.config.set("SnippingTool", "vid_saveas", str(self.vid_saveas))
            self.config.set("SnippingTool", "delay", str(self.delay))
            self.config.set("SnippingTool", "save_path", str(self.save_path))
            self.config.set("SnippingTool", "frame_rate", str(self.frame_rate))
            self.config.set("SnippingTool", "predefine_w", str(self.predefine_w))
            self.config.set("SnippingTool", "predefine_h", str(self.predefine_h))
            self.config.set("SnippingTool", "window_x", str(self.window_x))
            self.config.set("SnippingTool", "window_y", str(self.window_y))
            self.config.set("SnippingTool", "setting_x", str(self.setting_x))
            self.config.set("SnippingTool", "setting_y", str(self.setting_y))
            self.config.set("SnippingTool", "video_x", str(self.video_x))
            self.config.set("SnippingTool", "video_y", str(self.video_y))
            self.config.set("SnippingTool", "select_con_x", str(self.select_con_x))
            self.config.set("SnippingTool", "select_con_y", str(self.select_con_y))
            
        self.config.write(self.config_file)
        self.config_file.close()
        
        # Hide
        self.setting_hide()
            
        self.delay = int(self.delay)
                       
    def setting_hide(self):                            # in windw and fullscreen mode
        print("setting_hide")
        logging.info("setting_hide")
        
        self.settings_button.config(text = "Settings", command=self.setting_buttonclick)
        
        self.settings.attributes('-topmost', False)
        self.settings.withdraw()

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

# In[Initial]

if __name__ == "__main__":
    # set winfo size to fit with screen size, but the running speed is much slower
    # default dpi size is 1536x864, instead of 1920x1080
    windll.shcore.SetProcessDpiAwareness(2) # your windows version should >= 8.1, otherwise it will raise exception.
    
    logging_create()
    
    style = Style(theme='darkly')                             # need manual modification of theme file
    style_master = style.master                                         # create window by ttk

    window = WindowGUI(style_master)
    
    window.set_appwindow()
    
    window.mainloop()        # must add at the end to make it run
    
    logging_shutdown()
    
    time.sleep(0.5)              # sleep for 0.5 sec for quit function
    
    os._exit(1)

# In[things to do]

'''
Functionality:
ctrl c for gif (no solution so far)

exe issue:

Optimization:

Bug:
    
Known bug that can't be fixed:
    
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

pyinstaller --noconfirm --onedir --windowed --icon "C:/Users/simon/Practice/SimonAlpaca Snipping Tool/alpaca_ico.ico" --ascii --no-embed-manifest --paths "C:/ProgramData/Anaconda3/lib/site-packages/cv2:C:/ProgramData/Anaconda3/lib/site-packages/imageio" --collect-all "ttkbootstrap"  "C:/Users/simon/Practice/SimonAlpaca Snipping Tool/SimonAlpaca Snipping Tool.py"

6) replace imageio folder and ttkbootstrap folder
'''
