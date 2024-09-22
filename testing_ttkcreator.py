from ttkbootstrap import Style
from tkinter import ttk
import tkinter as tk
from ctypes import windll



def quit():
    
    settinglevel.destroy()
    listlevel.destroy()
    window.destroy()

def window_zoomed():
    max_button.config(text = "\u2583", command = window_normal)
    window.state("zoomed")
    
def window_normal():
    max_button.config(text = "\u2587", command = window_zoomed)
    window.state("normal")

def dragwin(event):
    x = window.winfo_x() + event.x - offsetx
    y = window.winfo_y() + event.y - offsety

    window.geometry('+{x}+{y}'.format(x=x,y=y))

def clickwin(event):
    
    global offsetx
    global offsety
    offsetx = event.x
    offsety = event.y

def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    # re-assert the new window style
    window.wm_withdraw()
    window.after(10, lambda: root.wm_deiconify())
    
GWL_EXSTYLE=-20
WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080

style = Style(theme='darkly')
style.configure("primary.TButton", font=("Helvetica", 11,"bold")) # letter button
style.configure("second.TButton", font=("Helvetica", 19)) # unicode symbol button

window = style.master

window.overrideredirect(1)
window.geometry('500x580+300+150') 
window.title("testing theme")

offsetx = 0
offsety = 0

top_frame = ttk.Frame(window,style='Warning.TFrame')             # add frame first
top_frame.pack(pady=1, side = tk.TOP, fill = "both")
quit_button = ttk.Button(top_frame, text= "\u03A7", width=3, style='primary.Outline.TButton', command=quit)
quit_button.pack(side =tk.RIGHT, padx = 10)

max_button = ttk.Button(top_frame, text= "\u2587", width=3, style='primary.Outline.TButton', command = window_zoomed)
max_button.pack(side =tk.RIGHT, padx = 0)

top_frame.bind('<Button-1>', clickwin)
top_frame.bind('<B1-Motion>', dragwin)

 # Canvas
pic_canvas = tk.Canvas()
pic_canvas.configure(background='black')
pic_canvas.pack(side=tk.TOP, fill="both", expand=True, pady = 0, padx =10)
pic_canvas.configure(scrollregion = pic_canvas.bbox("all"))


buttondown_frame = ttk.Frame(window,style='Warning.TFrame')             # add frame first
buttondown_frame.pack(pady=5, side = tk.BOTTOM)

folder_frame = ttk.Frame(window,style='inputbg.TFrame')             # add frame first
folder_frame.pack(pady=5, side = tk.BOTTOM)

ttk.Button(buttondown_frame, text="Submit", style='primary.TButton').pack(side='left', padx=5, pady=10)
ttk.Button(buttondown_frame, text="Submit", style='primary.Outline.TButton').pack(side='left', padx=5, pady=10)

# Up Button
buttonup_frame = ttk.Frame(window,style='inputbg.TFrame')
buttonup_frame.pack(fill = "y", side = tk.BOTTOM, pady = 5)
'''
backward_button = tk.Button(buttonup_frame, text = "<-", command=backward,width=10)

full_button = tk.Button(buttonup_frame, text = "[]", command=fullscreen,width=10)
full_button.pack(side =tk.LEFT, padx = 20)
forward_button = tk.Button(buttonup_frame, text = "->", command=forward,width=10)
forward_button.pack(side =tk.LEFT, padx = 20)
'''
backward_button = ttk.Button(buttonup_frame, text= u"\u2B98", width=3, style='second.TButton')
backward_button.pack(side =tk.LEFT, padx = 20)
full_button = ttk.Button(buttonup_frame, text= u"\u29C9", width=4, style='second.TButton')
full_button.pack(side =tk.LEFT, padx = 20)
forward_button = ttk.Button(buttonup_frame, text= u"\u2B9A", width=3, style='second.TButton')
forward_button.pack(side =tk.LEFT, padx = 20)
# assign image to other object


folder_label = ttk.Label(folder_frame, text = "Folder Name : " ,style='fg.TLabel')
folder_label.pack(side=tk.LEFT)
folder_entry = ttk.Entry(folder_frame, width=54, style='success.TEntry')
folder_entry.insert(1, "testing")
folder_entry.pack()

listlevel = tk.Toplevel(window)
listlevel.resizable(False,False)
listlevel.overrideredirect(1)
listlevel.geometry("250x550+50+200")

listbox_scroll = ttk.Scrollbar(listlevel, orient='vertical', style="Vertical.TScrollbar")                     # add scroll bar
listbox_scroll.pack(side=tk.RIGHT, fill=tk.Y)

w, h = listlevel.winfo_screenwidth(), listlevel.winfo_screenheight()
listbox1 = tk.Listbox(listlevel,width=100,height=200,highlightthickness=5, selectmode = tk.SINGLE, yscrollcommand = listbox_scroll.set)
listbox1.configure(background='black')
listbox1.pack(side=tk.LEFT)
listbox_scroll.config(command = listbox1.yview)

settinglevel = tk.Toplevel(window)
settinglevel.resizable(False,False)
settinglevel.overrideredirect(1)
settinglevel.geometry("350x200+800+200")
settinglevel.configure()  

setting_frame0 = tk.Frame(settinglevel)             
setting_frame0.pack(pady=10, side = tk.TOP, fill=tk.BOTH)

test_button = ttk.Button(settinglevel, text="test", style='primary.TButton').pack(side='top', padx=5, pady=10)
parent_check = tk.BooleanVar()
setting_check = ttk.Checkbutton(setting_frame0, text="Include", var=parent_check, style = "warning.Roundtoggle.Toolbutton")
setting_check.pack(pady=0, padx = 10, side= tk.RIGHT)



setting_gifspeedstr = tk.StringVar()
setting_scroll3 = ttk.Combobox(setting_frame0, textvariable = setting_gifspeedstr, style='primary.TCombobox', values=["Very Fast", "Fast", "Normal", "Slow", "Very Slow"])

setting_scroll3.pack(pady=0, padx = 10, side= tk.BOTTOM)
setting_scroll3.current(0)
window.after(10, lambda: set_appwindow(window))
window.mainloop()

''' auto py to exe
onedir
-- hidden import: ['ttkbootstrap']
-- collect all: ttkbootstrap

replace theme.json
'''
