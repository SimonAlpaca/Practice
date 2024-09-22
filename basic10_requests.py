# -*- coding: utf-8 -*-

import os
import requests
import shutil

def get_txt(input_url, to_dir):
    
    file_obj = requests.get(input_url)                     # get the files as object
    file_text = file_obj.text                              # get text from object

    output_path = os.path.join(to_dir,"CCMC List.txt")
    output_file = open(output_path, "w")                   # create txt
    output_file.flush()
    output_file.write(file_text)                           # write
    output_file.close()
    
def get_web(input_url, to_dir):
    
    a_session = requests.Session()                        
    a_session.get(input_url)
    session_cookies = a_session.cookies
    cookies_dictionary = session_cookies.get_dict()       # get cookies
    print(cookies_dictionary)
    
    file_obj = requests.get(input_url, cookies=cookies_dictionary)
    file_text = file_obj.text

    output_path = os.path.join(to_dir,"stock.txt")
    output_file = open(output_path, "w", encoding ="utf-8")
    output_file.flush()
    output_file.write(file_text)
    output_file.close()

def get_headers(input_url):                                      # get headers 

    url_requests = requests.get(input_url)
    print(url_requests.headers)

def get_cookies(input_url):                                      # get cookies using session
    
    a_session = requests.Session()                        
    a_session.get(input_url)
    session_cookies = a_session.cookies
    cookies_dictionary = session_cookies.get_dict()       # get cookies
    print(cookies_dictionary)

def get_web_with_cookies(input_url, to_dir):                             # get web text using cookies
   
    # add headers to pretend to be browser    
    url_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/" "537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

    cookie_name = "Login"                               # find existing cookies in chrome
    cookie_value = "service_type=+&status=1&uname=sheepss&mbr_id=614722&lang=chi&ver=1&ml=0&id=14&Prelease=0&product_id=10&AccountType=P&fname=+&QW_Ver=0&broker=AASTOCKS&ucalc=0&firewall_ver=0"
    url_cookies = {cookie_name:cookie_value}

    url_requests = requests.get(input_url, headers=url_headers,cookies=url_cookies)  #get with cookies

    file_text = url_requests.text

    output_path = os.path.join(to_dir,"aastock.txt")
    output_file = open(output_path, "w", encoding ="utf-8")
    output_file.flush()
    output_file.write(file_text)
    output_file.close()
    print("Finish")

to_dir = r"C:\Users\simon\Practice"

input_url = r"http://www.aastocks.com/tc/LTP/RTPortfolioMain.aspx?"
#get_txt(input_url, to_dir)

# get_web(input_url, to_dir)
#get_headers(input_url)
get_cookies(input_url)
#get_web_with_cookies(input_url, to_dir)