# -*- coding: utf-8 -*-
# https://pypi.org/project/yfinance/

import yfinance as yf
import time
from datetime import datetime
import threading
import os
import sys
import tkinter as tk
from ttkbootstrap import Style
from tkinter import ttk
from ctypes import windll
import configparser
import traceback

class WindowGUI(tk.Frame):
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.stock_info = {}
        self.stock_list = []
        self.to_dir = ""
        self.auto = False
        
        style.configure("primary.TButton", font=("Helvetica", 11,"bold")) # letter button
        
        self.parent.overrideredirect(True)                                  
        self.parent.geometry('540x420+300+150')                                 # window size  
        self.parent.resizable(width=False,height=False)                   # disallow window resize
        self.parent.title("SimonAlpaca Yahoo Finance Downloader")                  # title
        self.parent.withdraw()
   
        self.frame_top1 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_top1.pack(pady=1, side = tk.TOP, fill = "both")
        self.quit_button = ttk.Button(self.frame_top1, text= "\u03A7", width=3, style='primary.Outline.TButton', command = self.quit)
        self.quit_button.pack(side =tk.RIGHT, padx = 10)
        
        self.frame_mid1 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_mid1.pack(pady=1, side = tk.TOP, fill = "both")
        self.frame_mid2 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_mid2.pack(pady=1, side = tk.TOP, fill = "both")
        self.frame_mid3 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_mid3.pack(pady=5, side = tk.TOP, fill = "both")
        self.frame_mid4 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_mid4.pack(pady=8, side = tk.TOP, fill = "both")
        
        self.quote_label = tk.Label(self.frame_mid1, text = "    Input Stock Quote :", fg = "Yellow", font = ("Arial", 10))
        self.quote_label.pack(side = tk.LEFT)
        self.quote_text = tk.Text(self.frame_mid2, height=4, width=65, background='gray25')
        self.quote_text.pack(side=tk.TOP)
        self.dir_label = tk.Label(self.frame_mid3, text = "    Output Directory :", fg = "Yellow", font = ("Arial", 10))
        self.dir_label.pack(side = tk.LEFT)
        self.dir_text = tk.Text(self.frame_mid4, height=1, width=65, background='gray25')
        self.dir_text.pack(side=tk.TOP)
        
        self.frame_bot1 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_bot1.pack(pady=5, side = tk.TOP, fill = "both")
        self.frame_bot2 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_bot2.pack(pady=1, padx=35, side = tk.LEFT)
        self.frame_bot3 = ttk.Frame(self.parent,style='Warning.TFrame')             # add frame first
        self.frame_bot3.pack(pady=15, padx=35, side = tk.RIGHT, fill = "both")
        
        self.progress_label = tk.Label(self.frame_bot1, text = "    Progress :", fg = "Yellow", font = ("Arial", 10))
        self.progress_label.pack(side = tk.LEFT)
        self.progress_text = tk.Text(self.frame_bot2, height=9, width=35, background='gray25')
        self.progress_text.pack(side=tk.LEFT)
        self.progress_scroll = ttk.Scrollbar(self.frame_bot2, orient='vertical', command=self.progress_text.yview)
        self.progress_scroll.pack(side=tk.RIGHT, fill='y')
        self.progress_text['yscrollcommand'] = self.progress_scroll.set
        self.refresh_button = ttk.Button(self.frame_bot3, text= "Refresh", width=30, style='primary.TButton', command= self.refresh)
        self.refresh_button.pack(side=tk.BOTTOM, pady = 20, fill = "both")              # padx means gap of x-axis
        self.auto_button = ttk.Button(self.frame_bot3, text= "Auto", width=30, style='primary.TButton', command= self.auto_refresh)
        self.auto_button.pack(side=tk.BOTTOM, pady = 10, fill = "both")              # padx means gap of x-axis
        
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
        self.set_appwindow()
        
        self.import_config()
        
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
    
    def import_config(self):
        # Import config
        self.config = configparser.ConfigParser()
        
        try:
            exe_dir = os.path.split(sys.argv[0])[0]        # sys.argv[0] is the exe path
            self.config_path = os.path.join(exe_dir, "config_yf.ini")
            self.config.read(self.config_path)
            config_dir = self.config.get("YF_Download", "Dir")
            config_quote = self.config.get("YF_Download", "Quote")
            
            self.dir_text.insert(tk.INSERT, config_dir)
            self.quote_text.insert(tk.INSERT, config_quote)
        
        except Exception as e:
            print(e)
    
    def auto_refresh(self):
        print("auto_refresh")
        
        self.auto = True
        self.auto_button.config(text = "Pause", command=self.pause_refresh)

        while True:
            if self.auto:
                self.parent.update()
                self.refresh()
                
                time.sleep(max(0, 3 - self.time_spent))
            
            else:
                break
            
    def pause_refresh(self):
        print("pause_refresh")
        
        self.auto = False
        self.auto_button.config(text = "Auto", command=self.auto_refresh)
        self.parent.update()
    
    def refresh(self):
        
        timer = time.perf_counter()
        self.stock_info = {}
        self.stock_list = []
        self.err_dict = {}
        self.is_err = False
        self.progress = ""
        quote_get = str(self.quote_text.get(1.0, "end-1c"))
        self.stock_list = quote_get.split()
        #print(self.stock_list)
        
        self.progress_text.insert("1.0", "  *** Loading ***\n")
        
        for stock in self.stock_list:
            globals()['thread_ticker_%s' % stock] = threading.Thread(target = self.get_info, args=(stock,))
            globals()['thread_ticker_%s' % stock].start()
            
        for stock in self.stock_list:
            self.parent.update()
            globals()['thread_ticker_%s' % stock].join(timeout = 5)
        
        self.write_print()
        
        if self.is_err:
            self.progress_text.delete('1.0', '2.0')
            err_cantwrite()
        
        else:
            self.progress_text.delete('1.0', '2.0')
            self.time_spent = round(time.perf_counter() - timer,3)
            print("Time spent : %f\n" %self.time_spent)
            
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            
            self.progress_text.insert("1.0", "%s Success; Time Spent : %.3fs\n" %(current_time, self.time_spent))
            
    def get_info(self, stock):
        
        if stock != "***":
            if stock.isnumeric():
                stock_code = stock.rjust(4,"0") + ".hk"
            
            else:
                stock_code = stock
            
            ticker = yf.Ticker(stock_code)
            self.stock_info[stock] = ticker.info
        #print(ticker.info)
            
    def write_print(self):
        
        self.to_dir = str(self.dir_text.get(1.0, "end-1c"))
        
        output_path = os.path.join(self.to_dir,"yahoofin_data.txt")
        
        try:
            output_file = open(output_path, "w", encoding ="utf-8")   # create txt
        
        except FileNotFoundError:
            err_filenotfound()
            
        output_file.flush()
        
        print("Stock\t\t\t Quote\t\t Price\t Change\t %\t\t Vol")
        output_file.write("Stock\tQuote\tPrice\tChange\t%\tVolume\n")
        
        for stock in self.stock_list:                         # write txt
            if stock != "***":
                
                try:
                    self.progress = stock
                    stock_name = self.stock_info[stock]["shortName"]
                    stock_symbol = self.stock_info[stock]["symbol"]
                    stock_price = self.stock_info[stock]["regularMarketPrice"]
                    stock_volume = self.stock_info[stock]["regularMarketVolume"]
                    stock_preprice = self.stock_info[stock]["regularMarketPreviousClose"]
                    stock_price_change = round(stock_price - stock_preprice, 2)
                    stock_price_change_pct = round(100 * (stock_price_change) / stock_preprice, 2)
                    
                    print("%s\t %s\t %s\t %s\t %2s%%\t %s" %(stock_name, stock_symbol, stock_price, stock_price_change, stock_price_change_pct, stock_volume))
                    output_file.write("%s\t%s\t%s\t%s\t%s\t%s\n" %(stock_name, stock_symbol, stock_price, stock_price_change, round(stock_price_change_pct/100,4), stock_volume))
            
                    output_file.flush()
                
                except KeyError:
                    self.err_dict[self.progress] = traceback.format_exc()
                    self.is_err = True
                    
            else:
                print("******")
                output_file.write("******\n")
                
                output_file.flush()
    
        output_file.close()
    
    def quit(self):
        
        try:
            self.config_file = open(self.config_path, "w")
        
        except PermissionError:
            raise PermissionError("No write permission of the directory") 

        try:
            self.config.add_section("YF_Download")
            
        except configparser.DuplicateSectionError:
            pass                                   # exception if already have config and section
        
        finally:
            quote_get = str(self.quote_text.get(1.0, "end-1c"))
            dir_get = str(self.dir_text.get(1.0, "end-1c"))
            self.config.set("YF_Download", "Quote", str(quote_get))
            self.config.set("YF_Download", "Dir", str(dir_get))
            
            self.config.write(self.config_file)
            self.config_file.close()
        
        window.parent.destroy()
        
# In[Exception]

def err_filenotfound():
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    window.progress_text.insert("1.0", "%s Fail;No such file or directory" %current_time)
    raise FileNotFoundError("No such file or directory")

def err_cantwrite():
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    list_keys = list(window.err_dict.keys())
    list_values = list(window.err_dict.values())
    
    for i in range(len(list_keys)):
        print("Cant write : %s" % list_keys[i])
        print(list_values[i])
        window.progress_text.insert("1.0", "%s" % list_values[i])
        window.progress_text.insert("1.0", "%s\n" % list_keys[i])
    
    window.progress_text.insert("1.0", "%s Fail;\n" %(current_time))
    
# In[Initial]

if __name__ == "__main__":

    style = Style(theme='darkly')                             # need manual modification of theme file
    style_master = style.master                                         # create window by ttk

    window = WindowGUI(style_master)
    
    window.mainloop()        # must add at the end to make it run
    
    os._exit(1)
    
'''
Functionality:

- column selection?

Optimization:
    
Bug:
    
'''
