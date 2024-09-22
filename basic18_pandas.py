# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

# In[1-dimension]

def one_dimension():
    
    def create_series():
        # create series
        
        global series1
        
        list1 = ["T1", "JDG", "WBG", "BLG"]
        series1 = pd.Series(list1)
        print(series1)

    def get_data():
        # modify one data
        series1[0] = "T1 Win"
        
        # replace all data contains "JDG"
        print(series1.str.replace("JDG", "Bye JDG"))
        
        # get data
        print(series1[0])
        
        # get all data into one line
        print(series1.str.cat(sep= " ,"))
    
    def concat_data():
        
        list2 = ["GEN", "NRG", "KT", "LNG"]
        series2 = pd.Series(list2)
        
        series3 = pd.concat([series1, series2], ignore_index = True)  # rearrange index if ignore index = True
        
        print(series3)
    
    def count_series():
        print(series1.size)
    
    def upper_lower():
        # change all data to upper character
        print(series1.str.upper())
        
        # change all data to lower character
        print(series1.str.lower())
        
        # check if data contains "G"
        print(series1.str.contains("G"))
    
    def series_stat():
        
        global series4
        
        list4 = [2217, 6811, 52, 41, 752, 709]
        series4 = pd.Series(list4)
        print(series4)
        
        # max
        print(series4.max())
        
        # min
        print(series4.min())
        
        # sum
        print(series4.sum())
        
        # mean
        print(series4.mean())
        
        # generate a list consisting of the largest and smallest 2 data
        print(series4.nlargest(2))
        print(series4.nsmallest(2))
    
    def series_cal():
        
        # calculation of all data
        print(series4 + 1000)
        print(series4 - 1000)
        print(series4 * 2)
        print(series4 / 2)
        print(series4 ** 0.5)
        
        # modify format; "," refers to 1000 separater; ".2f" refers to 2 decimal place
        print(series4.map("{:,.2f}".format))
        
        # add string before each data
        print(series4.map("US${:}".format))
        
    create_series()
    get_data()
    concat_data()
    count_series()
    upper_lower()
    series_stat()
    series_cal()
    
# In[2-dimension]

