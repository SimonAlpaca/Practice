# -*- coding: utf-8 -*-
# author: SimonAlpaca
# project started on 25/8/2021

import tkinter as tk
import os
import sys
from PIL import Image, ImageTk, ImageSequence
import time
import configparser
import logging

# In[Logging]

def logging_create():
    
    exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
    logging_path = os.path.join(exe_dir, "err_handling.log")
    logging.basicConfig(level = logging.DEBUG, filename = logging_path, filemode = "w")

def logging_shutdown():
    
    logging.shutdown()
    
# In[GUI]

def GUI():
    print("GUI")
    logging.info("GUI")
   
    global window
    global listlevel
    global pic_canvas
    global listbox1
    global folder_entry
    global listbox_button
    global setting_button
    global error_label
    global full_w, full_h
    
    # Window
    window = tk.Tk()                                          # create window
    full_w, full_h = window.winfo_screenwidth(), window.winfo_screenheight()  # get screen width and screen height
    window.geometry('500x580+300+150')                                 # window size  
    window.resizable(width=True,height=True)                   # disallow window resize
    window.title("SimonAlpaca Picture Viewer")                  # title
    window.configure(background="white")                         # background colour
    
    try:                                                   # tkinter icon
        exe_dir = os.path.split(sys.argv[0])[0]            # sys.argv[0] is the exe path
        ico_path = os.path.join(exe_dir, "Alpaca_ico.ico")
        window.iconbitmap(ico_path)                     
    
    except:
        pass
    
    ImportSettings()                                          # import default settings or config
    
    window.geometry('%dx%d+%d+%d' %(int(window_width), int(window_height), int(window_x), int(window_y))) # re adjust window size
    window.state(window_state)      # zoomed or normal
    
    # Canvas
    pic_canvas = tk.Canvas()
    pic_canvas.configure(background='white')
    pic_canvas.pack(side=tk.TOP, fill="both", expand=True, pady = 10, padx =10)
    pic_canvas.configure(scrollregion = pic_canvas.bbox("all"))
    
    # Bottom Button
    buttondown_frame = tk.Frame(window,background="white")             # add frame first
    buttondown_frame.pack(pady=5, side = tk.BOTTOM)
    
    quit_button = tk.Button(buttondown_frame, text = "Quit", command=quit,width=8) # destroy to quit
    quit_button.pack(side=tk.RIGHT,padx=10)
    
    go_button = tk.Button(buttondown_frame, text = "GO", command=go,width=12)
                           
    check_button = tk.Checkbutton(buttondown_frame, text="Include Subfolder", var=parent_check, background="white")
    check_button.pack(side=tk.RIGHT, padx = 0)
    
    go_button.pack(side=tk.RIGHT,padx=10)              # padx means gap of x-axis
    
    listbox_button = tk.Button(buttondown_frame, text = "Hide List", command=hide_listbox,width=8) # destroy to quit
    listbox_button.pack(side=tk.LEFT,padx=10)
    
    setting_button = tk.Button(buttondown_frame, text = "Settings", command=show_settings,width=8) # destroy to quit
    setting_button.pack(side=tk.LEFT,padx=10)
    
    # Error label
    error_frame = tk.Frame(window,background="white")               
    error_frame.pack(pady=0, fill="y", side = tk.BOTTOM)
    error_label = tk.Label(error_frame, text = "", fg = "red", font = ("Arial", 10), background = "white")
    error_label.pack()
    
    # Path
    folder_frame = tk.Frame(window,background="white")               
    folder_frame.pack(pady=0, fill="y", side = tk.BOTTOM)               # pady means gap of y-axis, fill both means aligh to left and right
    folder_label = tk.Label(folder_frame, text = "Folder Name : " ,background="white")
    folder_label.pack(side=tk.LEFT)
    folder_entry = tk.Entry(folder_frame, width=54)
    folder_entry.insert(1, default_path)
    folder_entry.pack()
    
    # Up Button
    buttonup_frame = tk.Frame(window,background="white")
    buttonup_frame.pack(fill = "y", side = tk.BOTTOM, pady = 5)
    backward_button = tk.Button(buttonup_frame, text = "<-", command=backward,width=10)
    backward_button.pack(side =tk.LEFT, padx = 20)
    full_button = tk.Button(buttonup_frame, text = "[]", command=fullscreen,width=10)
    full_button.pack(side =tk.LEFT, padx = 20)
    forward_button = tk.Button(buttonup_frame, text = "->", command=forward,width=10)
    forward_button.pack(side =tk.LEFT, padx = 20)
    
    # Pop up and Listbox
    listlevel = tk.Toplevel(window)
    listlevel.resizable(False,False)
    listlevel.overrideredirect(1)
    listlevel.geometry("250x550+50+%d" %(full_h-700))
    listlevel.configure(background="white")   
    
    listbox_scroll = tk.Scrollbar(listlevel)                     # add scroll bar
    listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    w, h = listlevel.winfo_screenwidth(), listlevel.winfo_screenheight()
    listbox1 = tk.Listbox(listlevel,width=w-80,height=h,highlightthickness=5, selectmode = tk.SINGLE, yscrollcommand = listbox_scroll.set)
    listbox1.configure(background='white')
    listbox1.pack(side=tk.LEFT)
    
    listbox1.bind("<Double-Button-1>", select_listbox)
    
    listbox_scroll.config(command = listbox1.yview)
    
    window.focus_set()
    
    window.protocol("WM_DELETE_WINDOW", quit)
    
    hide_listbox()
    
    window.after(100, start)    # run def "start" first

    window.mainloop()        # must add at the end to make it run

# In[Start]

def start():
    print("start")
    logging.info("start")
    
    global supported_img
    global supported_ani
    global check_width
    global check_height
    
    # Supported format
    supported_img = [".jpg", ".jpeg", ".png", ".bmp", ".jfif", ".ico", ".webp", ".JPG", ".JPEG", ".PNG", ".BMP", ".JFIF", ".ICO", ".WEBP"]
    supported_ani = [".gif", ".GIF"]
    
    supported_img = set(supported_img)      # create set
    supported_ani = set(supported_ani)
    
    window.bind("<Configure>",event_resize)           # trigger event, after loading GUI
    window.bind("<MouseWheel>",event_zoom)            # trigger zoom event

    filepath = str(folder_entry.get())
    
    check_width = [window.winfo_width(), window.winfo_width()]
    check_height = [window.winfo_height(), window.winfo_height()]
    
    if filepath != "":
        go()
            
# In[Go Button]

def go():
    print("go")
    logging.info("go")
    
    global fileindex
    global filesplit
    global fullfilelist
    global filepath
    global full_mode
    global stop_ani
    global zoom_factor
    global listbox1
    global manga_mode
    global origX, origY
    
    manga_mode = False
    full_mode = False
    stop_ani = True
    zoom_factor = 1
    
    origX = pic_canvas.xview()[0]                # original canvas position for zoom and move
    origY = pic_canvas.yview()[0]
    
    listbox1.delete(0,"end")                         # clear listbox
    
    filepath = str(folder_entry.get())
    parent_bool = parent_check.get()
    if os.path.isdir(filepath) == False:              # handle dir path
        filesplit = os.path.split(filepath)           # separate dir path and file name
    
    else:
        filesplit = [filepath, ""]
    
    fullfilelist = []
    filename = ""
    
    if os.path.exists(filepath) == False:         # check whether the dir exists
        exception_dirnotfound()
        
    if os.access(filepath, os.R_OK) == False:     # check whehter the dir has read permission
        exception_dirnopermission()
    
    if parent_bool == False:                      # exclude sub folder
    
        filelist = os.listdir(filesplit[0])  
        filelist.sort()
        for filename in filelist:
            
            fullpathname = os.path.join(filesplit[0],filename)
            file_ext = os.path.splitext(fullpathname)[1]
            
            if file_ext in (supported_img|supported_ani):  #filter not support format
                fullfilelist.append(fullpathname)    # full path in list
            
            else:
                print("Not Supported : ", filename)
                logging.info("Not Supported : %s", filename)
    
    else:                                        # include sub folder
        file_walk = os.walk(filesplit[0])
        
        timeout_start = time.time()
        timeout = 10
        
        for root,dir,files in file_walk:
            dir.sort()
            files.sort()
            
            for file in files:
                
                if time.time() > timeout_start + timeout:       # timeout if the dir too large
                    exception_dirtoolarge()
                 
                fullpathname = os.path.join(root,file)
                file_ext = os.path.splitext(fullpathname)[1]
                
                if file_ext in (supported_img|supported_ani):    #filter not support format
                    fullfilelist.append(fullpathname)
                
                else:
                    if len(file_ext) > 0:
                        print("Not Supported : ", file)
                        logging.info("Not Supported : %s", file)
    
    if len(fullfilelist) == 0:
        exception_dirnosupportedfile()
    
    for path in fullfilelist:
        filename = os.path.split(path)
        listbox1.insert(tk.END, filename[1])                      # put file name in listbox
    
    try:
        fileindex = fullfilelist.index(filepath)                 # 0 if filepath is dir
    
    except:
        fileindex = 0
    
    filepath = fullfilelist[fileindex]
    
    file_ext = os.path.splitext(filepath)[1]      # separate file name and extension
    
    folder_entry.delete(0,"end")
    folder_entry.insert(1, filepath)             # replace folder entry
    
    if file_ext in supported_img:                 # show in window mode
        ShowIMG(filepath)
    
    elif file_ext in supported_ani:
        ShowANI(filepath)
    
