# -*- coding: utf-8 -*-
# author: SimonAlpaca
# project started on 25/8/2021, finished on 3/10/2021

import os
import sys
from PIL import Image, ImageTk, ImageSequence, ImageFile
import time
import configparser
import logging
import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk
from ctypes import windll

# In[Logging]

def logging_create():

    exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
    logging_path = os.path.join(exe_dir, "err_handling.log")
    logging.basicConfig(level = logging.DEBUG, filename = logging_path, filemode = "w")

def logging_exception(exc_type, exc_value, exc_traceback):

    print("Uncaught exception")
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
def logging_shutdown():
    
    logging.shutdown()
    
# In[GUI]

def window_create():
    print("window_create")
    logging.info("window_create")

    global window
    global pic_canvas
    global folder_entry
    global max_button
    global listbox_button
    global setting_button
    global error_label
    global full_w, full_h
    global offsetx, offsety
    global rotate_degree
    global is_rotated

    # Window
    style = Style(theme='darkly')                             # need manual modification of theme file
    style.configure("primary.TButton", font=("Helvetica", 11,"bold")) # letter button
    style.configure("second.TButton", font=("Helvetica", 19)) # unicode symbol button
    
    window = style.master                                         # create window by ttk

    window.overrideredirect(1)                                     
    full_w, full_h = window.winfo_screenwidth(), window.winfo_screenheight()  # get screen width and screen height
    window.geometry('500x580+300+150')                                 # window size  
    window.resizable(width=True,height=True)                   # disallow window resize
    window.title("SimonAlpaca Picture Viewer")                  # title
    window.withdraw()
    
    # Top Frame
    top_frame = ttk.Frame(window,style='Warning.TFrame')             # add frame first
    top_frame.pack(pady=1, side = tk.TOP, fill = "both")
    quit_button = ttk.Button(top_frame, text= "\u03A7", width=3, style='primary.Outline.TButton', command=quit)
    quit_button.pack(side =tk.RIGHT, padx = 10)
    
    max_button = ttk.Button(top_frame, text= "\u2587", width=3, style='primary.Outline.TButton', command = window_zoomed)
    max_button.pack(side =tk.RIGHT, padx = 0)
    
    rotate_degree = 0
    is_rotated = False
    
    anticlock_button = ttk.Button(top_frame, text= "\u2937", width=1, command = anticlockwise)
    anticlock_button.pack(side =tk.LEFT, padx = 10)
    
    clock_button = ttk.Button(top_frame, text= "\u2936", width=1, command = clockwise)
    clock_button.pack(side =tk.LEFT, padx = 5)
    
    window.protocol("WM_DELETE_WINDOW", quit)               # when close in taskbar
    
    # Program icon
    try:                                                   
        exe_dir = os.path.split(sys.argv[0])[0]            # sys.argv[0] is the exe path
        ico_path = os.path.join(exe_dir, "Alpaca_ico.ico")
        window.iconbitmap(ico_path)                     
    
    except:
        pass
    
    # Window Drag
    offsetx = 0
    offsety = 0
    top_frame.bind('<Button-1>', window_predrag)
    top_frame.bind('<B1-Motion>', window_drag)
    
    import_settings()                                          # import default settings or config
    
    window.geometry('%dx%d+%d+%d' %(int(window_width), int(window_height), int(window_x), int(window_y))) # re adjust window size
    
    # Canvas
    pic_canvas = tk.Canvas()
    pic_canvas.configure(background='black')
    pic_canvas.pack(side=tk.TOP, fill="both", expand=True, pady = 0, padx =10)
    pic_canvas.configure(scrollregion = pic_canvas.bbox("all"))
    
    # Bottom Button
    buttondown_frame = ttk.Frame(window, style='Warning.TFrame')             # add frame first
    buttondown_frame.pack(pady=5, side = tk.BOTTOM)
    
    check_button = ttk.Checkbutton(buttondown_frame, text="Include Subfolder               ", var=parent_check, style = "warning.Roundtoggle.Toolbutton")
    check_button.pack(padx = 0, side= tk.RIGHT) 
    
    go_button = ttk.Button(buttondown_frame, text= "GO", width=12, style='primary.TButton', command=go)
    go_button.pack(side=tk.RIGHT,padx=10)              # padx means gap of x-axis
    
    listbox_button = ttk.Button(buttondown_frame, text= "Hide List", width=8, style='primary.TButton', command=hide_listbox) # destory to quit
    listbox_button.pack(side=tk.LEFT,padx=10)
    
    create_listbox()
    
    setting_button = ttk.Button(buttondown_frame, text= "Settings", width=8, style='primary.TButton', command=setting_buttonclick) # destory to quit
    setting_button.pack(side=tk.LEFT,padx=10)
    
    # Error label
    error_frame = ttk.Frame(window, style='Warning.TFrame')               
    error_frame.pack(pady=0, fill="y", side = tk.BOTTOM)
    error_label = tk.Label(error_frame, text = "", fg = "red", font = ("Arial", 10))
    error_label.pack()
    
    # Path
    folder_frame = ttk.Frame(window, style='Warning.TFrame')           
    folder_frame.pack(pady=0, fill="y", side = tk.BOTTOM)               # pady means gap of y-axis, fill both means aligh to left and right
    folder_label = ttk.Label(folder_frame, text = "Folder Name : " ,style='fg.TLabel')
    folder_label.pack(side=tk.LEFT, padx = 5)
    reset_button = ttk.Button(folder_frame, text= "Reset", width=4.2, command=reset_entry, style='primary.Outline.TButton')
    reset_button.pack(side =tk.RIGHT, padx = 5)
    folder_entry = tk.Entry(folder_frame, width=120 , background='gray25')
    folder_entry.insert(1, default_path)
    folder_entry.pack(side=tk.LEFT)

    # Up Button
    buttonup_frame = ttk.Frame(window,style='inputbg.TFrame')
    buttonup_frame.pack(fill = "y", side = tk.BOTTOM, pady = 5)
    backward_button = ttk.Button(buttonup_frame, text= u"\u2B98", width=3, command=backward, style='second.TButton')
    backward_button.pack(side =tk.LEFT, padx = 20)
    full_button = ttk.Button(buttonup_frame, text= u"\u29C9", width=4, command=fullscreen, style='second.TButton')
    full_button.pack(side =tk.LEFT, padx = 20)
    forward_button = ttk.Button(buttonup_frame, text= u"\u2B9A", width=3, command=forward, style='second.TButton')
    forward_button.pack(side =tk.LEFT, padx = 20)
    
    # gripper for resizing
    grip=ttk.Sizegrip()
    grip.place(relx=1.0, rely=1.0, anchor="se")
    grip.lift(top_frame)
    grip.bind("<B1-Motion>", window_resize)
    
    window.after(100, start)    # run def"start" first

    window.after(1, set_appwindow)    # put window in taskbar
    
    window.mainloop()        # must add at the end to make it run
    
def window_zoomed():
    print("window_zoomed")
    logging.info("window_zoomed")
    
    max_button.config(text = "\u2583", command = window_normal)
    window.state("zoomed")
    
def window_normal():
    print("window_normal")
    logging.info("window_normal")
    
    max_button.config(text = "\u2587", command = window_zoomed)
    window.state("normal")

def window_predrag(event):
    print("drag_window")    
    logging.info("drag_window")
    
    global offsetx
    global offsety
    
    offsetx = event.x
    offsety = event.y
    
def window_drag(event):
    
    x = window.winfo_x() + event.x - offsetx
    y = window.winfo_y() + event.y - offsety

    window.geometry('+{x}+{y}'.format(x=x,y=y))

def reset_entry():
    
    folder_entry.delete(0,"end")

