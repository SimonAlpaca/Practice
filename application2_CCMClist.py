# -*- coding: utf-8 -*-
import requests

# In[IO]
CCMC_Link = "https://www.treasury.gov/ofac/downloads/ccmc/nscmiclist.txt"

output_path = r"C:\ProgramData\Anaconda3\Practice\CCMC_Output.csv"

CCMC_get = requests.get(CCMC_Link)
CCMC_get.raise_for_status()                 # raise exception for error code e.g. 404 

# In[merge paragraph and separate rows]

CCMC_text = CCMC_get.text
CCMC_text = CCMC_text.replace("\n\n","^o^")
CCMC_text = CCMC_text.replace("\n"," ")
CCMC_text = CCMC_text.replace("\r"," ")
CCMC_text = CCMC_text.replace(",",".")      # replace "," for creating csv
rows = []
rows = CCMC_text.split("^o^")


# In[create file]

with open(output_path, "w", encoding = "utf-8") as output_csv:
    output_csv.flush()
    
# In[count the number of columns needed]
    
    max_col_ticker = 0
    max_col_isin = 0
    
    for row in rows:
        column = []
        column = row.split(";")
        col_no_ticker = 0
        col_no_isin = 0
        for value in column:
            if " Equity Ticker " in value:               # count no. of column needed for equity ticker
                col_no_ticker = col_no_ticker + 1
                max_col_ticker = max(max_col_ticker, col_no_ticker)
            if " ISIN " in value:                        # count no. of column needed for isin 
                col_no_isin = col_no_isin + 1
                max_col_isin = max(max_col_isin, col_no_isin)

# In[write and output]
    output_csv.write("Name")                             # write column header
    output_csv.write(",Equity Ticker" * max_col_ticker)
    output_csv.write(",ISIN" * max_col_isin)
    output_csv.write("\n")
    
    for row in rows:                                      # for each row
    
        if row in rows[0:2]:                              # skip the first 2 rows
            continue
        
        column = []
        column = row.split(";")
        
        name_col = column[0]                             # remove aka and fka in name column
        name_find = column[0].find("(a.k.a")             
        name_find2 = column[0].find("(f.k.a")
        if max(name_find, name_find2) > 0:               # find returns -1 if not found
            max_name_find = max(name_find, name_find2)
            name_col = name_col[:max_name_find]          # equal to left function
        output_csv.write(name_col + ",")                 # write name column
        
        col_no2_ticker = 0
        for value in column:                               # write equity ticker columns
            if " Equity Ticker " in value:
                value = value.replace(" Equity Ticker ", "")
                value = value.replace(" alt.", "")
            
                output_csv.write(value + ",")
                col_no2_ticker = col_no2_ticker + 1
        output_csv.write("," * (max_col_ticker - col_no2_ticker))      # fill blank columns if less than max column
            
        
        column = []
        column = row.split(";")

        col_no2_isin = 0
        for value in column:                                # write isin columns
            if " ISIN " in value:
                value = value.replace(" ISIN ", "")
                value = value.replace(" alt.", "")
            
                output_csv.write(value + ",")
                col_no2_isin = col_no2_isin + 1
                
        output_csv.write("," * (max_col_isin - col_no2_isin))        # fill blank columns if less than max column
            
        output_csv.write("\n")                              # next row
      


    
    