# In[Quit Button]

def quit():
    print("quit")
    logging.info("quit")
    
    global stop_ani
    
    stop_ani = True
    
    show_settings()              # run and save settings
    ok_settings()                # settings toplevel destroyed
    
    try:
        popup.destroy()
        popup2.destroy()
        
    except:
        pass
    
    listlevel.destroy()
    window.destroy()

# In[Forward Button]

def forward():                                  # all modes except manga mode
    print("forward")
    logging.info("forward")
   
    global fileindex
    global zoom_factor
    global stop_ani
    
    stop_ani = True                             # stop previous ani
    zoom_factor = 1                             # reset zoom
    cancel_move()
    
    fileindex = fileindex + 1                    # next file

    if fileindex == len(fullfilelist):           # back to start
        fileindex = 0

    nextpath = fullfilelist[fileindex]          # get path of next file
    
    folder_entry.delete(0,"end")
    folder_entry.insert(1, nextpath)             # replace folder entry
    file_ext = os.path.splitext(nextpath)[1]
    if file_ext in supported_img:                # img
                                     
        if full_mode == True:
            
            if zoom_slide_mode == True:
                ShowIMG_FullZoomSlide(nextpath)  # zoom slide mode
            
            else:   
                ShowIMG_Full(nextpath)            # slide mode or simple fullscreen
        
        else:
            ShowIMG(nextpath)                    # window mode
            
    else:                                       # gif
        if full_mode == True:
            time.sleep(0.1)
            ShowANI_Full(nextpath)             # simple fullscreen, slide mode, zoom slide mode
            
            if manga_mode == True:
                forward()                       # skip gif in manga mode
        
        else:
            ShowANI(nextpath)
            
# In[Backward Button]

def backward():                               # all modes except manga mode
    print("backward")
    logging.info("backward")
    
    global fileindex
    global zoom_factor
    global stop_ani
    
    stop_ani = True                            # stop previous ani
    zoom_factor = 1                            # reset zoom
    cancel_move()
    
    fileindex = fileindex - 1                  # previous file
    if fileindex < 0:                          # back to end
        fileindex = len(fullfilelist) - 1
            
    filepath = fullfilelist[fileindex]         # get path of previous file
    
    folder_entry.delete(0,"end")
    folder_entry.insert(1, filepath)           # replace folder entry
    file_ext = os.path.splitext(filepath)[1]
    if file_ext in supported_img:                 # img
                                                  
        if full_mode == True:
            
            if zoom_slide_mode == True:
                ShowIMG_FullZoomSlide(filepath)   # zoom slide mode
            
            else:   
                ShowIMG_Full(filepath)            # simple fullscreen or slide mode
        
        else:
            ShowIMG(filepath)                     # window mode 
            
    else:                                         # gif                                             
        if full_mode == True:                  
            ShowANI_Full(filepath)                # simple fullscreen, slide mode, zoom slide mode
            
            if manga_mode == True:
                backward()                        # skip gif in manga mode
        
        else:
            ShowANI(filepath)                     # window mode
            
# In[Listbox]

def show_listbox():                          # in window and fullscreen mode
    print("show_listbox")    
    logging.info("show_listbox")
    
    try:    
        listbox_button2.config(text = "Hide", command=hide_listbox)
        popup.unbind("<Motion>",motion1)    # fullscreen mode 
        popup.unbind("<Button-1>", fullforward)
        popup.unbind("<Button-3>", fullbackward)    
    
    except:
        pass
    
    listbox_button.config(text = "Hide List", command=hide_listbox)
    listlevel.deiconify()
    listbox1.focus_set()
    
def select_listbox(event):
    print("select_listbox")
    logging.info("select_listbox")
    
    global fileindex
    
    fileindex = listbox1.curselection()[0]     # select on listbox, return integer
    filepath = fullfilelist[fileindex]
    folder_entry.delete(0,"end")
    folder_entry.insert(1, filepath)           # replace folder entry
    file_ext = os.path.splitext(filepath)[1]      # separate file name and extension
    
    if full_mode == False:                      # window mode
        
        if file_ext in supported_img:
            ShowIMG(filepath)
        
        elif file_ext in supported_ani:
            ShowANI(filepath)
   
    else:                                        # full screen mode
        hide_listbox()
        
        if file_ext in supported_img:
            ShowIMG_Full(filepath)
        
        elif file_ext in supported_ani:
            ShowANI_Full(filepath)
        
def hide_listbox():                            # in fullscreen mode
    print("hide_listbox")
    logging.info("hide_listbox")
    
    global motion1
    global button1
    global button3
    
    try:
        listbox_button2.config(text = "List", command=show_listbox)
        motion1 = popup.bind("<Motion>",motion)
        button1 = popup.bind("<Button-1>", fullforward)
        button3 = popup.bind("<Button-3>", fullbackward)
        
    except:
        pass
    
    listbox_button.config(text = "List", command=show_listbox)
    listlevel.withdraw()

# In[Settings]

def ImportSettings():
    print("ImportSettings") 
    logging.info("ImportSettings")
    
    global parent_check
    global gif_speed
    global default_path
    global default_timer
    global gif_loop
    global timer_frame
    global scroll_multiplier
    global manga_resize
    global auto_frame
    global auto_dis
    global setting_gifspeedstr
    global setting_scrollstr
    global setting_imagesizestr
    global setting_autospeedstr
    global config
    global config_path
    global window_width
    global window_height
    global window_x
    global window_y
    global window_state
    
    # Default Settings
    # window mode
    window_width = 500
    window_height = 580
    window_x = 300
    window_y = 150
    window_state = "normal"
    
    parent_check = tk.BooleanVar()
    parent_bool = False
    parent_check.set(False)                        # include subfolder
    
    try:
        default_path = sys.argv[1]                 # sys.argv[1] is the image path
    
    except:
        default_path = ""                          # if double-click the exe
    
    gif_speed = 1.0
    
    # simple fullscreen mode
    
    # slide mode and photo album mode
    default_timer = 5                              # timer for images
    gif_loop = 3                                   # times of gif loop for each slide
    
    # photo album mode
    timer_frame = 50                               # frame of image move
    
    # phto album mode and manga mode
    scroll_multiplier = 0.7                        # scroll distance, equal to half second
    
    # manga mode
    manga_resize = 1                               # width in manga mode
    auto_frame = 40                                # frame of auto manga
    auto_dis = 200                                 # distance of auto per second 
    
    setting_gifspeedstr = "Normal"
    setting_scrollstr = "Normal"
    setting_imagesizestr = "Fullscreen"
    setting_autospeedstr = "Normal"
    
    # Import config
    config = configparser.ConfigParser()
    
    exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
    config_path = os.path.join(exe_dir, "config.ini")
    config.read(config_path)
    
    parent_bool = str(getconfig("parent_check", parent_bool))
    parent_check.set(parent_bool)
    gif_speed = float(getconfig("gif_speed", gif_speed))
    default_timer = int(getconfig("default_timer", default_timer))
    gif_loop = int(getconfig("gif_loop", gif_loop))
    scroll_multiplier = float(getconfig("scroll_multiplier", scroll_multiplier))
    manga_resize = float(getconfig("manga_resize", manga_resize))
    auto_dis = int(getconfig("auto_dis", auto_dis))
    setting_gifspeedstr = str(getconfig("setting_gifspeedstr", setting_gifspeedstr))
    setting_scrollstr = str(getconfig("setting_scrollstr", setting_scrollstr))
    setting_imagesizestr = str(getconfig("setting_imagesizestr", setting_imagesizestr))
    setting_autospeedstr = str(getconfig("setting_autospeedstr", setting_autospeedstr))
    window_width = str(getconfig("window_width", window_width))
    window_height = str(getconfig("window_height", window_height))
    window_x = str(getconfig("window_x", window_x))
    window_y = str(getconfig("window_y", window_y))
    window_state = str(getconfig("window_state", window_state))
    
