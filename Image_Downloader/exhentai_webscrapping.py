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
    
    html_text = url_requests.text                      # html text
    # print(html_text)
    write_print(html_text)
    
    return html_text

def write_print(html_text):

    output_path = os.path.join(to_dir,"exhentai.txt")
    output_file = open(output_path, "w", encoding ="utf-8")   # create txt
    output_file.flush()

    output_file.write(html_text)
    output_file.flush()
    output_file.close()
        
def get_page_info(html_text):
    
    bs = BeautifulSoup(html_text, "lxml")   
    
    # get title
    title = bs.find_all("title")[0].get_text()
    title = title[:-15]    # exclude the ExHentai.org tag
    print(title)
    
    # get total number of pages
    total_page = bs.find_all("td", class_="gdt2")
    total_page = total_page[-2]
    total_page = total_page.get_text()      # get value inside tag
    total_page = int(total_page[:total_page.find("pages")])
    # print(total_page)
    
    return title, total_page
    
def get_first_page(html_text):
    
    bs = BeautifulSoup(html_text, "lxml")   
    first_page = bs.find_all("a")

    # print(first_page)
    exh_id = os.path.split(os.path.split(front_path[:-1])[0])[1]
    first_page_id = exh_id + "-1"
    for page in first_page:
        try:
            page_href = page["href"]
            
        except:
            page_href = ""
        
        if page_href.find(first_page_id) >= 0:
            first_page = page_href
            break
        
    # print(first_page)
    return first_page

def patch_download(next_path, url_cookies, to_dir, download_pages):
    timer = time.perf_counter()
    
    for i in range(download_pages):
        i = i + 1
        html_text = get_html(next_path, url_cookies)
        img_path = get_image_path(html_text)
        next_path = get_next_path(html_text)

        file_ext = os.path.splitext(img_path)[1].lower()
        file_name = str(i).rjust(4, "0") + file_ext
            
        save_img(img_path, file_name)
    
        time_spent = round(time.perf_counter()-timer,3)
        
        print(i)
        print("Time spent : %f" %time_spent)
        
def get_image_path(html_text):
    
    bs = BeautifulSoup(html_text, "lxml")   
    
    imgs = bs.find_all('img', id="img")
    for img in imgs:
        # print(img)
        img_path = img["src"]
        # print(img_path)
    
    return img_path

def get_next_path(html_text):
    
    bs = BeautifulSoup(html_text, "lxml")   
    paths = bs.find_all("a", id="next")
    
    next_path = paths[0]["href"]
    # print(next_path)
    
    return next_path

def save_img(img_path, file_name):
    
    img_data = requests.get(img_path).content
    to_path = os.path.join(to_dir, file_name)
    with open(to_path, 'wb') as handler:
        handler.write(img_data)
            
front_path = r"https://exhentai.org/g/2856376/a4057166f7/"

url_cookies = {"igneous":"qnzyvr5kb88ipg1aq0e", "sk":"ngk0ktce7hft83dem4njd9tzyt6y", "arp_scroll_position":"0", "ipb_pass_hash":"a9a5869db2c244a2294a38aeafa65178", "ipb_member_id":"528230"}
to_dir = r"C:\Users\simon\Practice\Image_Downloader\Output"

html_text = get_html(front_path, url_cookies)
# title, total_page = get_page_info(html_text)
# first_page = get_first_page(html_text)

# patch_download(first_page, url_cookies, to_dir, total_page)


