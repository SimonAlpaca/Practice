# -*- coding: utf-8 -*-
"""
Created on Sun Nov 27 09:17:18 2022

@author: simon
"""

import yfinance as yf

stock_list = [34,41,50,52,68,78,88,99,113,116,173,208,219,238,253,282,288,298,302,434,460,480,484,497,504,540,590,617,699,709,717,772,909,956,1024,1107,1137,1211,1212,1232,1247,1271,1290,1317,1337,1359,1428,1448,1588,1633,1685,1698,1776,1777,1811,1813,1816,1833,1918,1952,2033,2158,2217,2226,2288,2618,2819,2822,2858,2868,2957,3636,3668,3822,3900,4208,4214,4218,4222,4228,4231,4239,4246,6060,6618,6811,6839,6886,6988,6998,9633,9919,9922,9939,9996,9997
]


output_file = open("yahoofin_div.txt", "w", encoding ="utf-8")   # create txt

for stock in stock_list:
    stock_quote = str(stock).rjust(4,"0") + ".hk"
    # print(stock)
    ticker = yf.Ticker(stock_quote)
    print(ticker)
    print(ticker.dividends)

    output_file.flush()
    output_file.write("%s\n" %stock)
    output_file.write(str(ticker.dividends))
    output_file.write("\n")
    
output_file.close()