def getconfig(column, var):

    try:
        return config.get("ImageViewer", str(column))
    
    except:
        return var
    
def show_settings():                          # in window and fullscreen mode
    print("show_settings") 
    logging.info("show_settings")
    
    global settinglevel
    global setting_check2
    global setting_entry5
    global setting_entry6
    global setting_scroll
    global setting_gifspeed
    global setting_imagesize
    global setting_autospeed
    global setting_error
    
    try:    
        settings_button2.config(text = "Hide", command=hide_settings)
        popup.unbind("<Motion>",motion1)    # fullscreen mode 
        popup.unbind("<Button-1>", fullforward)
        popup.unbind("<Button-3>", fullbackward) 
        
    except:
        pass
    
    setting_button.config(text = "Hide", command=hide_settings)
    
    settinglevel = tk.Toplevel(window)
    settinglevel.resizable(False,False)
    settinglevel.overrideredirect(1)
    settinglevel.geometry("350x500+%d+%d" %(full_w-350-100, full_h-500-150))
    settinglevel.configure()  
    
    setting_frame0 = tk.Frame(settinglevel)             
    setting_frame0.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame1 = tk.Frame(settinglevel, highlightthickness=5, background='white')             
    setting_frame1.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame2 = tk.Frame(settinglevel)             
    setting_frame2.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame3 = tk.Frame(settinglevel)             
    setting_frame3.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame4 = tk.Frame(settinglevel , highlightthickness=5, background='white')             
    setting_frame4.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame5 = tk.Frame(settinglevel)             
    setting_frame5.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame6 = tk.Frame(settinglevel)             
    setting_frame6.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame7 = tk.Frame(settinglevel, highlightthickness=5, background='white')             
    setting_frame7.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame8 = tk.Frame(settinglevel)             
    setting_frame8.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame9 = tk.Frame(settinglevel, highlightthickness=5, background='white')             
    setting_frame9.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame10 = tk.Frame(settinglevel)             
    setting_frame10.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame11 = tk.Frame(settinglevel)             
    setting_frame11.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame13 = tk.Frame(settinglevel)             
    setting_frame13.pack(pady=5, side = tk.BOTTOM)
    
    setting_frame12 = tk.Frame(settinglevel)             
    setting_frame12.pack(pady=5, side = tk.BOTTOM)
    
    setting_label1 = tk.Label(setting_frame1, text = "General : ", background='white')
    setting_label1.pack(pady=0, side= tk.LEFT)
    
    setting_label2 = tk.Label(setting_frame2, text = "      Include Subfolder : " )
    setting_label2.pack(pady=0, side= tk.LEFT)
    
    setting_label3 = tk.Label(setting_frame3, text = "      GIF Speed : " )
    setting_label3.pack(pady=0, side= tk.LEFT)
    
    setting_label4 = tk.Label(setting_frame4, text = "Slide mode / Photo Album mode : ", background='white')
    setting_label4.pack(pady=0, side= tk.LEFT)
    
    setting_label5 = tk.Label(setting_frame5, text = "      Image Timer (seconds): " )
    setting_label5.pack(pady=0, side= tk.LEFT)
    
    setting_label6 = tk.Label(setting_frame6, text = "      GIF Loop (times): " )
    setting_label6.pack(pady=0, side= tk.LEFT)
    
    setting_label7 = tk.Label(setting_frame7, text = "Photo Album mode / Manga mode : ", background='white')
    setting_label7.pack(pady=0, side= tk.LEFT)
    
    setting_label8 = tk.Label(setting_frame8, text = "      Scroll : " )
    setting_label8.pack(pady=0, side= tk.LEFT)
    
    setting_label9 = tk.Label(setting_frame9, text = "Manga mode : ", background='white')
    setting_label9.pack(pady=0, side= tk.LEFT)
    
    setting_label10 = tk.Label(setting_frame10, text = "      Image Size : " )
    setting_label10.pack(pady=0, side= tk.LEFT)
    
    setting_label11 = tk.Label(setting_frame11, text = "      Auto Speed : " )
    setting_label11.pack(pady=0, side= tk.LEFT)
    
    setting_check2 = tk.Checkbutton(setting_frame2, text="", var=parent_check)
    setting_check2.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_gifspeed = tk.StringVar()
    setting_gifspeed.set(setting_gifspeedstr)
    setting_scroll3 = tk.OptionMenu(setting_frame3, setting_gifspeed, "Very Fast", "Fast", "Normal", "Slow", "Very Slow")
    setting_scroll3.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_entry5 = tk.Entry(setting_frame5, width=5)
    setting_entry5.insert(1, default_timer)
    setting_entry5.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_entry6 = tk.Entry(setting_frame6, width=5)
    setting_entry6.insert(1, gif_loop)
    setting_entry6.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_scroll = tk.StringVar()
    setting_scroll.set(setting_scrollstr)
    setting_scroll8 = tk.OptionMenu(setting_frame8, setting_scroll, "Fast", "Normal", "Slow")
    setting_scroll8.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_imagesize = tk.StringVar()
    setting_imagesize.set(setting_imagesizestr)
    setting_scroll10 = tk.OptionMenu(setting_frame10, setting_imagesize, "Normal", "Large", "Fullscreen")
    setting_scroll10.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_autospeed = tk.StringVar()
    setting_autospeed.set(setting_autospeedstr)
    setting_scroll11 = tk.OptionMenu(setting_frame11, setting_autospeed, "Fast", "Normal", "Slow")
    setting_scroll11.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_error = tk.Label(setting_frame12, text = "", fg = "red", font = ("Arial", 10))
    setting_error.pack()
    
    setting_button_save = tk.Button(setting_frame13, text = "Save and Close", command=ok_settings,width=20)
    setting_button_save.pack(side =tk.LEFT, padx = 20)
    
    setting_button_quit = tk.Button(setting_frame13, text = "Cancel", command=hide_settings,width=20)
    setting_button_quit.pack(side =tk.RIGHT, padx = 20)
    
    settinglevel.focus_set()