def two_dimension():

    def dict_to_df():
        # use dictionary to create df, column by column
        
        global df
        
        grades = {
            "name": ["Mike", "Sherry", "Cindy", "John"],
            "math": [80, 75, 93, 86],
            "chinese": [63, 90, 85, 70]
        }
         
        df = pd.DataFrame(grades)
        
        print(df)
        print("=============")
    
    def list_to_df():
        # use list to create, row by row
        
        global new_df
        
        grades = [
            ["Mike", 80, 63],
            ["Sherry", 75, 90],
            ["Cindy", 93, 85],
            ["John", 86, 70]
        ]
         
        list_df = pd.DataFrame(grades)
         
        print(list_df)
        print("=============")
    
    def head_function():
        # get the first two lines
        
        df_head = df.head(2)
        print(df_head)
        print("=============")
    
    def tail_function():
        # get the last two lines
        
        df_tail = df.tail(2)
        print(df_tail)
        print("=============")
    
    def get_row_col():
        # get all data under name column
        print(df["name"])
        print("=============")
        # get all data under row 0
        print(df[0:1])
        print("=============")
        # get all rows with math > 80
        print(df[df["math"] > 80])
        print("=============")
        # get all rows with name = Cindy
        print(df[df["name"].isin(["Cindy"])])     # need to use isin becoz can't put "=" inside print
        print("=============")
        
    def get_data():
        # modify and get one data, row 1 at col math
        df.at[1, "math"] = 82
        print(df.at[1, "math"])
        print("=============")
        # modify and get one data, row 1 at col 1
        df.iat[1,1] = 85
        print(df.iat[1, 1])
        print("=============")
        # get multiple data, row 1 and 3 at col chinese
        new_df = df.loc[[1,3],["name","chinese"]]
        print("=============")
        
        # reset_index after .loc and how to handle .at .iat 
        print("Before reset_index")
        print(new_df)
        print("at : %i" %new_df.at[1, "chinese"])    # .at can't work with loc before reset index
        print("iat : %i" %new_df.iat[0, 1])          # .iat can work with loc before reset index
        
        print("After reset_index")
        new_df2 = new_df.reset_index()     # # need to reset_index for at otherwise the index is still the old one, but for .iat, it does not need to reset index
        print(new_df2)
        print("at : %i" %new_df2.at[0, "chinese"])    # .at work with loc after reset index
        
        new_df3 = new_df.reset_index(drop=True)       # drop=True means it will drop new index column
        print("iat : %s" %new_df3.iat[0, 1])          # .iat no change if drop=True
        
        print("=============")
        # get multiple data, row 1 and 3 at col 0 and 2
        print(df.iloc[[1,3],[0,2]])
        print("=============")
        
        
    def insert_data():
        # insert data at col 2 
        
        df.insert(2, column="english", value=[50,70,95,80])
        print(df)
        print("=============")
        
    def concat_data():
        # insert rows or merge two dataframes
        
        grades = {"name": ["Henry"], "math":[70], "english":[75], "chinese":[80]}
        df2 = pd.DataFrame(grades)
        new_df = pd.concat([df, df2], ignore_index=True)
        
        print(new_df)
        
    def drop_data():
        # delete columns
        
        new_df = df.drop(["math"], axis=1)   # axis 1 refers to column
        print(new_df)
        print("=============")
        
        # delete rows
        
        new_df2 = df.drop([1], axis=0)        # axis 0 refers to row
        print(new_df2)
        print("=============")
    
    def drop_na():
        # adding data with NaN
        grades = {"name": [np.NaN, "John"], "math": [80, np.NaN], "english": [70,70], "chinese":[75,75]}
        df2 = pd.DataFrame(grades)
        new_df = pd.concat([df, df2], ignore_index = True)
        print("Before dropna: ")
        print(new_df)
        
        # clear rows with any NaN data
        new_df = new_df.dropna()
        print("After dropna: ")
        print(new_df)
    
    def drop_duplicates():
        # adding duplicates data
        grades = {"name": ["Mike"], "math": [80], "english": [50], "chinese":[63]}
        df2 = pd.DataFrame(grades)
        new_df = pd.concat([df, df2], ignore_index = True)
        print("Before drop_duplicates: ")
        print(new_df)
        
        # clear rows with all data duplicates with another row
        new_df = new_df.drop_duplicates()
        print("After drop_duplicates: ")
        print(new_df)
    
    def sort_data():
        # sort by index
        new_df = df.sort_index(ascending = False)
        print(new_df)
        print("=============")
        
        # sort by values
        new_df = df.sort_values(["math"], ascending = False)
        print(new_df)
        print("=============")
    
    def df_to_list():
        # convert 1 column in dataframe to list
        list_name = df["name"].tolist()
        print(list_name)
    
    def df_to_dict():
        # convert df to dictionary
        dict_convert = df.to_dict()
        print(dict_convert)
    
    dict_to_df()
    # list_to_df()
    # tail_function()
    get_row_col()
    get_data()
    # insert_data()    
    # # concat_data()
    # # drop_data()
    # # drop_na()
    # # drop_duplicates()
    # sort_data()
    # df_to_list()
    # df_to_dict()

# In[Import]
def import_pandas():
    
    def import_excel():
        
        global df_excel
        
        excel_path = r"D:\stock_quote_excel\Portfolio_Tax_Management.xlsm"
        sheet_name = "Current_Position"
        df_excel = pd.read_excel(excel_path, sheet_name = sheet_name)
        
        df_excel = df_excel.dropna()   # clear rows with NaN
        
        print(df_excel)
    
    def import_csv():
        
        csv_path = r"C:\Users\simon\Practice\pandas_export.csv"
        df_csv = pd.read_csv(csv_path)
        
        print(df_csv)
    
    def save_csv():
        
        save_path = r"C:\Users\simon\Practice\pandas_export.csv"
        df_excel.to_csv(save_path, index=False)
    
    def save_excel():
        
        save_path = r"C:\Users\simon\Practice\pandas_export.xlsx"
        sheet_name = "Sheet1"
        df_excel.to_excel(save_path, sheet_name = sheet_name, index=False)

    import_excel()
    # save_csv()
    import_csv()
    # save_excel()
    
# In[Initial]

# one_dimension()
two_dimension()
# import_pandas()