def set_appwindow():
    
    GWL_EXSTYLE=-20                                       # for showing program in taskbar
    WS_EX_APPWINDOW=0x00040000
    WS_EX_TOOLWINDOW=0x00000080
    
    hwnd = windll.user32.GetParent(window.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    
    # re-assert the new window style
    window.wm_withdraw()
    window.after(1, show_appwindow)

def show_appwindow():
    
    window.state("zoomed")                    # fix bug of "can't bring to back before dragging the window"
    window.state("normal")
    
    if window_state == "normal":
        window_normal()
    
    else:
        window_zoomed()
    
    window.wm_deiconify()
    window.attributes('-topmost', True)
    window.update()
    
    time.sleep(0.05)                          # perform better after sleep
    window.attributes('-topmost', False)      # force window to the front but not always

# In[Start]

def start():
    print("start")
    logging.info("start")
    
    global supported_img
    global supported_ani
    global check_width
    global check_height
    global gif_speed2
    
    gif_speed2 = 1
    
    # Supported format
    supported_img = [".jpg", ".jpeg", ".png", ".bmp", ".jfif", ".ico", ".webp"]
    supported_ani = [".gif"]
    
    supported_img = set(supported_img)      # create set
    supported_ani = set(supported_ani)
    
    window.bind("<Configure>",event_resize)           # trigger event, after loading GUI
    window.bind("<MouseWheel>",event_zoom)            # trigger zoom event
    window.bind("<Up>", gif_speedup)
    window.bind("<Down>", gif_speeddown)

    filepath = str(folder_entry.get())
    
    check_width = [window.winfo_width(), window.winfo_width()]
    check_height = [window.winfo_height(), window.winfo_height()]
    
    window.update()
    window.focus_set()
    
    if filepath != "":
        go()
            
# In[Go Button]

def go():
    print("go")
    logging.info("go")

    global fileindex
    global fullfilelist
    global is_full_mode
    global is_stop_ani
    global zoom_factor
    global origX, origY
    
    is_full_mode = False
    is_stop_ani = True
    zoom_factor = 1
    
    #timer_start = time.perf_counter()
    
    origX = pic_canvas.xview()[0]                # original canvas position for zoom and move
    origY = pic_canvas.yview()[0]
    
    pic_canvas.bind('<ButtonPress-1>', move_from)
    pic_canvas.bind('<B1-Motion>', move_to)
    
    listbox1.delete(0,"end")                         # clear listbox
    
    filepath = str(folder_entry.get())
    is_parent = parent_check.get()
    if not os.path.isdir(filepath):              # handle dir path
        filesplit = os.path.split(filepath)           # separate dir path and file name
    
    else:
        filesplit = [filepath, ""]
    
    fullfilelist = []
    filename = ""
    
    if filepath == "":
        exception_emptypath()
    
    if not os.path.exists(filepath):         # check whether the dir exists
        exception_dirnotfound()
        
    if not os.access(filepath, os.R_OK):     # check whether the dir has read permission
        exception_dirnopermission()
    
    if not is_parent:                      # exclude sub folder
        filelist = os.listdir(filesplit[0])  
            
        filelist.sort()
        for filename in filelist:
            
            fullpathname = os.path.join(filesplit[0],filename)
            file_ext = os.path.splitext(fullpathname)[1].lower()
            
            if file_ext in (supported_img|supported_ani):  #filter not support format
                fullfilelist.append(fullpathname)    # full path in list
            
            #else:
                #print("Not Supported : ", filename)
                #logging.info("Not Supported : %s", filename)
    
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
                file_ext = os.path.splitext(fullpathname)[1].lower()
                
                if file_ext in (supported_img|supported_ani):    #filter not support format
                    fullfilelist.append(fullpathname)
                
                #else:
                 #   if len(file_ext) > 0:
                  #      print("Not Supported : ", file)
                   #     logging.info("Not Supported : %s", file)
    
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
    
    file_ext = os.path.splitext(filepath)[1].lower()      # separate file name and extension
    
    folder_entry.delete(0,"end")
    folder_entry.insert(1, filepath)             # replace folder entry
    
    #time_diff = time.perf_counter() - timer_start
    
    #print(time_diff)
    
    if file_ext in supported_img:                 # show in window mode
        ShowIMG(filepath)
    
    elif file_ext in supported_ani:
        ShowANI(filepath)
    
# In[Quit Button]

def quit():
    print("quit")
    logging.info("quit")
    
    global is_stop_ani
    
    is_stop_ani = True
    
    try:
        setting_create()              # run and save settings
        setting_ok()                # settings toplevel destroyed
    
    except:
        print("Not saved when quit: Settings Error")
        logging.info("Not saved when quit: Settings Error")
    
    try:
        popup.destroy()
        popup2.destroy()
        
    except:
        pass
    
    settinglevel.destroy()
    listlevel.destroy()
    window.destroy()

# In[Forward Button]

def forward():                                  # all modes except manga mode
    print("forward")
    logging.info("forward")
   
    global fileindex
    global zoom_factor
    global is_stop_ani
    
    is_stop_ani = True                             # stop previous ani
    zoom_factor = 1                             # reset zoom
    cancel_move()
    
    fileindex = fileindex + 1                    # next file

    if fileindex == len(fullfilelist):           # back to start
        fileindex = 0

    nextpath = fullfilelist[fileindex]          # get path of next file
    
    folder_entry.delete(0,"end")
    folder_entry.insert(1, nextpath)             # replace folder entry
    file_ext = os.path.splitext(nextpath)[1].lower()
    if file_ext in supported_img:                # img
                                     
        if is_full_mode:
            
            if is_photoalbum_mode:
                ShowIMG_FullPhotoalbum(nextpath)  # Photo Album mode
            
            else:   
                ShowIMG_Full(nextpath)            # slide mode or simple fullscreen
        
        else:
            ShowIMG(nextpath)                    # window mode
            
    else:                                       # gif
        if is_full_mode:
            time.sleep(0.1)
            ShowANI_Full(nextpath)             # simple fullscreen, slide mode, Photo Album mode
        
        else:
            ShowANI(nextpath)
            
# In[Backward Button]

def backward():                               # all modes except manga mode
    print("backward")
    logging.info("backward")
    
    global fileindex
    global zoom_factor
    global is_stop_ani
    
    is_stop_ani = True                            # stop previous ani
    zoom_factor = 1                            # reset zoom
    cancel_move()
    
    fileindex = fileindex - 1                  # previous file
    if fileindex < 0:                          # back to end
        fileindex = len(fullfilelist) - 1
            
    filepath = fullfilelist[fileindex]         # get path of previous file
    
    folder_entry.delete(0,"end")
    folder_entry.insert(1, filepath)           # replace folder entry
    file_ext = os.path.splitext(filepath)[1].lower()
    if file_ext in supported_img:                 # img
                                                  
        if is_full_mode:
            
            if is_photoalbum_mode:
                ShowIMG_FullPhotoalbum(filepath)   # Photo Album mode
            
            else:   
                ShowIMG_Full(filepath)            # simple fullscreen or slide mode
        
        else:
            ShowIMG(filepath)                     # window mode 
            
    else:                                         # gif                                             
        if is_full_mode:                  
            ShowANI_Full(filepath)                # simple fullscreen, slide mode, Photo Album mode
        
        else:
            ShowANI(filepath)                     # window mode
            
# In[Listbox]

def create_listbox():
    print("create_listbox")    
    logging.info("create_listbox")
    
    global listlevel
    global listbox1
    global list_offsetx
    global list_offsety
    
    listlevel = tk.Toplevel(window)
    listlevel.resizable(False,False)
    listlevel.overrideredirect(1)
    listlevel.geometry('250x550+%d+%d' %(int(listbox_x), int(listbox_y)))    # re adjust list position
    
    listbox_scroll = ttk.Scrollbar(listlevel, orient='vertical', style="Vertical.TScrollbar") 
    listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    w, h = listlevel.winfo_screenwidth(), listlevel.winfo_screenheight()
    listbox1 = tk.Listbox(listlevel,width=w-80,height=h,highlightthickness=5, selectmode = tk.SINGLE, yscrollcommand = listbox_scroll.set)
    listbox1.configure(background='black')
    listbox1.pack(side=tk.LEFT)
    
    listbox_scroll.config(command = listbox1.yview)
    
    listbox1.bind("<Double-Button-1>", select_listbox)
    
    # Listbox Drag
    list_offsetx = 0
    list_offsety = 0
    listbox1.bind('<Button-1>', listbox_predrag)
    listbox1.bind('<B1-Motion>', listbox_drag)
    
    hide_listbox()
    
def listbox_predrag(event):
    print("drag_listbox")    
    logging.info("drag_listbox")
    
    global list_offsetx
    global list_offsety
    
    list_offsetx = event.x
    list_offsety = event.y
    
def listbox_drag(event):
    
    x = listlevel.winfo_x() + event.x - list_offsetx
    y = listlevel.winfo_y() + event.y - list_offsety

    listlevel.geometry('+{x}+{y}'.format(x=x,y=y))

def show_listbox():                          # in window and fullscreen mode
    print("show_listbox")    
    logging.info("show_listbox")
    
    try:    
        listbox_button2.config(text = "Hide", command=hide_listbox)
        popup.unbind("<Motion>",motion1)    # fullscreen mode 
        popup2.attributes('-topmost', True)
        
    except:
        pass
    
    listlevel.attributes('-topmost', True)
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
    file_ext = os.path.splitext(filepath)[1].lower()      # separate file name and extension
    
    if not is_full_mode:                      # window mode
        
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
        popup2.attributes('-topmost', False)
        
    except:
        pass
    
    listlevel.attributes('-topmost', False)
    
    listbox_button.config(text = "List", command=show_listbox)
    listlevel.withdraw()

# In[Settings]

def import_settings():
    print("import_settings") 
    logging.info("import_settings")
    
    global parent_check
    global original_check
    global is_original
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
    global listbox_x
    global listbox_y
    global setting_x
    global setting_y
    
    # Default Settings
    # window mode
    window_width = 500
    window_height = 580
    window_x = 300
    window_y = 150
    window_state = "normal"
    
    listbox_x = 50
    listbox_y = full_h - 700
    
    setting_x = full_w - 350 - 100
    setting_y = full_h - 500 - 150
    
    parent_check = tk.BooleanVar()
    #is_parent = False
    parent_check.set(False)                        # include subfolder
    
    original_check = tk.BooleanVar()
    is_original = False
    original_check.set(False)                        # original size
    
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
    auto_frame = 50                                # frame of auto manga
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
    
    #is_parent = str(getconfig("parent_check", is_parent)) # disable getting parent_check
    #parent_check.set(is_parent)
    is_original = str(getconfig("original_check", is_original))
    original_check.set(is_original)
    is_original = original_check.get()
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
    listbox_x = str(getconfig("listbox_x", listbox_x))
    listbox_y = str(getconfig("listbox_y", listbox_y))
    setting_x = str(getconfig("setting_x", setting_x))
    setting_y = str(getconfig("setting_y", setting_y))
    
def getconfig(column, var):

    try:
        return config.get("ImageViewer", str(column))
    
    except:
        return var

def setting_buttonclick():
    
    setting_create()
    setting_show()

def setting_create():                          # in window and fullscreen mode
    print("setting_create") 
    logging.info("setting_create")
    
    global settinglevel
    global setting_check2
    global setting_entry5
    global setting_entry6
    global setting_scroll
    global setting_gifspeed
    global setting_imagesize
    global setting_autospeed
    global setting_error
    global setting_offsetx
    global setting_offsety
    
    try:    
        settings_button2.config(text = "Hide", command=setting_hide)
        popup2.attributes('-topmost', True)
        popup.unbind("<Motion>",motion1)    # fullscreen mode 

    except:
        pass
    
    setting_button.config(text = "Hide", command=setting_hide)
    
    settinglevel = tk.Toplevel(window)
    settinglevel.resizable(False,False)
    settinglevel.overrideredirect(1)
    settinglevel.geometry('350x500+%d+%d' %(int(setting_x), int(setting_y)))    # re adjust list position
    
    setting_frame0 = tk.Frame(settinglevel)             
    setting_frame0.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
      
    setting_frame1 = tk.Frame(settinglevel, background='gray25')             
    setting_frame1.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame2 = tk.Frame(settinglevel)             
    setting_frame2.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame3 = tk.Frame(settinglevel)             
    setting_frame3.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame4 = tk.Frame(settinglevel, background='gray25')             
    setting_frame4.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame5 = tk.Frame(settinglevel)             
    setting_frame5.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame6 = tk.Frame(settinglevel)             
    setting_frame6.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame7 = tk.Frame(settinglevel, background='gray25')             
    setting_frame7.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame8 = tk.Frame(settinglevel)             
    setting_frame8.pack(pady=0, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame9 = tk.Frame(settinglevel, background='gray25')             
    setting_frame9.pack(pady=10, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame10 = tk.Frame(settinglevel)             
    setting_frame10.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame11 = tk.Frame(settinglevel)             
    setting_frame11.pack(pady=5, side = tk.TOP, fill=tk.BOTH)
    
    setting_frame13 = tk.Frame(settinglevel)             
    setting_frame13.pack(pady=5, side = tk.BOTTOM)
    
    setting_frame12 = tk.Frame(settinglevel)             
    setting_frame12.pack(pady=5, side = tk.BOTTOM)
    
    setting_label0 = ttk.Label(setting_frame0, text = "" , style='fg.TLabel') # to enable frame0
    setting_label0.pack(pady=0, side= tk.LEFT)
    
    setting_label1 = ttk.Label(setting_frame1, text = "  General : " , style='fg.TLabel' , background='gray25')
    setting_label1.pack(pady=0, side= tk.LEFT)
    
    setting_label2 = ttk.Label(setting_frame2, text = "      Original Size : " , style='fg.TLabel')
    setting_label2.pack(pady=0, side= tk.LEFT)
    
    setting_label3 = ttk.Label(setting_frame3, text = "      GIF Speed : " , style='fg.TLabel')
    setting_label3.pack(pady=0, side= tk.LEFT)
    
    setting_label4 = ttk.Label(setting_frame4, text = "  Slide mode / Photo Album mode : " ,style='fg.TLabel', background='gray25')
    setting_label4.pack(pady=0, side= tk.LEFT)
    
    setting_label5 = ttk.Label(setting_frame5, text = "      Image Timer (seconds): " , style='fg.TLabel')
    setting_label5.pack(pady=0, side= tk.LEFT)
    
    setting_label6 = ttk.Label(setting_frame6, text = "      GIF Loop (times): " , style='fg.TLabel')
    setting_label6.pack(pady=0, side= tk.LEFT)
    
    setting_label7 = ttk.Label(setting_frame7, text = "  Photo Album mode / Manga mode : " ,style='fg.TLabel', background='gray25')
    setting_label7.pack(pady=0, side= tk.LEFT)
    
    setting_label8 = ttk.Label(setting_frame8, text = "      Scroll : ", style='fg.TLabel' )
    setting_label8.pack(pady=0, side= tk.LEFT)
    
    setting_label9 = ttk.Label(setting_frame9, text = "  Manga mode : " ,style='fg.TLabel', background='gray25')
    setting_label9.pack(pady=0, side= tk.LEFT)
    
    setting_label10 = ttk.Label(setting_frame10, text = "      Image Size : " , style='fg.TLabel')
    setting_label10.pack(pady=0, side= tk.LEFT)
    
    setting_label11 = ttk.Label(setting_frame11, text = "      Auto Speed : ", style='fg.TLabel' )
    setting_label11.pack(pady=0, side= tk.LEFT)
    
    setting_check2 = ttk.Checkbutton(setting_frame2, text="", var=original_check, style = "warning.Roundtoggle.Toolbutton")
    setting_check2.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_gifspeed = tk.StringVar()
    setting_gifspeed.set(setting_gifspeedstr)
    setting_scroll3 = tk.OptionMenu(setting_frame3, setting_gifspeed, "Very Fast", "Fast", "Normal", "Slow", "Very Slow")
    setting_scroll3["highlightthickness"] = 0                  # remove the option boundary
    setting_scroll3.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_entry5 = tk.Entry(setting_frame5, width=5, background='gray25')
    setting_entry5.insert(1, default_timer)
    setting_entry5.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_entry6 = tk.Entry(setting_frame6, width=5, background='gray25')
    setting_entry6.insert(1, gif_loop)
    setting_entry6.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_scroll = tk.StringVar()
    setting_scroll.set(setting_scrollstr)
    setting_scroll8 = tk.OptionMenu(setting_frame8, setting_scroll, "Fast", "Normal", "Slow")
    setting_scroll8["highlightthickness"] = 0
    setting_scroll8.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_imagesize = tk.StringVar()
    setting_imagesize.set(setting_imagesizestr)
    setting_scroll10 = tk.OptionMenu(setting_frame10, setting_imagesize, "Normal", "Large", "Fullscreen")
    setting_scroll10["highlightthickness"] = 0
    setting_scroll10.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_autospeed = tk.StringVar()
    setting_autospeed.set(setting_autospeedstr)
    setting_scroll11 = tk.OptionMenu(setting_frame11, setting_autospeed, "Fast", "Normal", "Slow")
    setting_scroll11["highlightthickness"] = 0
    setting_scroll11.pack(pady=0, padx = 10, side= tk.RIGHT)
    
    setting_error = tk.Label(setting_frame12, text = "", fg = "red", font = ("Arial", 10))
    setting_error.pack()
    
    setting_button_save = tk.Button(setting_frame13, text = "Save and Close", command=setting_ok,width=20)
    setting_button_save.pack(side =tk.LEFT, padx = 20)
    
    setting_button_quit = tk.Button(setting_frame13, text = "Cancel", command=setting_hide,width=20)
    setting_button_quit.pack(side =tk.RIGHT, padx = 20)
    
    # Setting Drag
    setting_offsetx = 0
    setting_offsety = 0
    setting_frame0.bind('<Button-1>', setting_predrag)
    setting_frame0.bind('<B1-Motion>', setting_drag)

    settinglevel.withdraw()
    settinglevel.update()
    
def setting_show():
    print("setting_show")
    logging.info("setting_show")
    
    settinglevel.deiconify()
    settinglevel.attributes('-topmost', True)
    settinglevel.update()         # update for the position

def setting_predrag(event):
    print("drag_setting")    
    logging.info("drag_setting")
    
    global setting_offsetx
    global setting_offsety
    
    setting_offsetx = event.x
    setting_offsety = event.y
    
def setting_drag(event):
    
    x = settinglevel.winfo_x() + event.x - setting_offsetx
    y = settinglevel.winfo_y() + event.y - setting_offsety

    settinglevel.geometry('+{x}+{y}'.format(x=x,y=y))

def setting_ok():
    print("setting_ok")
    logging.info("setting_ok")
    
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
    global listbox_x
    global listbox_y
    global setting_x
    global setting_y
    global is_original
    
    setting_error.config(text = "")
    
    # window mode
    is_parent = parent_check.get()
    is_original = original_check.get()
        
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
        auto_dis = 240
    
    elif setting_autospeedstr == "Normal": 
        auto_dis = 180    
    
    elif setting_autospeedstr == "Slow": 
        auto_dis = 120
    
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    window_x = window.winfo_x()
    window_y = window.winfo_y()
    
    listbox_x = listlevel.winfo_x()
    listbox_y = listlevel.winfo_y()
    
    #settinglevel.deiconify()
    #settinglevel.update()
    
    setting_x = settinglevel.winfo_x()
    setting_y = settinglevel.winfo_y()

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
        config.set("ImageViewer", "parent_check", str(is_parent))
        config.set("ImageViewer", "original_check", str(is_original))
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
        config.set("ImageViewer", "listbox_x", str(listbox_x))
        config.set("ImageViewer", "listbox_y", str(listbox_y))
        config.set("ImageViewer", "setting_x", str(setting_x))
        config.set("ImageViewer", "setting_y", str(setting_y))
        
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
    setting_hide()

def setting_hide():                            # in windw and fullscreen mode
    print("setting_hide")
    logging.info("setting_hide")
    
    global motion1
    global button1
    global button3
    
    try:
        settings_button2.config(text = "Settings", command=setting_buttonclick)
        motion1 = popup.bind("<Motion>",motion)
        popup2.attributes('-topmost', False)
        
    except:
        pass
    
    settinglevel.attributes('-topmost', False)
    setting_button.config(text = "Settings", command=setting_buttonclick)
    settinglevel.withdraw()
    
# In[Show Image]

def ShowIMG(pic_path):                         # window mode
    print("ShowIMG")    
    logging.info("ShowIMG")

    global is_stop_ani

    is_stop_ani = True
    
    error_label.config(text = "")
    window.update()                                 # update pic_w, pic_h for fullscreen resize 
    pic_canvas.delete("all")                        
  
    if len(pic_path) > 255:
        exception_pathtoolong()
    
    try:
        img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
    
    except FileNotFoundError:
        exception_filenotfound()
    
    if is_rotated:                          # skip rotate if haven't clicked rotate
        img = img.rotate(rotate_degree, expand = True)
    
    img_w, img_h = img.size
    
    try:
        pic_w,pic_h = pic_canvas.winfo_width(),pic_canvas.winfo_height()  # get canvas width and height

    except:
        pass                                          # exception when resize with 0 canvas

    if pic_w > 1 and pic_h > 1:

        if is_original:
            resize_scale = 1

        else:
            resize_scale = min(pic_w/img_w,pic_h/img_h)   # calculate the resize ratio, maintaining height-width scale
            resize_scale = min(resize_scale,1)            # avoid bigger than original

        w,h=int(img_w*resize_scale*zoom_factor),int(img_h*resize_scale*zoom_factor)

        try:
            resize_img = img.resize((w,h))   
        
        except OSError:                              # fix OSError: image file is truncated
            print("OSError: image file is truncated")
            logging.info("OSError: image file is truncated")               
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            resize_img = img.resize((w,h))
        
        pic_canvas.image = ImageTk.PhotoImage(resize_img)
        pic_canvas.create_image(pic_w/2,pic_h/2,anchor="center",image=pic_canvas.image)
        
        window.focus_set()
        
        del img
        del resize_img
        
def anticlockwise():
    print("anticlockwise")    
    logging.info("anticlockwise")
    
    global rotate_degree
    global is_rotated
    
    is_rotated = True                             # enable rotate check
    
    rotate_degree = (rotate_degree + 90) % 360                  # anti-clockwise
    
    filepath = fullfilelist[fileindex]
    
    file_ext = os.path.splitext(filepath)[1].lower()      
    
    if file_ext in supported_img:                 
        ShowIMG(filepath)
    
def clockwise():
    print("clockwise")    
    logging.info("clockwise")
    
    global rotate_degree
    global is_rotated
    
    is_rotated = True                             # enable rotate check
    
    rotate_degree = (rotate_degree - 90) % 360                  # clockwise
    
    filepath = fullfilelist[fileindex]
    
    file_ext = os.path.splitext(filepath)[1].lower()      
    
    if file_ext in supported_img:                 
        ShowIMG(filepath)

# Show Image in Fullscreen and Slide mode

def ShowIMG_Full(pic_path):                     # full screen mode
    print("ShowIMG_Full")
    logging.info("ShowIMG_Full")    

    global is_stop_ani     
    
    is_stop_ani = True
    error_label.config(text = "")
    
    if len(pic_path) > 255:
        exception_pathtoolong()
        
    try:
        img = Image.open(pic_path)                  # necessary steps: Image.open, ImageTk.PhotoImage,canvas.create_image
    
    except FileNotFoundError:
        exception_filenotfound()
        
    img_w, img_h = img.size
    
    if is_original:
        resize_scale = 1
    
    else:
        resize_scale = min(full_w/img_w,full_h/img_h)   # calculate the resize ratio, maintaining height-width scale
        
    #resize_scale = min(resize_scale,1)            # avoid bigger than original
    w,h=int(img_w*resize_scale*zoom_factor),int(img_h*resize_scale*zoom_factor)
    
    try:
        resize_img = img.resize((w,h))   
    
    except OSError:                                # fix OSError: image file is truncated
        print("OSError: image file is truncated")
        logging.info("OSError: image file is truncated")   
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        resize_img = img.resize((w,h))  
        
    full_canvas.image = ImageTk.PhotoImage(resize_img)
    full_canvas.create_image(full_w/2,full_h/2,anchor="center",image=full_canvas.image)
    
    img.close()
    resize_img.close()
    del img
    del resize_img

    if check_slide_mode():
        countdown_timer()

# Show Image in Photo Album Mode

def ShowIMG_FullPhotoalbum(pic_path):          # Photo Album mode
    print("ShowIMG_FullPhotoalbum")
    logging.info("ShowIMG_FullPhotoalbum")
    
    global is_stop_ani
    global move_diff
    global img_w, img_h
    global zoom_pic

    is_stop_ani = True
    
    img = Image.open(pic_path)                  
    img_w, img_h = img.size
    
    if full_w/img_w >= full_h/img_h:                    # if the image is narrower than screen
    
        resize_scale = full_w/img_w                    # calculate the resize ratio, maintaining height-width scale
        w,h=int(img_w*resize_scale),int(img_h*resize_scale)

        try:
            resize_img = img.resize((w,h))   
        
        except OSError:                               # fix OSError: image file is truncated
            print("OSError: image file is truncated")
            logging.info("OSError: image file is truncated")      
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            resize_img = img.resize((w,h)) 
            
        full_canvas.image = ImageTk.PhotoImage(resize_img)
        zoom_pic = full_canvas.create_image(0,0,anchor="nw",image=full_canvas.image) # final pic
        
        del img
        del resize_img
        
        h_diff = h - full_h                               # diff between final pic height and full screen height
        move_diff = (h_diff/timer/timer_frame) * -1      # move distance per frame

        while check_slide_mode():
            
            slide_timer = float(check_timer(False))
             
            time.sleep(1/timer_frame)
            full_canvas.move(zoom_pic, 0, move_diff)     # move
            popup.update()
            
            while check_timer_pause():            # pause
                popup.update()
            
            if slide_timer >= default_timer + 2 and check_slide_mode():
                fullbackward()
            
            if slide_timer < 0 and check_slide_mode():  # forward
                fullforward()
        
    if full_h/img_h > full_w/img_w:                     # if the image is wider than screen
        
        resize_scale = full_h/img_h                    # calculate the resize ratio, maintaining height-width scale
        w,h=int(img_w*resize_scale),int(img_h*resize_scale)
        resize_img = img.resize((w,h))   
        full_canvas.image = ImageTk.PhotoImage(resize_img)
        zoom_pic = full_canvas.create_image(0,0,anchor="nw",image=full_canvas.image) # final pic
        
        del img
        del resize_img
        
        w_diff = w - full_w                            # diff between final pic width and full screen width
        move_diff = (w_diff/timer/timer_frame) * -1   # move distance per frame
       
        while check_slide_mode():
            
            slide_timer = float(check_timer(False))
             
            time.sleep(1/timer_frame)
            full_canvas.move(zoom_pic, move_diff, 0)     # move
            popup.update()
            
            while check_timer_pause():            # pause
                popup.update()
            
            if slide_timer >= default_timer + 2 and check_slide_mode(): # backward
                fullbackward()
            
            if slide_timer < 0 and check_slide_mode():  # forward
                fullforward()
                
# In[Show Animation]

def ShowANI(pic_path):                       # window mode
    print("ShowANI")
    logging.info("ShowANI")
    
    global is_stop_ani
    global gif_speed2

    is_stop_ani = False                         # enable running animation
    gif_speed2 = 1
    
    pic_canvas.delete("all")                 # remove existing image
    gif_img = []                             # create list to store frames of gif

    
    error_label.config(text = "")
    
    if len(pic_path) > 255:
        exception_pathtoolong()
        
    try:
        gif_img = Image.open(pic_path)
    
    except FileNotFoundError:
        exception_filenotfound()
    
    iter = ImageSequence.Iterator(gif_img)
    iter_length = len(list(iter))                  # get number of frame of iter
    print(iter_length)
    del iter
    
    window.focus_set()
    
    pic_w,pic_h=pic_canvas.winfo_width(),pic_canvas.winfo_height()

    while not check_stop_ani() and not check_full_mode():          # loop gif until stop
        
        #logging.info("time_check3: %s", time.perf_counter())
        #timer_start2 = time.perf_counter()
        iter = ImageSequence.Iterator(gif_img)   # create iterator to get frames
        i = 0
        
        if pic_w > 1 and pic_h > 1:    
            img_w, img_h = iter[0].size
            
            if is_original:
                resize_scale = 1

            else:
                resize_scale = min(pic_w/img_w,pic_h/img_h)   # calculate the resize ratio, maintaining height-width scale
            
            w,h=int(img_w*resize_scale),int(img_h*resize_scale)
            
            #time_diff2 = time.perf_counter() - timer_start2
            #print("time diff start: ", time_diff2)
            #logging.info("time_diff_start: %s", time_diff2)
            
            for frame in iter:
                timer_start = time.perf_counter()
                
                if not check_stop_ani(): # stop animation controlled by other def
                    i = i + 1
                    #print(i)
                    #logging.info(i)
                    
                    gif_speed = check_gifspeed()
                    resize_img = frame.resize((w,h)) 
                    pic = ImageTk.PhotoImage(resize_img)
                    pic_canvas.create_image(pic_w/2,pic_h/2,anchor="center",image=pic)  # create image frame by frame
                    
                    window.update()
                    
                    try:
                        gif_duration = gif_img.info['duration']
                        #print("duration: ", gif_duration)
                            
                    except:
                        gif_duration = 40     # set to 40 if can't find duration
                    
                    if i != iter_length:    # skip sleep for last frame to reduce gif lag issue in exe
                        
                        time_diff = time.perf_counter() - timer_start
                        #print("time diff: ", time_diff)
                           
                        sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.008))
                        #print("sleep : ", sleep_time)
                    
                        time.sleep(sleep_time)
                    
                    #else:
                        #print("sleep : skipped for last frame")
                        
                    #logging.info("time_check1: %s", time.perf_counter())
                    '''
                    if not check_stop_ani():
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
                
    del iter
    del gif_img
    del pic
    del resize_img
    
# Show Animation in Fullscreen, Slide mode and Photo Album mode

def ShowANI_Full(pic_path):
    print("showANI_Full")
    logging.info("showANI_Full")
    
    global timer
    global is_stop_ani
    global is_skip_ani
    global gif_speed2
    
    is_stop_ani = False                         # enable running animation
    is_skip_ani = False
    gif_speed2 = 1
    
    error_label.config(text = "")
    full_canvas.delete("all")                 # remove existing image
    
    if check_slide_mode():

        timer = gif_loop     # get timer
    
    gif_img2 = []                             # create list to store frames of gif
    
    if len(pic_path) > 255:
        exception_pathtoolong()
        
    try:
        gif_img2 = Image.open(pic_path)
    
    except FileNotFoundError:
        exception_filenotfound()
    
    iter = ImageSequence.Iterator(gif_img2)
    iter_length = len(list(iter))               # get number of frame of iter
    print(iter_length)
    del iter
    
    while not check_stop_ani() and check_full_mode():          # loop gif until stop
        #timer_start2 = time.perf_counter()
        iter = ImageSequence.Iterator(gif_img2)   # create iterator to get frames
        i = 0
        
        img_w, img_h = iter[0].size
        
        if is_original:
            resize_scale = 1

        else:
            resize_scale = min(full_w/img_w,full_h/img_h)   # calculate the resize ratio, maintaining height-width scale
        
        w,h = int(img_w*resize_scale), int(img_h*resize_scale)
        
        #time_diff2 = time.perf_counter() - timer_start2
        #print("time diff start: ", time_diff2)
        #logging.info("time_diff_start: %s", time_diff2)
        
        for frame in iter:
            timer_start = time.perf_counter()
            
            if not check_stop_ani(): # stop animation controlled by other def
                i = i + 1
                #print(i)
                #logging.info(i)
                
                if check_skip_ani():                         # skip ani in slide mode
                    timer = check_timer(True)                 # control timer and countdown
            
                    if timer <= 0 and check_slide_mode():
                        fullforward()                        # forward
                    
                    if timer > default_timer and check_slide_mode():
                        fullbackward()                        # forward
                
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
                
                if i != iter_length:    # skip sleep for last frame to reduce gif lag issue in exe
                    time_diff = time.perf_counter() - timer_start
                    #print("time diff: ", time_diff)
                    
                    sleep_time = max(0.001, gif_duration/1000 * gif_speed - (time_diff + 0.008))
                    #print("sleep : ", sleep_time)
                    
                    time.sleep(sleep_time)
                
                #else:
                    #print("sleep : skipped for last frame")
                '''    
                if not check_stop_ani():
                    logging.info("duration: %s", gif_duration)
                    
                    if i != iter_length:
                        logging.info("time_diff: %s", time_diff)
                        logging.info("sleep : %s", sleep_time)
                    
                    else: 
                        logging.info("sleep : skipped for last frame")
                        '''
            else:
                break
            
        if check_slide_mode():
            timer = check_timer(True)                 # control timer and countdown

            if timer <= 0 and check_slide_mode():
                fullforward()                        # forward
            
            if timer > gif_loop and check_slide_mode():
                fullbackward()                        # backward
    
    del iter
    del gif_img2
    del pic
    del resize_img

def gif_speedup(event):

    global gif_speed2
    
    gif_speed2 = max(0.3, gif_speed2 - 0.15)
    print("Gif Speed Up: ", gif_speed2)
    logging.info("Gif Speed Up: ", gif_speed2)

def gif_speeddown(event):

    global gif_speed2
    
    gif_speed2 = min(1.7, gif_speed2 + 0.15)
    print("Gif Speed Down: ", gif_speed2)
    logging.info("Gif Speed Down: ", gif_speed2)

# In[When Resize]

def window_resize(e):
    
   x1 = window.winfo_pointerx()
   y1 = window.winfo_pointery()
   x0 = window.winfo_rootx()
   y0 = window.winfo_rooty()
   
   window.geometry("%sx%s" % ((x1-x0),(y1-y0))) # for resizing the window

def event_resize(event=None):          # window mode
    
    global zoom_factor
    
    listbox1.focus_set()
    zoom_factor = 1                    # reset zoom
    
    '''
    print("e_w: ", event.width)
    print("e_h: ", event.height)
    print("w: ", check_width)
    print("h: ", check_height)
    '''
    
    if event.width == window.winfo_width() and event.height == window.winfo_height(): # trigger
        check_width[0] = check_width[1]
        check_height[0] = check_height[1]
        check_width[1] = event.width
        check_height[1] = event.height
        
        if check_width[0] != check_width[1] or check_height[0] != check_height[1]: # 2nd trigger
            print("event_resize")
            logging.info("event_resize")

            filepath = str(folder_entry.get())
            file_ext = os.path.splitext(filepath)[1].lower()              # separate file name and extension
            
            if file_ext in supported_img:
                ShowIMG(filepath)
            
            #elif file_ext in supported_ani:
             #   ShowANI(filepath)                # can't resize ani
         
# In[When Zoom]

def event_zoom(event):                  # window mode or full screen mode         
    print("event_zoom")
    logging.info("event_zoom")
    
    global zoom_factor
    #global pic_move_from, pic_move_to
    
    x = pic_canvas.canvasx(event.x)
    y = pic_canvas.canvasy(event.y)
    
    if event.delta > 1:                           # scroll up
        zoom_factor = zoom_factor + 0.2
    
    else:                                         # scroll down
        zoom_factor = max(zoom_factor - 0.2, 1)
    
    filepath = str(folder_entry.get())
    file_ext = os.path.splitext(filepath)[1].lower()
    
    if is_full_mode:                            
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
        
        ''' allow move pic only when zoom
        if zoom_factor > 1:
            pic_move_from = pic_canvas.bind('<ButtonPress-1>', move_from)
            pic_move_to = pic_canvas.bind('<B1-Motion>',     move_to)
        
        if zoom_factor == 1:                          # reset zoom
            cancel_move()
        '''
        
def cancel_move():
    
    ''' cancel move pic when no zoom
    try:
        pic_canvas.unbind('<ButtonPress-1>', pic_move_from)
        pic_canvas.unbind('<B1-Motion>', pic_move_to)
    
    except:
        pass
        '''
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
    global is_slide_check
    global is_full_mode
    global is_stop_ani
    global motion1
    global button1
    global button3
    global button_esc
    global wheel
    global is_photoalbum_mode
    global slide_button2
    global photoalbum_button2
    global listbox_button2
    global manga_button2
    global settings_button2
    
    is_slide_check = False
    is_full_mode = True
    is_photoalbum_mode = False
    is_stop_ani = True
    
    # GUI of Fullscreen
    popup = tk.Toplevel(window, bd=0)
    popup.resizable(False,False)
    popup.overrideredirect(1)
    
    popup.geometry("%dx%d+0+0" % (full_w, full_h))
    
    button_esc = popup.bind("<Escape>", quit_full)
    button1 = popup.bind("<Button-1>", fullforward)
    button3 = popup.bind("<Button-3>", fullbackward)
    wheel = popup.bind("<MouseWheel>",event_zoom)            # trigger zoom event
    popup.bind("<Up>", gif_speedup)
    popup.bind("<Down>", gif_speeddown)

    full_canvas = tk.Canvas(popup,width=full_w,height=full_h,highlightthickness=0)
    full_canvas.pack()
    full_canvas.configure(background='black')
    full_canvas.configure(scrollregion = full_canvas.bbox("all"))
    
    # Controller in fullscreen
    popup2 = tk.Toplevel(popup, bd=0)
    popup2.resizable(False,False)
    popup2.overrideredirect(1)
    popup2.geometry("800x50+%d+%d" % (full_w/2-800/2, full_h-64))
    
    listbox_button2 = ttk.Button(popup2, text = "List", style='primary.TButton', command=show_listbox, width=8)
    listbox_button2.pack(side =tk.LEFT, padx = 5)
    
    settings_button2 = ttk.Button(popup2, text = "Settings", style='primary.TButton', command=setting_buttonclick, width=8)
    settings_button2.pack(side=tk.LEFT,padx= 23)
    
    backward_button2 = ttk.Button(popup2, text= u"\u2B98", width=3, command=fullbackward, style='primary.TButton')
    backward_button2.pack(side =tk.LEFT, padx = 1)
    
    forward_button2 = ttk.Button(popup2, text= u"\u2B9A", width=3, command=fullforward, style='primary.TButton')
    forward_button2.pack(side =tk.LEFT, padx = 5)
    
    quit_button2 = ttk.Button(popup2, text= "\u03A7", width=3, style='primary.TButton', command=quit_full)
    quit_button2.pack(side =tk.RIGHT, padx = 5)
    
    manga_button2 = ttk.Button(popup2, text= "Manga Mode", width=12, command=start_manga, style='primary.TButton')
    manga_button2.pack(side =tk.RIGHT, padx = 5)
    
    photoalbum_button2 = ttk.Button(popup2, text= "Photo Album", width=12, command=start_photoalbum, style='primary.TButton')
    photoalbum_button2.pack(side =tk.RIGHT, padx = 5)
    
    slide_button2 = ttk.Button(popup2, text= "Slide Mode", width=12, command=start_slide, style='primary.TButton')
    slide_button2.pack(side =tk.RIGHT, padx = 10)
    
    motion1 = popup.bind("<Motion>",motion)                          # control appearance controller
    
    window.attributes('-topmost', False)
    popup.focus_set()    
    
    try:
        setting_hide()
    
    except:
        pass
    
    hide_listbox()
    
    if len(fullfilelist) == 0:
        exception_emptypath()
    
    filepath = fullfilelist[fileindex] 
    file_ext = os.path.splitext(filepath)[1].lower()
    
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
    
def back_simple_full():           # from slide mode, Photo Album, manga to simple fullscreen
    print("back_simple_full")
    logging.info("back_simple_full")
    
    global is_slide_check
    global timer
    global is_photoalbum_mode
    global is_auto_manga

    is_slide_check = False
    is_photoalbum_mode = False
    is_auto_manga = False
    timer = default_timer                       # reset timer
    
    full_canvas.delete("all")                    # remove existing image
    
    pic_path = fullfilelist[fileindex]
    
    file_ext = os.path.splitext(pic_path)[1].lower()      # separate file name and extension
        
    if file_ext in supported_img:     
        ShowIMG_Full(pic_path)                    # back to simple full screen
    
    elif file_ext in supported_ani:
        ShowANI_Full(pic_path)                    # back to simple full screen

def quit_full(event=0):                              # from full screen mode to window mode
    print("quit_full")
    logging.info("quit_full")    

    global is_full_mode
    global is_slide_check

    is_slide_check = False 
    is_full_mode = False
    
    popup.destroy()                                 # close full screen and controller
    popup2.destroy()
    
    try:
        setting_hide()
    
    except:
        pass
    
    hide_listbox()
    
    filepath = str(folder_entry.get())              # refresh root window
    file_ext = os.path.splitext(filepath)[1].lower()                  
    
    if file_ext in supported_img:
        ShowIMG(filepath)
    
    elif file_ext in supported_ani:
        ShowANI(filepath)                
    
def motion(event):                      # simple full screen or slide mode
    
    y = event.y                          # mouse pointer location
    
    if y > full_h - 70:
        popup2.focus_set()                          # show controller
        
    if y < full_h - 70:
        popup.focus_set()                           # hide controller

# In[Auto slide mode]

def start_slide():                        # slide mode or Photo Album mode
    print("start_slide")
    logging.info("start_slide")
    
    global is_slide_check
    global is_timer_pause
    global timer
    global left_slide_button
    global right_slide_button
    
    slide_button2.config(text = "Stop Slide", command=quit_slide)
    photoalbum_button2.config(state=tk.DISABLED)
    manga_button2.config(state=tk.DISABLED)
    
    is_slide_check = True
    is_timer_pause = False
    
    timer = default_timer
    
    filepath = fullfilelist[fileindex] 
    file_ext = os.path.splitext(filepath)[1].lower()
    
    if not is_photoalbum_mode:                          # slide mode
        popup.unbind("<Button-1>", button1)
        popup.unbind("<Button-3>", button3)
        left_slide_button = popup.bind("<Button-1>", leftclick_slide)
        right_slide_button = popup.bind("<Button-3>", rightclick_slide)
        
        if file_ext in supported_img:                    
            ShowIMG_Full(filepath)
        
        else:
            ShowANI_Full(filepath)

def leftclick_slide(event):
    
    global timer
    global is_skip_ani
    
    timer = timer - default_timer
    is_skip_ani = True
    
def rightclick_slide(event):
    
    global timer
    global is_skip_ani
    
    timer = timer + default_timer + gif_loop + 2
    is_skip_ani = True

def countdown_timer():                       # ShowIMG_full only, to fix "crash in slide mode when click fast for 200+ times"

    while check_timer(False) >= 0 and check_slide_mode(): # check and control timer
        popup.update()
        time.sleep(1/timer_frame)                     # maintain frame
        
        if timer > default_timer and check_slide_mode():    # forward
            fullbackward()
        
    if timer < 0 and check_slide_mode():    # forward
        fullforward()
        
def check_timer(is_ani):                                  # timer in slide mode or Photo Album mode 
    
    global timer    
    
    #print("timer:", format(timer, ".3f"), end= " ")
    #logging.info("timer: %s", timer)
    
    if not is_ani:                                            # from ShowIMG_Full and ShowIMG_Fullphotoalbum
        timer = timer - 1/timer_frame
        return timer
        
    else:                                                      # from ShowANI_Full
        timer = timer - 1                                      # timer = gif_loop
        return timer
    
def quit_slide():                                                 # slide mode and Photo Album mode
    print("quit_slide")
    logging.info("quit_slide")
    
    global button1
    global button3
    
    slide_button2.config(text = "Slide Mode", command=start_slide)
    photoalbum_button2.config(state = tk.NORMAL)
    manga_button2.config(state = tk.NORMAL)
    
    if not is_photoalbum_mode:                            # slide mode
        popup.unbind("<Button-1>", left_slide_button)
        popup.unbind("<Button-3>", right_slide_button)
    
    button1 = popup.bind("<Button-1>", fullforward)
    button3 = popup.bind("<Button-3>", fullbackward)
    
    back_simple_full()
    
# In[Photo Album Mode]

def start_photoalbum():                           # Photo Album mode
    print("start_photoalbum")
    logging.info("start_photoalbum")
    
    global pause_button
    global updown_wheel
    global esc_quit_photoalbum
    global is_photoalbum_mode
    global is_slide_check
    global timer
    
    try:
        setting_hide()
    
    except:
        pass
    
    hide_listbox()
    
    popup.unbind("<Motion>",motion1)                     # control in Photo Album mode
    popup.unbind("<Escape>", button_esc)
    popup.unbind("<MouseWheel>", wheel)
    popup.unbind("<Button-1>", button1)
    popup.unbind("<Button-3>", button3)
    popup.config(cursor='none')
    
    pause_button = popup.bind("<Button-1>", pause_auto)
    updown_wheel = popup.bind("<MouseWheel>", wheel_photoalbum)
    esc_quit_photoalbum = popup.bind("<Escape>", quit_photoalbum)
    
    is_photoalbum_mode = True
    is_slide_check = True
    
    timer = default_timer
    
    popup.focus_set()
    
    full_canvas.delete("all") 
    
    start_slide()                                 # use common definition as slide mode
    
    pic_path = fullfilelist[fileindex]
    file_ext = os.path.splitext(pic_path)[1].lower()      # separate file name and extension
    
    if file_ext in supported_img:
        ShowIMG_FullPhotoalbum(pic_path)           # Photo Album mode
    
    elif file_ext in supported_ani:
        ShowANI_Full(pic_path)                    # same as full mode for gif
       
def quit_photoalbum(event):                          # Photo Album mode
    print("quit_photoalbum")    
    logging.info("quit_photoalbum")

    global motion1
    global button_esc
    #global button1
    #global button3
    global wheel

    popup.unbind("<Button-1>", pause_button)
    popup.unbind("<MouseWheel>", updown_wheel)
    popup.unbind("<Escape>", esc_quit_photoalbum)
    
    motion1 = popup.bind("<Motion>",motion)                          # control appearance controller 
    button_esc = popup.bind("<Escape>", quit_full)
    wheel = popup.bind("<MouseWheel>",event_zoom)   
    
    popup.config(cursor='')
    quit_slide()
    
def pause_auto(event):                              # Photo Album mode
    print("pause_auto")
    logging.info("pause_auto")
    
    global is_timer_pause
    
    if not is_timer_pause:
        is_timer_pause = True
    
    else:
        is_timer_pause = False
           
def wheel_photoalbum(event):                      # Photo Album mode
    print("wheel_photoalbum")
    logging.info("wheel_photoalbum")
    
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
    
    global is_stop_ani
    global mangalist, mangaindex
    global h1,h2,h3,h4
    global updown_wheel_manga
    global esc_quit_manga
    global auto_button
    global is_auto_manga, auto
    
    try:
        setting_hide()
    
    except:
        pass
    
    hide_listbox()
    
    popup.unbind("<Motion>",motion1)                     
    popup.unbind("<Button-1>", button1)
    popup.unbind("<Button-3>", button3)
    popup.unbind("<Escape>", button_esc)
    popup.unbind("<MouseWheel>", wheel)
    popup.config(cursor='none')
    
    auto_button = popup.bind("<Button-1>", auto_scrollmanga)
    updown_wheel_manga = popup.bind("<MouseWheel>", scroll_manga)
    esc_quit_manga = popup.bind("<Escape>", quit_manga)
    
    is_stop_ani = True
    is_auto_manga = False
    full_canvas.delete("all") 
    popup.focus_set()
    
    auto = 0
    
    mangalist= []                                   # create new list to avoid gif
    
    for file in fullfilelist:
        if os.path.splitext(file)[1].lower() in supported_img:
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
    
    del img
    del resize_img
    
    print("Add: ", ['manga_%s' % pre_mangaindex])
    #print("image Height: ", resized_h1)
    logging.info("Add: %s", ['manga_%s' % pre_mangaindex])
    #logging.info("image Height: %s", resized_h1)

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
    
    del img
    del resize_img
    
    print("Add: ",  ['manga_%s' % mangaindex])
    #print("image Height: ", resized_h2)
    logging.info("Add: %s", ['manga_%s' % mangaindex])
    #logging.info("image Height: %s", resized_h2)

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
    
    del img
    del resize_img
    
    print("Add: ",  ['manga_%s' % next_mangaindex])
    #print("image Height: ", resized_h3)
    logging.info("Add: %s", ['manga_%s' % next_mangaindex])
    #logging.info("image Height: %s", resized_h3)
 
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
        
    #print("Move: ", ['manga_%s' % pre_mangaindex], ",", ['manga_%s' % mangaindex], ",", ['manga_%s' % next_mangaindex])
    #print(h1,",",h2,",", h3, "," ,h4)
    
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
    
    global is_auto_manga
    
    if is_auto_manga:
        is_auto_manga = False
    
    else:
        is_auto_manga = True
        
    while check_auto_manga():
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
    global fileindex
    
    popup.unbind("<Button-1>", auto_button)
    popup.unbind("<MouseWheel>", updown_wheel_manga)
    popup.unbind("<Escape>", esc_quit_manga)
    popup.config(cursor='')
    
    motion1 = popup.bind("<Motion>",motion)                          # control appearance controller 
    button_esc = popup.bind("<Escape>", quit_full)
    button1 = popup.bind("<Button-1>", fullforward)
    button3 = popup.bind("<Button-3>", fullbackward)
    wheel = popup.bind("<MouseWheel>",event_zoom) 
    
    del globals()['manga_%s' % pre_mangaindex]               # del to release resource
    del globals()['manga_%s' % mangaindex]                   # del to release resource
    del globals()['manga_%s' % next_mangaindex]              # del to release resource
    
    manga_filepath = mangalist[mangaindex]
    fileindex = fullfilelist.index(manga_filepath) # reset fileindex
    
    filepath = fullfilelist[fileindex]
    folder_entry.delete(0,"end")
    folder_entry.insert(1, filepath)               # reset folder entry
    
    back_simple_full()

# In[Check variable status]

def check_stop_ani():                                 # check if animation is turned off
    
    if is_stop_ani:
        return True
    
    else:
        return False
    
def check_skip_ani():                                 # check if animation skips in slide mode
    
    if is_skip_ani:
        return True
    
    else:
        return False

def check_full_mode():                                 # check if it is fullscreen
    
    if is_full_mode:
        return True
    
    else:
        return False

def check_slide_mode():                                # check if slide mode is on

    if is_slide_check:
        return True
    
    else:
        return False

def check_timer_pause():                                 # check if it is paused in zoom-slide mode
    
    if is_timer_pause:
        time.sleep(0.1)
        return True
    
    else:
        return False

def check_auto_manga():                                # check if auto manga is on

    if is_auto_manga:
        return True
    
    else:
        return False

def check_gifspeed():
    
    return gif_speed * gif_speed2

# In[Exception]

def exception_emptypath():
    
    error_label.config(text = "Please input file path")
    logging.warning("Empty file path")
    raise FileNotFoundError("Empty file path")
    
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

if __name__ == "__main__":
        
    logging_create()
    
    sys.excepthook = logging_exception  # override default uncaught exception handling by def"logging_exception"
    
    window_create()

    logging_shutdown()

# In[things to do]

r''' 
functionality (completed):
    
optimization:
change to class

bug fix:

known bugs which can't be fixed:
[severity: medium] GIF distorted (neko para vol3 and 4) (note: can't support some gifs')
[severity: low] some GIF 0.2s lag in the end of iter in exe only (Bishoujo Mangekyou) (note: maybe due to slow processing)
[severity: low] GIF can't be resized upon window resize
[severity: low] some GIF can't get duration (note: replaced by constant 40 in try except)
[severity: minor] can't launch py by double click (note: not affecting usage in exe)
[severity: low] def"logging_exception" may not work (note: probably an internal bug)

convert to exe:

https://ithelp.ithome.com.tw/articles/10231524

1) Open Windows PowerShell
2) Install Python (go to python website to install)
3) Install module including tkinter, Pillow, configparser, auto-py-to-exe, pyinstaller, ttkbootstrap
4) open auto-py-to-exe
5) 
-- onedir
-- noconfirm
-- icon
-- ascii
-- hidden import: ['ttkbootstrap']
-- collect all: ttkbootstrap

pyinstaller --noconfirm --onedir --windowed --icon "C:/Users/simon/Practice/alpaca_ico.ico" --ascii --collect-all "ttkbootstrap" --hidden-import "['ttkbootstrap']"  "C:/Users/simon/Practice/SimonAlpaca Image Viewer.py"
'''