def ok_settings():
    print("ok_settings")
    logging.info("ok_settings")
    
    global default_timer
    global gif_speed
    global gif_loop
    global scroll_multiplier
    global manga_resize
    global auto_dis
    global setting_gifspeedstr
    global setting_scrollstr
    global setting_imagesizestr
    global setting_autospeedstr
    global window_width
    global window_height
    global window_x
    global window_y
    
    setting_error.config(text = "")
    
    # window mode
    # simple fullscreen mode
    setting_gifspeedstr = setting_gifspeed.get()
    if setting_gifspeedstr == "Very Fast":       
        gif_speed = 0.4
    
    elif setting_gifspeedstr == "Fast":
        gif_speed = 0.7
    
    elif setting_gifspeedstr == "Normal":
        gif_speed = 1.0
        
    elif setting_gifspeedstr == "Slow":
        gif_speed = 1.25
    
    elif setting_gifspeedstr == "Very Slow":
        gif_speed = 1.5
    
    # slide mode and photo album mode
    parent_bool = parent_check.get()
    
    try:
        default_timer = int(setting_entry5.get())                      # timer for images
    
    except ValueError:
        exception_settingswrongvalue()
    
    try:
        gif_loop = int(setting_entry6.get())                # times of gif loop for each slide
    
    except ValueError:
        exception_settingswrongvalue()
    
    # phto album mode and manga mode
    setting_scrollstr = setting_scroll.get()
    if setting_scrollstr == "Fast":       # scroll distance, equal to half second
        scroll_multiplier = 0.9
    
    elif setting_scrollstr == "Normal":
        scroll_multiplier = 0.7
    
    elif setting_scrollstr == "Slow":
        scroll_multiplier = 0.5
        
    # manga mode
    setting_imagesizestr = setting_imagesize.get()
    if setting_imagesizestr == "Fullscreen":        # width in manga mode
        manga_resize = 1
    
    elif setting_imagesizestr == "Large":
        manga_resize = 0.85
    
    elif setting_imagesizestr == "Normal":
        manga_resize = 0.7
    
    setting_autospeedstr = setting_autospeed.get()
    if setting_autospeedstr == "Fast":             # distance of auto per second 
        auto_dis = 300
    
    elif setting_autospeedstr == "Normal": 
        auto_dis = 200    
    
    elif setting_autospeedstr == "Slow": 
        auto_dis = 120
    
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    window_x = window.winfo_x()
    window_y = window.winfo_y()
    
    # Save config
    try:
        config_file = open(config_path, "w")
    
    except PermissionError:
        exception_settingnopermission()
    
    try:
        config.add_section("ImageViewer")
    
    except configparser.DuplicateSectionError:
        pass                                   # exception if already have config and section
    
    finally:
        config.set("ImageViewer", "parent_check", str(parent_bool))
        config.set("ImageViewer", "gif_speed", str(gif_speed))
        config.set("ImageViewer", "default_timer", str(default_timer))
        config.set("ImageViewer", "gif_loop", str(gif_loop))
        config.set("ImageViewer", "setting_scrollstr", setting_scrollstr)
        config.set("ImageViewer", "scroll_multiplier", str(scroll_multiplier))
        config.set("ImageViewer", "setting_gifspeedstr", setting_gifspeedstr)
        config.set("ImageViewer", "setting_imagesizestr", setting_imagesizestr)
        config.set("ImageViewer", "manga_resize", str(manga_resize))
        config.set("ImageViewer", "setting_autospeedstr", setting_autospeedstr)
        config.set("ImageViewer", "auto_dis", str(auto_dis))
        
        if window.state() == "zoomed":
            window_state = "zoomed"
            config.set("ImageViewer", "window_state", window_state)
            
        else:
            window_state = "normal"
            config.set("ImageViewer", "window_width", str(window_width))
            config.set("ImageViewer", "window_height", str(window_height))
            config.set("ImageViewer", "window_x", str(window_x))
            config.set("ImageViewer", "window_y", str(window_y))
            config.set("ImageViewer", "window_state", window_state)
        
    config.write(config_file)
    config_file.close()
    
    # Hide
    hide_settings()

def hide_settings():                            # in windw and fullscreen mode
    print("hide_settings")
    logging.info("hide_settings")
    
    global motion1
    global button1
    global button3
    
    try:
        settings_button2.config(text = "Settings", command=show_settings)
        motion1 = popup.bind("<Motion>",motion)
        button1 = popup.bind("<Button-1>", fullforward)
        button3 = popup.bind("<Button-3>", fullbackward)
        
    except:
        pass
    
    setting_button.config(text = "Settings", command=show_settings)
    settinglevel.destroy()
    
# In[Show Image]

def ShowIMG(pic_path):                         # window mode
    print("ShowIMG")    
    logging.info("ShowIMG")

    global stop_ani
    
    stop_ani = True
    
    error_label.config(text = "")
    pic_canvas.delete("all")                        
    
    if len(pic_path) > 255:
        exception_pathtoolong()
    
    try:
        img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
    
    except FileNotFoundError:
        exception_filenotfound()
        
    img_w, img_h = img.size
    
    window.update()
    
    try:
        pic_w,pic_h=pic_canvas.winfo_width(),pic_canvas.winfo_height()  # get canvas width and height
    
    except:
        pass                                          # exception when resize with 0 canvas
    
    if pic_w > 1 and pic_h > 1:
        resize_scale = min(pic_w/img_w,pic_h/img_h)   # calculate the resize ratio, maintaining height-width scale
        resize_scale = min(resize_scale,1)            # avoid bigger than original
        w,h=int(img_w*resize_scale*zoom_factor),int(img_h*resize_scale*zoom_factor)
        resize_img = img.resize((w,h))   
        pic_canvas.image = ImageTk.PhotoImage(resize_img)
        pic_canvas.create_image(pic_w/2,pic_h/2,anchor="center",image=pic_canvas.image)
            
# In[Show Animation]

def ShowANI(pic_path):                       # window mode
    print("ShowANI")
    logging.info("ShowANI")
    
    global stop_ani
    global ani_slide
    
    ani_slide = True
    stop_ani = False                         # enable running animation
    pic_canvas.delete("all")                 # remove existing image
    gif_img = []                             # create list to store frames of gif
    
    error_label.config(text = "")
    
    if len(pic_path) > 255:
        exception_pathtoolong()
        
    try:
        gif_img = Image.open(pic_path)
    
    except FileNotFoundError:
        exception_filenotfound()
    
    pic_w,pic_h=pic_canvas.winfo_width(),pic_canvas.winfo_height()

    while check_stop_ani() == False and check_full_mode() == False:          # loop gif until stop
        
        #logging.info("time_check3: %s", time.perf_counter())
        #timer_start2 = time.perf_counter()
        iter = ImageSequence.Iterator(gif_img)   # create iterator to get frames
        i = 0
        
        if pic_w > 1 and pic_h > 1:    
            img_w, img_h = iter[0].size
            resize_scale = min(pic_w/img_w,pic_h/img_h)   # calculate the resize ratio, maintaining height-width scale
            w,h=int(img_w*resize_scale),int(img_h*resize_scale)
            
            #time_diff2 = time.perf_counter() - timer_start2
            #print("time diff start: ", time_diff2)
            #logging.info("time_diff_start: %s", time_diff2)
            
            for frame in iter:
                timer_start = time.perf_counter()
                
                if check_stop_ani() == False: # stop animation controlled by other def
                    i = i + 1
                    print(i)
                    logging.info(i)
                    
                    gif_speed = check_gifspeed()
                    resize_img = frame.resize((w,h)) 
                    pic = ImageTk.PhotoImage(resize_img)
                    pic_canvas.create_image(pic_w/2,pic_h/2,anchor="center",image=pic)  # create image frame by frame
                    
                    window.update()
                    
                    try:
                        gif_duration = gif_img.info['duration']
                        print("duration: ", gif_duration)
                            
                    except:
                        gif_duration = 40
                    
                    time_diff = time.perf_counter() - timer_start
                    print("time diff: ", time_diff)
                       
                    sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.009))
                    print("sleep : ", sleep_time)
                    
                    time.sleep(sleep_time)
                    #logging.info("time_check1: %s", time.perf_counter())
                    if check_stop_ani() == False:
                        logging.info("duration: %s", gif_duration)
                        logging.info("time_diff: %s", time_diff)
                        logging.info("sleep : %s", sleep_time)
                    #logging.info("time_check2: %s", time.perf_counter())
                else:
                    break
                
    del iter

# In[When Resize]

def event_resize(event=None):          # window mode
    
    global zoom_factor
    
    listbox1.focus_set()
    zoom_factor = 1                    # reset zoom

    if event.width == window.winfo_width() and event.height == window.winfo_height(): # trigger
        check_width[0] = check_width[1]
        check_height[0] = check_height[1]
        check_width[1] = event.width
        check_height[1] = event.height
        
        if check_width[0] != check_width[1] or check_height[0] != check_height[1]: # 2nd trigger
            print("event_resize")
            logging.info("event_resize")

            filepath = str(folder_entry.get())
            file_ext = os.path.splitext(filepath)[1]                  # separate file name and extension
            
            if file_ext in supported_img:
                ShowIMG(filepath)
            
            #elif file_ext in supported_ani:
             #   ShowANI(filepath)                # can't resize ani
         
