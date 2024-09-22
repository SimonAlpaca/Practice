# -*- coding: utf-8 -*-
# Project started on 5/11/2022

import os
import sys
import time
import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk
from ctypes import windll
import mss
import cv2
import numpy as np
import PIL

# In[GUI]
class WindowGUI(tk.Frame):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.to_dir = ""
        self.full_w, self.full_h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.select_range = None
        self.image_mode = False
        self.video_mode = False
        
        style.configure("primary.TButton", font=("Helvetica", 9,"bold")) # letter button
        style.map("primary.TButton", foreground=[("disabled", "grey")])   # appearance of disabled button
        
        self.parent.overrideredirect(True)                                  
        self.parent.geometry('330x90+300+150')                                 # window size  
        self.parent.resizable(width=False,height=False)                   # disallow window resize
        self.parent.title("SimonAlpaca Snipping Tool")                  # title
        self.parent.withdraw()
        
        self.frame_top1 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_top1.pack(pady=1, side = tk.TOP, fill = "both")
        self.quit_button = ttk.Button(self.frame_top1, text= "\u03A7", width=3, style='primary.Outline.TButton', command = self.quit)
        self.quit_button.pack(side =tk.RIGHT, padx = 10)
        self.progress_text = tk.Text(self.frame_top1, height=1, width=25, background='gray25')
        self.progress_text.pack(side=tk.LEFT, padx = 10)
        
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
        self.settings_button = ttk.Button(self.frame_mid1, text= "Settings", width=10, style='primary.TButton', command= self.pass_)
        self.settings_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")  
        self.save_button = ttk.Button(self.frame_mid1, text= "Save", width=10, style='primary.TButton', command= self.pass_)
        self.save_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")  
        
        self.preview_canvas = tk.Canvas(self.frame_bot, width=900,height=600,scrollregion=(0,0,self.full_w + 20, self.full_h + 20), highlightthickness = 5)
        self.preview_canvas.pack(side=tk.LEFT)
        self.preview_canvas.configure(background='black')
        
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
            ico_path = os.path.join(exe_dir, "Alpaca_ico.ico")
            self.parent.iconbitmap(ico_path)                   # must be parent otherwise can't show program in taskbar   
        
        except:
            pass
        
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)               # when close in taskbar
        
        self.parent.update()
        # self.set_appwindow()
        
        # Program icon
        try:                                                   
            exe_dir = os.path.split(sys.argv[0])[0]            # sys.argv[0] is the exe path
            ico_path = os.path.join(exe_dir, "Alpaca_ico.ico")
            self.parent.iconbitmap(ico_path)                   # must be parent otherwise can't show program in taskbar   
        
        except:
            pass
        
        # GUI of Select Area
        self.popup = tk.Toplevel(self.parent)
        self.popup.resizable(False,False)
        self.popup.overrideredirect(1)
        
        self.popup.geometry("%dx%d+0+0" % (self.full_w, self.full_h))
        self.pic_canvas = tk.Canvas(self.popup, width = self.full_w, height = self.full_h, highlightthickness = 0)
        self.pic_canvas.pack()
        
        self.popup.attributes("-alpha", 0.1)

        self.popup.bind("<Escape>", self.area_quit)
        self.popup.bind('<Button-1>', self.area_predrag)
        self.popup.bind('<B1-Motion>', self.area_drag)
        self.popup.bind('<ButtonRelease-1>', self.button_release)
        
        self.popup.withdraw()
        
        # GUI of Video Cap
        self.video = tk.Toplevel(self.parent)
        self.video.resizable(False,False)
        self.video.overrideredirect(1)
        
        self.video.geometry("220x40+100+800")
        style.configure("secondary.TButton", font=("Helvetica", 8,"bold")) # letter button
        self.start_button = ttk.Button(self.video, text= "Start", width=6, style='secondary.TButton', command= self.start_button_click)
        self.start_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")              # padx means gap of x-axis
        self.finish_button = ttk.Button(self.video, text= "Finish", width=6, style='secondary.TButton', command= self.finish_button_click)
        self.finish_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")              # padx means gap of x-axis
        self.cancel_button = ttk.Button(self.video, text= "X", width=5, style='secondary.TButton', command= self.pass_)
        self.cancel_button.pack(side=tk.LEFT, padx = 5, pady = 5, fill = "both")  

        # Video Drag
        self.video.bind('<Button-1>', self.video_predrag)
        self.video.bind('<B1-Motion>', self.video_drag)
        
        self.video.deiconify()
        self.video.attributes('-topmost', True)

        self.video.withdraw()
    
    def window_changesize(self, width, height):
        
        adj_width = 450 + max(0, min(800, width - 450))
        adj_height = 90 + 30 + max(0, min(500, height))      # 30 for the scrollbar
        
        adj_canva_width = 420 + max(0, min(800, width - 450))
        adj_canva_height = 0 + max(0, min(500, height))
        
        self.parent.geometry('%sx%s+200+150' %(adj_width, adj_height))           # window size  
        self.preview_canvas.configure(width = adj_canva_width, height = adj_canva_height)
        
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
        self.after(100, self.show_appwindow)
    
    def show_appwindow(self):
        
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
    
    def video_predrag(self, event):
        
        self.video_offsetx = event.x
        self.video_offsety = event.y
        
    def video_drag(self, event):
        
        x = self.video.winfo_x() + event.x - self.video_offsetx
        y = self.video.winfo_y() + event.y - self.video_offsety
    
        self.video.geometry('+{x}+{y}'.format(x=x,y=y))
            
    def quit(self):
        
        self.parent.destroy()

