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

    output_path = os.path.join(to_dir,"baozimh.txt")
    output_file = open(output_path, "w", encoding ="utf-8")   # create txt
    output_file.flush()

    output_file.write(html_text)
    output_file.flush()
    output_file.close()
        
def get_page_info(html_text):
    
    bs = BeautifulSoup(html_text, "lxml")   
    
    # get title
    title = bs.find_all("title")[0].get_text()
    title = title[:-7]    # exclude the baozhi tag
    title_separater = title.find(" - ")
    print(title)
    # print(title_separater)
    
    title_no = title[:title_separater]
    title_name = title[title_separater + 3:]
    
    title = title_name + "_" + title_no
    print(title)
    
    # get list of pic in the page
    # total_page = bs.find_all("td", class_="gdt2")
    # total_page = total_page[-2]
    # total_page = total_page.get_text()      # get value inside tag
    # total_page = int(total_page[:total_page.find("pages")])
    img_list = []
    imgs = bs.find_all('amp-img')
    for img in imgs:
        # print(img)
        img_path = img["src"]
        if "baozicdn.com" in img_path:
            img_list.append(img_path)
    # print(total_page)
    # print(img_list)
    total_page = ""
    return title, img_list

def patch_download(next_path, url_cookies, to_dir, img_list):
    timer = time.perf_counter()
    
    i = 0
    for img_path in img_list:
        i = i + 1
        # html_text = get_html(next_path, url_cookies)
        # img_path = get_image_path(html_text)
        # next_path = get_next_path(html_text)

        file_ext = os.path.splitext(img_path)[1].lower()
        file_name = str(i).rjust(4, "0") + file_ext
            
        save_img(img_path, file_name)
    
        time_spent = round(time.perf_counter()-timer,3)
        print(i)
        print("Time spent : %f" %time_spent)

def check_last_chapter(html_text):
    bs = BeautifulSoup(html_text, "lxml")   
    next_chapter = bs.find_all("div", class_="next_chapter")
    next_chapter = next_chapter[0].get_text()
    print(next_chapter)

def save_img(img_path, file_name):
    
    img_data = requests.get(img_path).content
    to_path = os.path.join(to_dir, file_name)
    with open(to_path, 'wb') as handler:
        handler.write(img_data)
            
front_path = r"https://www.hbmanga.com/comic/chapter/gebulinshashou-heilaihaojieguaniukumo/0_97.html"

url_cookies = {"cdn_domain":"-mha1-nlams.baozicdn.com", "tuid":"Sxz2dl5Dp6bypfEafyGVoigtCMBD88Xz"}
to_dir = r"C:\Users\simon\Practice\Image_Downloader\Output"

html_text = get_html(front_path, url_cookies)
# title, img_list = get_page_info(html_text)

# check_last_chapter(html_text)
# patch_download(front_path, url_cookies, to_dir, img_list)