# In[When Zoom]

def event_zoom(event):                  # window mode or full screen mode         
    print("event_zoom")
    logging.info("event_zoom")
    
    global pic_canvas
    global zoom_factor
    global pic_move_from, pic_move_to
    
    x = pic_canvas.canvasx(event.x)
    y = pic_canvas.canvasy(event.y)
    
    if event.delta > 1:                           # scroll up
        zoom_factor = zoom_factor + 0.2
    
    else:                                         # scroll down
        zoom_factor = max(zoom_factor - 0.2, 1)
    
    filepath = str(folder_entry.get())
    file_ext = os.path.splitext(filepath)[1]
    
    if full_mode == True:                            
        if file_ext in supported_img:                 # skip gif
            ShowIMG_Full(filepath)
            
            try:
                full_canvas.scale(tk.ALL, x, y, zoom_factor, zoom_factor)
            
            except:
                pass                                  # exception when slide mode -> zoom -> quit
    
    else:                                             # move in window mode only
        if file_ext in supported_img:                 # skip gif
            ShowIMG(filepath)
            pic_canvas.scale(tk.ALL, x, y, zoom_factor, zoom_factor) 
    
        if zoom_factor > 1:
            pic_move_from = pic_canvas.bind('<ButtonPress-1>', move_from)
            pic_move_to = pic_canvas.bind('<B1-Motion>',     move_to)
        
        if zoom_factor == 1:                          # reset zoom
            cancel_move()
            ShowIMG(filepath)
        
def cancel_move():
    
    try:
        pic_canvas.unbind('<ButtonPress-1>', pic_move_from)
        pic_canvas.unbind('<B1-Motion>', pic_move_to)
    
    except:
        pass
    
    pic_canvas.xview_moveto(origX)
    pic_canvas.yview_moveto(origY)
    
def move_from(event):
        
    pic_canvas.scan_mark(event.x, event.y)

def move_to(event):
    
    pic_canvas.scan_dragto(event.x, event.y, gain=1)

# In[fullscreen mode]

def fullscreen():
    print("fullscreen")
    logging.info("fullscreen")
    
    global popup
    global popup2
    global full_canvas
    global slide_check
    global full_mode
    global motion1
    global button1
    global button3
    global button_esc
    global wheel
    global zoom_slide_mode
    global slide_button2
    global zoomslide_button2
    global listbox_button2
    global manga_button2
    global settings_button2
    
    slide_check = False
    full_mode = True
    zoom_slide_mode = False
    
    # GUI of Fullscreen
    popup = tk.Toplevel(window, bd=0)
    popup.resizable(False,False)
    popup.overrideredirect(1)
    
    popup.geometry("%dx%d+0+0" % (full_w, full_h))
    
    popup.focus_set()    
    
    button_esc = popup.bind("<Escape>", quit_full)
    button1 = popup.bind("<Button-1>", fullforward)
    button3 = popup.bind("<Button-3>", fullbackward)
    wheel = popup.bind("<MouseWheel>",event_zoom)            # trigger zoom event

    full_canvas = tk.Canvas(popup,width=full_w,height=full_h,highlightthickness=0)
    full_canvas.pack()
    full_canvas.configure(background='black')
    full_canvas.configure(scrollregion = full_canvas.bbox("all"))
    
    # Controller in fullscreen
    popup2 = tk.Toplevel(popup, bd=0)
    popup2.resizable(False,False)
    popup2.overrideredirect(1)
    popup2.geometry("640x50+%d+%d" % (full_w/2-640/2, full_h-64))
    
    listbox_button2 = tk.Button(popup2, text = "List", command=show_listbox,width=8)
    listbox_button2.pack(side =tk.LEFT, padx = 5)
    
    settings_button2 = tk.Button(popup2, text = "Settings", command=show_settings,width=8) # destroy to quit
    settings_button2.pack(side=tk.LEFT,padx= 23)
    
    backward_button2 = tk.Button(popup2, text = "<-", command=fullbackward,width=5)
    backward_button2.pack(side =tk.LEFT, padx = 1)
    
    forward_button2 = tk.Button(popup2, text = "->", command=fullforward,width=5)
    forward_button2.pack(side =tk.LEFT, padx = 5)
    
    quit_button2 = tk.Button(popup2, text = "X", command=quit_full,width=5)
    quit_button2.pack(side =tk.RIGHT, padx = 5)
    
    manga_button2 = tk.Button(popup2, text = "Manga Mode", command=start_manga,width=11)
    manga_button2.pack(side =tk.RIGHT, padx = 5)
    
    zoomslide_button2 = tk.Button(popup2, text = "Photo Album", command=start_zoomslide,width=10)
    zoomslide_button2.pack(side =tk.RIGHT, padx = 5)
    
    slide_button2 = tk.Button(popup2, text = "Slide Mode", command=start_slide,width=10)
    slide_button2.pack(side =tk.RIGHT, padx = 10)

    motion1 = popup.bind("<Motion>",motion)                          # control appearance controller
    
    filepath = fullfilelist[fileindex] 
    file_ext = os.path.splitext(filepath)[1]
    
    if file_ext in supported_img:                     # full screen mode
        ShowIMG_Full(filepath)
    
    else:
        ShowANI_Full(filepath)

def fullforward(event=0):                           # full screen mode
    print("fullforward")    
    logging.info("fullforward")

    global timer
    
    full_canvas.delete("all")
    
    timer = default_timer 
    
    forward()

def fullbackward(event=0):                           # full screen mode
    print("fullbackward")  
    logging.info("fullbackward")

    global timer
    
    full_canvas.delete("all")

    timer = default_timer
    
    backward()
    
def back_simple_full():           # from slide mode, zoom slide, manga to simple fullscreen
    print("back_simple_full")
    logging.info("back_simple_full")
    
    global slide_check
    global timer
    global zoom_slide_mode
    global auto_manga

    slide_check = False
    zoom_slide_mode = False
    auto_manga = False
    timer = default_timer                       # reset timer
    
    full_canvas.delete("all")                    # remove existing image
    
    pic_path = fullfilelist[fileindex]
    
    file_ext = os.path.splitext(pic_path)[1]      # separate file name and extension
        
    if file_ext in supported_img:     
        ShowIMG_Full(pic_path)                    # back to simple full screen
    
    elif file_ext in supported_ani:
        ShowANI_Full(pic_path)                    # back to simple full screen

def quit_full(event=0):                              # from full screen mode to window mode
    print("quit_full")
    logging.info("quit_full")    

    global full_mode
    global slide_check

    slide_check = False 
    full_mode = False
    
    popup.destroy()                                 # close full screen and controller
    popup2.destroy()
    
    filepath = str(folder_entry.get())              # refresh root window
    file_ext = os.path.splitext(filepath)[1]                  
    
    if file_ext in supported_img:
        ShowIMG(filepath)
    
    elif file_ext in supported_ani:
        ShowANI(filepath)                
    
def motion(event):                      # simple full screen or slide mode
    
    global popup
    global popup2
    
    y = event.y                          # mouse pointer location
    
    if y > full_h - 70:
        popup2.focus_set()                          # show controller
        
    if y < full_h - 70:
        popup.focus_set()                           # hide controller

# In[Show Image in Fullscreen and Slide mode]

def ShowIMG_Full(pic_path):                     # full screen mode
    print("ShowIMG_Full")
    logging.info("ShowIMG_Full")    

    global stop_ani     
    
    stop_ani = True
    error_label.config(text = "")
    
    if len(pic_path) > 255:
        exception_pathtoolong()
        
    try:
        img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
    
    except FileNotFoundError:
        exception_filenotfound()
        
    img_w, img_h = img.size
    popup.update()
    
    resize_scale = min(full_w/img_w,full_h/img_h)   # calculate the resize ratio, maintaining height-width scale
    #resize_scale = min(resize_scale,1)            # avoid bigger than original
    w,h=int(img_w*resize_scale*zoom_factor),int(img_h*resize_scale*zoom_factor)
    resize_img = img.resize((w,h))   
    full_canvas.image = ImageTk.PhotoImage(resize_img)
    full_canvas.create_image(full_w/2,full_h/2,anchor="center",image=full_canvas.image)
    
    if check_slide_mode() == True:
        
        while check_timer(False) >= 0 and check_slide_mode() == True: # check and control timer
            popup.update()
            time.sleep(1/timer_frame)                     # maintain frame
            
        if timer < 0 and check_slide_mode() == True:    # forward
            fullforward()