# In[Select Area]

    def area_enter(self):
        
        self.parent.withdraw()
        
        self.popup.focus_set()
        self.popup.deiconify()
        self.popup.attributes('-topmost', True)
        
        self.i = 0
        
    def area_quit(self, event=None):
        
        if self.i != 0 :
            self.pic_canvas.delete(globals()["rect_%s" %self.i])
        
        self.i = 0
        
        self.popup.update()
        self.popup.withdraw()
        self.popup.attributes('-topmost', False)
    
    def area_predrag(self, event):
        
        self.left = event.x
        self.top = event.y
        
        self.width = event.x + 1          # for fixing crash when clicking without dragging
        self.height = event.y + 1         # for fixing crash when clicking without dragging
    
    def area_drag(self, event):

        self.width = event.x
        self.height = event.y
        
        pre_i = self.i
        self.i = self.i + 1
    
        globals()["rect_%s" %self.i] = self.pic_canvas.create_rectangle(self.left, self.top, self.width, self.height, fill='white')
        
        if pre_i != 0 :
            self.pic_canvas.delete(globals()["rect_%s" %pre_i])
        
    def pass_(self):
        
        pass
    
    def button_release(self, event):
        
        if self.image_mode:
            self.area_quit()
            
            width, height, img = self.cap_image()

            self.window_changesize(width, height)
        
            self.ShowIMG(img)
            
            self.parent.deiconify()
            self.parent.focus_set()
            self.parent.attributes('-topmost', True)
            self.parent.attributes('-topmost', False)
            
            self.image_mode = False
            
        if self.video_mode:
            self.area_quit()
            
            self.video.deiconify()
            self.video.attributes('-topmost', True)
            
            self.video_mode = False
            
# In[Image Cap]
    
    def image_button_click(self):
        
        self.image_mode = True
        
        self.preview_canvas.delete("all")   
        
        self.area_enter()
    
    def cap_image(self):
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
        
        output_path = r"C:\Users\simon\Practice\test.jpg"
        cv2.imwrite(output_path, img)
        
        return width, height, img
    
