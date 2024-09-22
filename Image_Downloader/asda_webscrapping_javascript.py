# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 15:52:46 2024

@author: simon
"""

# import libraries
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

# specify the url
urlpage = 'https://groceries.asda.com/search/yogurt' 

# run firefox webdriver from executable path of your choice
driver = webdriver.Firefox()

# get web page
driver.get(urlpage)
time.sleep(5)

# execute script to scroll down the page
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")

# sleep for 5s
time.sleep(5)

# find elements by xpath
# results = driver.find_elements("xpath", "//*[@class=' co-product-list__main-cntr']//*[@class=' co-item ']//*[@class='co-product']//*[@class='co-item__title-container']//*[@class='co-product__title']")
result_title = driver.find_elements(By.CLASS_NAME, 'co-product__title')
result_price = driver.find_elements(By.CLASS_NAME, 'co-product__price')
print('Number of results', len(result_title))

# create empty array to store data
data = []
# loop over results
for i in range(len(result_title)):
    product_name = result_title[i].text
    product_price = result_price[i].text
    product_price = product_price.replace("now\n", "")
    link = result_title[i].find_element('tag name', 'a')
    product_link = link.get_attribute("href")
    # append dict to array
    data.append({"product" : product_name, "price" : product_price, "link" : product_link})
    
    # get the first 60 results
    if i == 59:
        break
    
# close driver 
driver.quit()
# save to pandas dataframe
df = pd.DataFrame(data)
print(df)

export_path = r"C:\Users\simon\Practice\Image_Downloader\Output\asda.csv"
df.to_csv(export_path)