# In[Show Animation in Fullscreen, Slide mode and Zoom Slide mode]
def ShowANI_Full(pic_path):
    print("showANI_Full")
    logging.info("showANI_Full")
    
    global timer
    global stop_ani
    
    stop_ani = False                         # enable running animation
    
    error_label.config(text = "")
    full_canvas.delete("all")                 # remove existing image
    
    if check_slide_mode() == True:

        timer = gif_loop     # get timer
    
    gif_img2 = []                             # create list to store frames of gif
    
    if len(pic_path) > 255:
        exception_pathtoolong()
        
    try:
        gif_img2 = Image.open(pic_path)
    
    except FileNotFoundError:
        exception_filenotfound()
    
    popup.update()
    
    while check_stop_ani() == False and check_full_mode() == True:          # loop gif until stop
        timer_start2 = time.perf_counter()
        iter = ImageSequence.Iterator(gif_img2)   # create iterator to get frames
        i = 0
        
        img_w, img_h = iter[0].size
        resize_scale = min(full_w/img_w,full_h/img_h)   # calculate the resize ratio, maintaining height-width scale
        w,h=int(img_w*resize_scale),int(img_h*resize_scale)
        
        time_diff2 = time.perf_counter() - timer_start2
        print("time diff start: ", time_diff2)
        logging.info("time_diff_start: %s", time_diff2)
        
        for frame in iter:
            timer_start = time.perf_counter()
            
            if check_stop_ani() == False: # stop animation controlled by other def
                i = i + 1
                print(i)
                logging.info(i)
                
                gif_speed = check_gifspeed()
                resize_img = frame.resize((w,h)) 
                pic = ImageTk.PhotoImage(resize_img)
                full_canvas.create_image(full_w/2,full_h/2,anchor="center",image=pic)  # create image frame by frame

                popup.update()
                
                try:
                    gif_duration = gif_img2.info['duration']
                    print("duration: ", gif_duration)
                    
                except:
                    gif_duration = 40
                    
                time_diff = time.perf_counter() - timer_start
                print("time diff: ", time_diff)
                
                sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.009))
                print("sleep : ", sleep_time)
                
                time.sleep(sleep_time)
                
                if check_stop_ani() == False:
                    logging.info("duration: %s", gif_duration)
                    logging.info("time_diff: %s", time_diff)
                    logging.info("sleep : %s", sleep_time)

            else:
                break
            
        if check_slide_mode() == True:
            timer = check_timer(True)                 # control timer and countdown
            
            if timer <= 0 and check_slide_mode() == True:
                fullforward()                        # forward
    
    del iter

# In[Auto slide mode]

def start_slide():                        # slide mode or zoom slide mode
    print("start_slide")
    logging.info("start_slide")
    
    global slide_check
    global timer_pause
    global timer
    
    slide_button2.config(text = "Stop Slide", command=quit_slide)
    zoomslide_button2.config(state=tk.DISABLED)
    manga_button2.config(state=tk.DISABLED)
    
    slide_check = True
    timer_pause = False
    
    timer = default_timer
    
    filepath = fullfilelist[fileindex] 
    file_ext = os.path.splitext(filepath)[1]
    
    if zoom_slide_mode == False:                          # reset image in slide mode
        if file_ext in supported_img:                    
            ShowIMG_Full(filepath)
        
        else:
            ShowANI_Full(filepath)
    
def check_timer(ani):                                  # timer in slide mode or zoom slide mode 
    
    global timer    
    
    print("timer:", format(timer, ".3f"), end= " ")
    logging.info("timer: %s", timer)
    
    if ani == False:                                            # from ShowIMG_Full and ShowIMG_Fullzoomslide
        timer = timer - 1/timer_frame
        return timer
        
    else:                                                      # from ShowANI_Full
        timer = timer - 1                                      # timer = gif_loop
        return timer
    
def quit_slide():                                                 # slide mode and zoom slide mode
    print("quit_slide")
    logging.info("quit_slide")
    
    slide_button2.config(text = "Slide Mode", command=start_slide)
    zoomslide_button2.config(state = tk.NORMAL)
    manga_button2.config(state = tk.NORMAL)
    
    back_simple_full()
    
# In[Zoom Slide Mode]

def start_zoomslide():                           # zoom slide mode
    print("start_zoomslide")
    logging.info("start_zoomslide")
    
    global pause_button
    global updown_wheel
    global esc_quit_zoomslide
    global zoom_slide_mode
    global slide_check
    global timer
    
    popup.unbind("<Motion>",motion1)                     # control in zoom slide mode
    popup.unbind("<Button-1>", button1)
    popup.unbind("<Button-3>", button3)
    popup.unbind("<Escape>", button_esc)
    popup.unbind("<MouseWheel>", wheel)
    
    pause_button = popup.bind("<Button-1>", pause_auto)
    updown_wheel = popup.bind("<MouseWheel>", wheel_zoomslide)
    esc_quit_zoomslide = popup.bind("<Escape>", quit_zoomslide)
   
    zoom_slide_mode = True
    slide_check = True
    
    timer = default_timer
    
    popup.focus_set()
    
    full_canvas.delete("all") 
    
    start_slide()                                 # use common def as slide mode
    
    pic_path = fullfilelist[fileindex]
    file_ext = os.path.splitext(pic_path)[1]      # separate file name and extension
    
    if file_ext in supported_img:
        ShowIMG_FullZoomSlide(pic_path)           # zoom slide mode
    
    elif file_ext in supported_ani:
        ShowANI_Full(pic_path)                    # same as full mode for gif
        
def ShowIMG_FullZoomSlide(pic_path):          # zoom slide mode
    print("ShowIMG_FullZoomSlide")
    logging.info("ShowIMG_FullZoomSlide")
    
    global stop_ani
    global move_diff
    global img_w, img_h
    global zoom_pic

    stop_ani = True
    
    img = Image.open(pic_path)                  
    img_w, img_h = img.size
    
    popup.update()
    
    if full_w/img_w >= full_h/img_h:                    # if the image is narrower than screen
    
        resize_scale = full_w/img_w                    # calculate the resize ratio, maintaining height-width scale
        w,h=int(img_w*resize_scale),int(img_h*resize_scale)
        resize_img = img.resize((w,h))   
        full_canvas.image = ImageTk.PhotoImage(resize_img)
        zoom_pic = full_canvas.create_image(0,0,anchor="nw",image=full_canvas.image) # final pic
        
        h_diff = h - full_h                               # diff between final pic height and full screen height
        move_diff = (h_diff/timer/timer_frame) * -1      # move distance per frame

        while check_slide_mode() == True:
            
            slide_timer = float(check_timer(False))
             
            time.sleep(1/timer_frame)
            full_canvas.move(zoom_pic, 0, move_diff)     # move
            popup.update()
            
            while check_timer_pause() == True:            # pause
                popup.update()
            
            if slide_timer >= default_timer + 2 and check_slide_mode() == True:
                fullbackward()
            
            if slide_timer < 0 and check_slide_mode() == True:  # forward
                fullforward()
        
    if full_h/img_h > full_w/img_w:                     # if the image is wider than screen
        
        resize_scale = full_h/img_h                    # calculate the resize ratio, maintaining height-width scale
        w,h=int(img_w*resize_scale),int(img_h*resize_scale)
        resize_img = img.resize((w,h))   
        full_canvas.image = ImageTk.PhotoImage(resize_img)
        zoom_pic = full_canvas.create_image(0,0,anchor="nw",image=full_canvas.image) # final pic
        
        w_diff = w - full_w                            # diff between final pic width and full screen width
        move_diff = (w_diff/timer/timer_frame) * -1   # move distance per frame
       
        while check_slide_mode() == True:
            
            slide_timer = float(check_timer(False))
             
            time.sleep(1/timer_frame)
            full_canvas.move(zoom_pic, move_diff, 0)     # move
            popup.update()
            
            while check_timer_pause() == True:            # pause
                popup.update()
            
            if slide_timer >= default_timer + 2 and check_slide_mode() == True: # backward
                fullbackward()
            
            if slide_timer < 0 and check_slide_mode() == True:  # forward
                fullforward()
       