# In[Video Cap]

    def video_button_click(self):
        
        self.video_mode = True
        self.pause_vid = False
        self.stop_vid = False
        self.is_vid = False
        
        self.preview_canvas.delete("all")   
        
        self.area_enter()
        
    def start_button_click(self):
        
        self.start_button.configure(text= "Pause", command= self.pause_button_click)
        self.video.update()
        
        self.pause_vid = False
        
        if not self.is_vid:
            width, height, pic_frame = self.cap_video()
            self.window_changesize(width, height)
            self.ShowANI(pic_frame)
        
    def pause_button_click(self):
        
        self.start_button.configure(text= "Start", command= self.start_button_click)
        self.video.update()
        
        self.pause_vid = True
        
    def finish_button_click(self):
        
        self.stop_vid = True
        self.start_button.configure(text= "Start", command= self.start_button_click)
        self.video.withdraw()
        
        self.parent.deiconify()
        self.parent.attributes('-topmost', True)
        self.parent.attributes('-topmost', False)
        
    def cap_video(self):
        
        self.is_vid = True
        
        top = self.top
        left = self.left
        width = self.width - self.left
        height = self.height - self.top
        output = r"C:\Users\simon\Practice\video.avi"
        fps = 30
        
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
            # monitor_1 = mss_instance.monitors[1]           # whole screen
            monitor_1 = {"top": top, "left": left, "width": width, "height": height}
            screenshot = mss_instance.grab(monitor_1)
        
        print(monitor_1)
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, fps, (width, height))
        pic_frame = []
        
        while True:
            self.video.update()
            
            while self.pause_vid:
                time.sleep(0.01)
            
            if self.stop_vid:
                break
            
            time_start = time.perf_counter()
            
            with mss.mss() as mss_instance:
                screenshot = mss_instance.grab(monitor_1)
            
            pic_frame.append(screenshot)
            
            time_spent = time.perf_counter() - time_start
            print(time_spent)
            time.sleep(max(1/fps - time_spent, 0))
        
        print("Generating Video")
        self.progress_text.insert("1.0", "Generating Video")
        self.image_button.config(state=tk.DISABLED)
        self.vid_button.config(state=tk.DISABLED)
        self.settings_button.config(state=tk.DISABLED)
        self.parent.update()
        
        i = 0
        for frame in pic_frame:
            progress_percentage = int(round(i/len(pic_frame), 2) * 100)
            self.progress_text.delete('1.0', '2.0')
            self.progress_text.insert("1.0", "Generating Video (%s%%)" %progress_percentage)
            self.parent.update()
            i = i + 1
            
            frame = PIL.Image.frombytes("RGB", frame.size, frame.bgra, "raw", "BGRX")  # Convert to PIL.Image
            img_np = np.array(frame)
            image = cv2.cvtColor(np.array(img_np), cv2.COLOR_RGB2BGR)
            out.write(image)
            
        out.release()
        cv2.destroyAllWindows()
        
        self.is_vid = False
        print("Vid Generated")
        self.progress_text.delete('1.0', '2.0')
        self.image_button.config(state=tk.NORMAL)
        self.vid_button.config(state=tk.NORMAL)
        self.settings_button.config(state=tk.NORMAL)
        self.parent.update()
        
        return width, height, pic_frame
    
# In[Preview]

    def ShowIMG(self, img):
    
        self.parent.update()                                 # update pic_w, pic_h for fullscreen resize 
        self.preview_canvas.delete("all")                        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.preview_canvas.image = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(img))
        self.preview_canvas.create_image(10,10, anchor="nw", image = self.preview_canvas.image)
        
        self.parent.update()

    def ShowANI(self, pic_frame) :                   
        
        ani_preview = []

        for frame in pic_frame[:300]:            # set the max frame of preview to 300 frames
            frame = PIL.Image.frombytes("RGB", frame.size, frame.bgra, "raw", "BGRX")  # Convert to PIL.Image
            img_np = np.array(frame)
            ani_preview.append(img_np)
            
        i = 0
        
        gif_len = len(ani_preview)
        
        del pic_frame
        
        while True:          # loop gif until stop
            timer_start = time.perf_counter()
            
            if self.image_mode or self.video_mode:       # stop ShowANI when clicking image or video
                break
            
            gif_dur = 30/1000
                
            self.pic_canvas.delete("all")                 # remove existing image
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
    
# In[Initial]

if __name__ == "__main__":
    # set winfo size to fit with screen size, but the running speed is much slower
    # default dpi size is 1536x864, instead of 1920x1080
    windll.shcore.SetProcessDpiAwareness(2) # your windows version should >= 8.1, otherwise it will raise exception.
    style = Style(theme='darkly')                             # need manual modification of theme file
    style_master = style.master                                         # create window by ttk

    window = WindowGUI(style_master)
    
    window.set_appwindow()
    
    window.mainloop()        # must add at the end to make it run
    
    os._exit(1)

# In[things to do]

'''
Functionality:
save
ctrl c for img
settings and config
setting: skip area selection and use last selection (instead of area controller)
temp video file to support very long video cap

Optimization:
fps adj to running speed?
    
Bug:
    
'''
