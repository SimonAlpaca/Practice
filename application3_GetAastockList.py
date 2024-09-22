# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import time

def get_html(input_url, cookie_name, cookie_value):
    global div_tr
    global div_a
    
    # add headers to pretend to be browser
    url_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/" "537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    
    url_cookies = {cookie_name:cookie_value}
    
    url_requests = requests.get(input_url, headers=url_headers,cookies=url_cookies)  #get with cookies
    
    html_text = url_requests.text                      # html text
    bs = BeautifulSoup(html_text, "lxml")              # add to beautifulsoup
    bs_div = bs.find("div", class_="div-container")    # find html -> div class "div-container"
    div_tr = bs_div.find_all("td", class_="R")         # find html -> div class "div_container -> td class "R"
    div_a = bs_div.find_all("a", {"href" : True})      # find html -> div class "div_container -> a with href
    
def create_list():
    global stock_name
    global stock_quote
    global stock_price
    
    stock_name = []                                    # list of stock name
    stock_quote = []                                   # list of stock quote
    stock_price = []                                   # list of stock price
    
    for j in range(len(div_a)):
        if ".HK" in div_a[j].text:
            stock_name.append(div_a[j].text[:-8])
            stock_quote.append(div_a[j].text[-8:])
    
    for k in range(len(div_tr)):
        if "(港元)" in div_tr[k].text:
            stock_price.append(float(div_tr[k].text[:-4]))

def write_print(to_dir):

    output_path = os.path.join(to_dir,"aastock2.txt")
    output_file = open(output_path, "w", encoding ="utf-8")   # create txt
    output_file.flush()
    
    for i in range(len(stock_price)):                         # write txt
        print(i+1, "\t" , stock_name[i], "\t" , stock_quote[i], "\t", stock_price[i])
        output_file.write(str(i+1) + "\t" + stock_name[i] + "\t" + stock_quote[i] + "\t" + str(stock_price[i]) + "\n")
        output_file.flush()

    output_file.close()

timer = time.perf_counter()
input_url = r"http://www.aastocks.com/tc/LTP/RTPortfolioMain.aspx?"
cookie_name = "Login"                               # find existing cookies in chrome
cookie_value = "service_type=+&status=1&uname=sheepss&mbr_id=614722&lang=chi&ver=1&ml=0&id=14&Prelease=0&product_id=10&AccountType=P&fname=+&QW_Ver=0&broker=AASTOCKS&ucalc=0&firewall_ver=0"

to_dir = r"C:\Users\simon\Practice"

get_html(input_url, cookie_name, cookie_value)
create_list()
write_print(to_dir)

time_spent = round(time.perf_counter()-timer,3)

print("Time spent : %f" %time_spent)