def quit_zoomslide(event):                          # zoom slide mode
    print("quit_zoomslide")    
    logging.info("quit_zoomslide")

    global motion1
    global button_esc
    global button1
    global button3
    global wheel

    popup.unbind("<Button-1>", pause_button)
    popup.unbind("<MouseWheel>", updown_wheel)
    popup.unbind("<Escape>", esc_quit_zoomslide)
    
    motion1 = popup.bind("<Motion>",motion)                          # control appearance controller 
    button_esc = popup.bind("<Escape>", quit_full)
    button1 = popup.bind("<Button-1>", fullforward)
    button3 = popup.bind("<Button-3>", fullbackward)
    wheel = popup.bind("<MouseWheel>",event_zoom)   
    
    quit_slide()
    
def pause_auto(event):                              # zoom slide mode
    print("pause_auto")
    logging.info("pause_auto")
    
    global timer_pause
    
    if timer_pause == False:
        timer_pause = True
    
    else:
        timer_pause = False
           
def wheel_zoomslide(event):                      # zoom slide mode
    print("wheel_zoomslide")
    logging.info("wheel_zoomslide")
    
    global timer
    global scroll_multiplier
    
    if event.delta > 1:                           # scroll up
        
        timer = timer + scroll_multiplier           # add timer
        
        if full_w/img_w >= full_h/img_h:
            full_canvas.move(zoom_pic, 0, move_diff * timer_frame * -scroll_multiplier)  # move up
        
        else:
            full_canvas.move(zoom_pic, move_diff * timer_frame * -scroll_multiplier, 0)
    
    else:                                          # scroll down
        timer = timer - scroll_multiplier                          # reduce timer
        
        if full_w/img_w >= full_h/img_h:
            full_canvas.move(zoom_pic, 0, move_diff * timer_frame * scroll_multiplier)  # move down
        
        else:
            full_canvas.move(zoom_pic, move_diff * timer_frame * scroll_multiplier, 0)

# In[Mange Mode]

def start_manga():
    print("start_manga")
    logging.info("start_manga")
    
    global stop_ani
    global mangalist, mangaindex
    global h1,h2,h3,h4
    global updown_wheel_manga
    global esc_quit_manga
    global auto_button
    global auto_manga, auto
    
    popup.unbind("<Motion>",motion1)                     
    popup.unbind("<Button-1>", button1)
    popup.unbind("<Button-3>", button3)
    popup.unbind("<Escape>", button_esc)
    popup.unbind("<MouseWheel>", wheel)
    
    auto_button = popup.bind("<Button-1>", auto_scrollmanga)
    updown_wheel_manga = popup.bind("<MouseWheel>", scroll_manga)
    esc_quit_manga = popup.bind("<Escape>", quit_manga)
    
    stop_ani = True
    auto_manga = False
    full_canvas.delete("all") 
    popup.focus_set()
    
    auto = 0
    
    mangalist= []                                   # create new list to avoid gif
    
    for file in fullfilelist:
        if os.path.splitext(file)[1] in supported_img:
            mangalist.append(file)
    
    filepath = str(folder_entry.get())
    
    try:
        mangaindex = mangalist.index(filepath) 
    
    except:
        mangaindex = 0                             # get index of list
    
    '''
       w1
       w2
       w3
    h1                                                     
      [manga_top] resized_h1 |  pre_mangaindex                 
    h2                                                   0             full_w
      [manga_mid] resized_h2 |  mangaindex                 [Full_canvas]
    h3                                               full_h
      [manga_bot] resized_h3 |  next_mangaindex
    h4  
    '''
    
    h2 = 0                                         
    show_manga_top()
    show_manga_mid()                                  
    h1 = 0 - resized_h1
    h3 = 0 + resized_h2
    show_manga_bot()
    h4 = 0 + resized_h2 + resized_h3

def show_manga_top():
    print("show_manga_top")
    logging.info("show_manga_top")
    
    global resized_h1
    global pre_mangaindex
    
    # 1st image
    pre_mangaindex = mangaindex - 1
    if pre_mangaindex < 0:                          # back to end
        pre_mangaindex = len(mangalist) - 1
        
    pic_path = mangalist[pre_mangaindex]
    
    if len(pic_path) > 255:
        exception_pathtoolong()
    
    try:
        img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
    
    except FileNotFoundError:
        exception_filenotfound()
                
    img_w, img_h = img.size
    
    resize_scale = full_w / img_w * manga_resize               # calculate the resize ratio, maintaining height-width scale
    resized_w1,resized_h1=int(img_w*resize_scale),int(img_h*resize_scale)
    resize_img = img.resize((resized_w1,resized_h1))   
    globals()['image_%s' % pre_mangaindex] = ImageTk.PhotoImage(resize_img) 
    w1 = int((1-manga_resize)/2*full_w)
    #dynamic variable to get manga_[mangaindex]
    globals()['manga_%s' % pre_mangaindex] = full_canvas.create_image(w1,h2,anchor="sw",image=globals()['image_%s' % pre_mangaindex])
    
    print("Add: ", ['manga_%s' % pre_mangaindex])
    print("image Height: ", resized_h1)
    logging.info("Add: %s", ['manga_%s' % pre_mangaindex])
    logging.info("image Height: %s", resized_h1)

def show_manga_mid():
    print("show_manga_mid")
    logging.info("show_manga_mid")
    
    global resized_h2
    
    # 2nd image
    pic_path = mangalist[mangaindex]
    
    if len(pic_path) > 255:
        exception_pathtoolong()
    
    try:
        img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
    
    except FileNotFoundError:
        exception_filenotfound()
                         
    img_w, img_h = img.size
    
    resize_scale = full_w / img_w * manga_resize               # calculate the resize ratio, maintaining height-width scale
    resized_w2,resized_h2=int(img_w*resize_scale),int(img_h*resize_scale)
    resize_img = img.resize((resized_w2,resized_h2))   
    globals()['image_%s' % mangaindex] = ImageTk.PhotoImage(resize_img)
    w2 = int((1-manga_resize)/2*full_w)
    globals()['manga_%s' % mangaindex] = full_canvas.create_image(w2,h2,anchor="nw",image=globals()['image_%s' % mangaindex])
    
    print("Add: ",  ['manga_%s' % mangaindex])
    print("image Height: ", resized_h2)
    logging.info("Add: %s", ['manga_%s' % mangaindex])
    logging.info("image Height: %s", resized_h2)

def show_manga_bot():
    print("show_manga_bot")
    logging.info("show_manga_bot")
    
    global resized_h3
    global next_mangaindex
    
    # 3rd image
    next_mangaindex = mangaindex + 1
    if next_mangaindex == len(mangalist):           # back to start
        next_mangaindex = 0
        
    pic_path = mangalist[next_mangaindex]
   
    if len(pic_path) > 255:
        exception_pathtoolong()
    
    try:
        img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
    
    except FileNotFoundError:
        exception_filenotfound()
               
    img_w, img_h = img.size
    
    resize_scale = full_w / img_w * manga_resize             # calculate the resize ratio, maintaining height-width scale
    resized_w3,resized_h3=int(img_w*resize_scale),int(img_h*resize_scale)
    resize_img = img.resize((resized_w3,resized_h3))   
    globals()['image_%s' % next_mangaindex] = ImageTk.PhotoImage(resize_img)
    w3 = int((1-manga_resize)/2*full_w)
    globals()['manga_%s' % next_mangaindex] = full_canvas.create_image(w3,h3,anchor="nw",image=globals()['image_%s' % next_mangaindex])
    
    print("Add: ",  ['manga_%s' % next_mangaindex])
    print("image Height: ", resized_h3)
    logging.info("Add: %s", ['manga_%s' % next_mangaindex])
    logging.info("image Height: %s", resized_h3)
 
