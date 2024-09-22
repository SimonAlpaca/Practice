# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 14:15:12 2024

@author: simon
"""

# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import time

def get_html(input_url, url_cookies):
    
    # add headers to pretend to be browser
    url_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/" "537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    
    url_requests = requests.get(input_url, headers=url_headers,cookies=url_cookies)  #get with cookies
    url_requests.encoding = "big5"       # follow the charset in html_text
    html_text = url_requests.text                      # html text
    # print(html_text)
    
    check_last_chapter(html_text) 
    
    write_print(html_text)
    
    return html_text

def write_print(html_text):

    output_path = os.path.join(to_dir,"cartoonmad.txt")
    output_file = open(output_path, "w", encoding ="utf-8")   # create txt
    output_file.flush()

    output_file.write(html_text)
    output_file.flush()
    output_file.close()
        
def get_page_info(html_text):
    
    bs = BeautifulSoup(html_text, "lxml")   
    
    # get title
    title = bs.find_all("title")[0].get_text()
    # print(title)
    
    # get path of img
    imgs = bs.find_all('img')
    for img in imgs:
        # print(img)
        img_path = img["src"]
        
        # get total page
        if "cc.fun8.us" in img_path:
            
            find_a = bs.find_all("a")

            for a_elements in find_a:
                try:
                    total_page = int(a_elements.get_text())

                except:
                    pass
            
            # print(total_page)
            break
    
    img_path = "https:" + img_path

    # print(img_path)
    
    return title, img_path, total_page

def patch_download(next_path, url_cookies, to_dir, download_pages):
    timer = time.perf_counter()
    
    for i in range(download_pages):
        i = i + 1
        
        print(next_path)
        html_text = get_html(next_path, url_cookies)
        next_path = check_next_pic(next_path, html_text)
        
        title, img_path, total_page = get_page_info(html_text)

        file_ext = os.path.splitext(img_path)[1].lower()
        file_name = str(i).rjust(4, "0") + file_ext
            
        save_img(img_path, file_name)
    
        time_spent = round(time.perf_counter()-timer,3)
        
        print(i)
        print("Time spent : %f" %time_spent)

def check_next_pic(front_path, html_text):
    bs = BeautifulSoup(html_text, "lxml")   
    find_a = bs.find_all("a", class_="pages")
    
    for result in find_a:
        # print(result.text)
        if "下一頁" in result.text:
            next_pic_path = result["href"]
            next_pic_path = os.path.split(front_path)[0] + "/" + next_pic_path
            # print(next_pic_path)
            
    return next_pic_path

def check_next_chapter(html_text):
    bs = BeautifulSoup(html_text, "lxml")   
    find_a = bs.find_all("a", class_="pages")
    
    for result in find_a:
        # print(result.text)
        if "下一話" in result.text:
            next_chapter_path = result["href"]
            next_chapter_path = os.path.split(front_path)[0] + "/" + next_chapter_path
            # print(next_chapter_path)

def check_last_chapter(html_text):

    if "An error occurred on the server when processing the URL" in html_text:
        print("This is the last chapter")
        raise Exception
    
    else:
        # print("Not the last chapter")
        pass

def save_img(img_path, file_name):
    
    img_data = requests.get(img_path).content
    to_path = os.path.join(to_dir, file_name)
    with open(to_path, 'wb') as handler:
        handler.write(img_data)
            
front_path = r"https://cc.fun8.us/post/526400142026001.html"

url_cookies = {"ASPSESSIONIDAGRCDCQT":"JCDLNBGBNKIHIFCNGGMJFNAC", "ASPSESSIONIDQUQTBQRA":"AEELIGDCPEDKNAPPIBJHLOJF", "ASPSESSIONIDSURRARRA":"KCFOLFJAALFOEENKOMJDLNGB", "ASPSESSIONIDSWTQBQRB": "LPJLOBADDFJMPGIGJEPFEIKP", "arp_scroll_position": "0"}
to_dir = r"C:\Users\simon\Practice\Image_Downloader\Output"

html_text = get_html(front_path, url_cookies)
title, img_path, total_page = get_page_info(html_text)
next_pic_path = check_next_pic(front_path, html_text)
check_next_chapter(html_text)

patch_download(front_path, url_cookies, to_dir, total_page)


