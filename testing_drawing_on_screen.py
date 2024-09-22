# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 12:39:53 2022

@author: simon
"""

import win32gui, win32ui
from win32api import GetSystemMetrics
import ctypes

awareness = ctypes.c_int()
ctypes.windll.shcore.SetProcessDpiAwareness(2)     # set awareness level to get accurate cursor position

dc = win32gui.GetDC(0)
dcObj = win32ui.CreateDCFromHandle(dc)
hwnd = win32gui.WindowFromPoint((0,0))
monitor = (0, 0, GetSystemMetrics(0), GetSystemMetrics(1))

ori_x = win32gui.GetCursorPos()[0]
ori_y = win32gui.GetCursorPos()[1]

while True:
    try:
        # m = win32gui.GetCursorPos()
        current_x = win32gui.GetCursorPos()[0]
        current_y = win32gui.GetCursorPos()[1]
        # dcObj.Rectangle((m[0], m[1], m[0]+30, m[1]+30))
        dcObj.Rectangle((ori_x, ori_y, current_x, current_y))
        win32gui.InvalidateRect(hwnd, monitor, True) # Refresh the entire monitor

    except KeyboardInterrupt:
        print("break")
        break
    
win32gui.InvalidateRect(hwnd, monitor, True) # Refresh the entire monitor