def scroll_manga(event=None, auto=0):                       # manga mode
    print("scroll_manga")
    logging.info("scroll_manga")
    
    global h1,h2,h3,h4
    global pre_mangaindex, mangaindex, next_mangaindex
    
    if auto == 0:
        scroll_dis = auto_dis * scroll_multiplier
    
    else:
        scroll_dis = int(auto/auto_frame)
    
    try:
        
        if event.delta > 1:                      # manual scroll
            scroll = "up"
        
        else:
            scroll = "down"
    
    except:                                      # auto scroll
        scroll = "up"
            
    if scroll == "up":                           # scroll up, move up
        full_canvas.move(globals()['manga_%s' % pre_mangaindex], 0, scroll_dis * -1)
        full_canvas.move(globals()['manga_%s' % mangaindex], 0, scroll_dis * -1)     
        full_canvas.move(globals()['manga_%s' % next_mangaindex], 0, scroll_dis * -1)
        
        h1 = h1 - scroll_dis
        h2 = h2 - scroll_dis
        h3 = h3 - scroll_dis
        h4 = h4 - scroll_dis
 
    if scroll == "down":                         # scroll down, move down      
        full_canvas.move(globals()['manga_%s' % pre_mangaindex], 0, scroll_dis * 1)
        full_canvas.move(globals()['manga_%s' % mangaindex], 0, scroll_dis * 1)     
        full_canvas.move(globals()['manga_%s' % next_mangaindex], 0, scroll_dis * 1)
        
        h1 = h1 + scroll_dis
        h2 = h2 + scroll_dis
        h3 = h3 + scroll_dis
        h4 = h4 + scroll_dis
        
    print("Move: ", ['manga_%s' % pre_mangaindex], ",", ['manga_%s' % mangaindex], ",", ['manga_%s' % next_mangaindex])
    print(h1,",",h2,",", h3, "," ,h4)
    
    if h3 < 0:                             # scroll up, forward
        mangaindex = mangaindex + 1
        
        if mangaindex == len(mangalist):           # back to start
            mangaindex = 0
            
        h1 = h2
        h2 = h3
        h3 = h4
        
        full_canvas.delete(globals()['manga_%s' % pre_mangaindex])
        del globals()['manga_%s' % pre_mangaindex]               # del to release resource
        print("Remove: ",  ['manga_%s' % pre_mangaindex])
        logging.info("Remove: %s",  ['manga_%s' % pre_mangaindex])
        
        show_manga_bot()
        
        h4 = h3 + resized_h3
        pre_mangaindex = pre_mangaindex + 1
        
        if pre_mangaindex == len(mangalist):           # back to start
            pre_mangaindex = 0
    
    if h2 > full_h:                            # full_h = 865
        mangaindex = mangaindex - 1           # scroll down, backward
        
        if mangaindex < 0:                          # back to end
            mangaindex = len(mangalist) - 1
            
        h4 = h3
        h3 = h2
        h2 = h1
        
        full_canvas.delete(globals()['manga_%s' % next_mangaindex])
        del globals()['manga_%s' % next_mangaindex]              # del to release resource
        print("Remove: ",  ['manga_%s' % next_mangaindex])
        logging.info("Remove: %s",  ['manga_%s' % next_mangaindex])
        
        show_manga_top()
        
        h1 = h2 - resized_h1
        next_mangaindex = next_mangaindex - 1           # scroll down, backward
        
        if next_mangaindex < 0:                          # back to end
            next_mangaindex = len(mangalist) - 1

def auto_scrollmanga(event):                         # manga mode
    print("auto_manga")
    logging.info("auto_manga")
    
    global auto_manga
    
    if auto_manga == True:
        auto_manga = False
    
    else:
        auto_manga = True
        
    while check_auto_manga() == True:
        scroll_manga(None,auto_dis)
        popup.update()
        time.sleep(1/auto_frame)

def quit_manga(event):                       # manga mode
    print("quit_manga")
    logging.info("quit_manga")
    
    global motion1
    global button_esc
    global button1
    global button3
    global wheel
    
    popup.unbind("<Button-1>", auto_button)
    popup.unbind("<MouseWheel>", updown_wheel_manga)
    popup.unbind("<Escape>", esc_quit_manga)
    
    motion1 = popup.bind("<Motion>",motion)                          # control appearance controller 
    button_esc = popup.bind("<Escape>", quit_full)
    button1 = popup.bind("<Button-1>", fullforward)
    button3 = popup.bind("<Button-3>", fullbackward)
    wheel = popup.bind("<MouseWheel>",event_zoom) 
    
    del globals()['manga_%s' % pre_mangaindex]               # del to release resource
    del globals()['manga_%s' % mangaindex]                   # del to release resource
    del globals()['manga_%s' % next_mangaindex]              # del to release resource
    
    back_simple_full()

# In[Check variable status]

def check_stop_ani():                                 # check if animation is turned off
    
    if stop_ani == True:
        return True
    
    else:
        return False

def check_full_mode():                                 # check if it is fullscreen
    
    if full_mode == True:
        return True
    
    else:
        return False

def check_slide_mode():                                # check if slide mode is on

    if slide_check == True:
        return True
    
    else:
        return False

def check_timer_pause():                                 # check if it is paused in zoom-slide mode
    
    if timer_pause == True:
        time.sleep(0.1)
        return True
    
    else:
        return False

def check_auto_manga():                                # check if auto manga is on

    if auto_manga == True:
        return True
    
    else:
        return False

def check_gifspeed():
    
    return gif_speed

# In[Exception]

def exception_dirnotfound():
    
    error_label.config(text = "Directory not found")
    logging.warning("Directory not found")
    raise FileNotFoundError("Directory not found")

def exception_dirnosupportedfile():
    
    error_label.config(text = "No supported file in the directory")
    logging.warning("No supported file in the directory")
    raise FileNotFoundError("No supported file in the directory") 

def exception_dirnopermission():
    
    # including read image and write config
    error_label.config(text = "No read permission of the directory")
    logging.warning("No read permission of the directory")
    raise PermissionError("No read permission of the directory") 

def exception_dirtoolarge():
    
    error_label.config(text = "Timeout: 10 sec. Try limiting the number of directory searched")
    logging.warning("Timeout: 10 sec. Try limiting the number of directory searched")
    raise RuntimeWarning("Timeout: 10 seconds. Try limiting the number of directory searched") 

def exception_filenotfound():
    
    error_label.config(text = "No such file")
    logging.warning("No such file")    
    raise FileNotFoundError("No such file") 

def exception_pathtoolong():
    
    error_label.config(text = "file path can't exceed 255 characters")
    logging.warning("file path can't exceed 255 characters")  
    raise FileNotFoundError("file path can't exceed 255 characters") 

def exception_settingswrongvalue():
    
    setting_error.config(text = "Not saved: Value must be integer")
    logging.warning("Not saved: Value must be integer")  
    raise ValueError("Value must be integer") 
    
def exception_settingnopermission():
    
    # including read image and write config
    setting_error.config(text = "No write permission of the directory")
    logging.warning("No write permission of the directory")
    raise PermissionError("No write permission of the directory") 

def exception_unidentifiedimage():
    
    # supported format but invalid file
    # PIL.UnidentifiedImageError: cannot identify image file
    logging.warning("PIL.UnidentifiedImageError: cannot identify image file")
    pass   # can't handle module exception

# In[Initial]

logging_create()

GUI()

logging_shutdown()

# In[things to do]

r''' 
functionality (completed):

    
optimization:
faster open (use directory mode)
improve efficiency (remove unnecessary var, reorganize def, black?)
better GUI (try change color to black, orange, white)
change to class

bug fix:
can't launch py by double click
    
known bug can't be fixed:
[severity: medium] GIF distorted (neko para vol3 and 4) (note: can't support some gifs')
[severity: low ] some GIF 0.2s lag in the end of iter (Bishoujo Mangekyou) (note: maybe due to slow processing)
[severity: low] GIF can't be resized upon window resize
[severity: low] some GIF can't get duration (note: replaced by constant 40 in try except)

convert to exe:

https://ithelp.ithome.com.tw/articles/10231524

1) Open Windows PowerShell
2) Install Python (go to python website to install)
3) Install module including tkinter, Pillow, configparser, auto-py-to-exe, pyinstaller
4) open auto-py-to-exe

'''

