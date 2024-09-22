# -*- coding: utf-8 -*-

import yfinance as yf
import pandas as pd
import numpy as np
import datetime
from scipy import stats
import threading
import time

# In[YFquote]

class YFquote:
    
    def __init__(self, name, column_list):
        
        self.quote = name
        self.column_list = column_list

        # self.data_download()
        
        self.thread_download = threading.Thread(target = self.data_download)
        self.thread_download.start()
        
    def data_download(self):
        
        ticker = yf.Ticker(self.quote)
        self.history_data = ticker.history(period='5y')
        # print(self.history_data.index)
        date_column = self.history_data.index.date
        
        self.history_data.insert(loc=0, column="Date", value=date_column)
        
        col_weekday = []
        for date in self.history_data.index:
            col_weekday.append(date.weekday())
            
        self.history_data.insert(loc=len(self.history_data.columns), column="Weekday", value=col_weekday)
        
        self.add_daily_perf()
            
        # print(self.history_data)
        save_path = r"C:\Users\simon\Practice\%s_close_export.csv" %self.quote
        self.history_data.to_csv(save_path)
        # self.history_data[['Close','Weekday']].to_csv(save_path)
    
        self.calculation()
    
    def add_daily_perf(self):
        
        daily_perf = []
        daily_perf = self.history_data['Close'].pct_change()
        self.history_data.insert(loc=len(self.history_data.columns), column="Daily_Perf", value=daily_perf)

    def array_adjustment(self, benchmark):
        
        dates_to_filter = self.history_data['Date']
        
        if benchmark == "benchmark_index":
            df = benchmark_index.history_data
        
        elif benchmark == "risk_free_rate":
            df = risk_free_rate.history_data
        
        filtered_benchmark = df[df['Date'].isin(dates_to_filter)]
        
        return filtered_benchmark
        
    def calculation(self):
        
        for column in self.column_list:
            
            if column == "standard_deviation":
                self.standard_deviation_calculation()
                
            if column == "sharpe_ratio":
                self.sharpe_ratio_calculation()
                
            if column == "beta":
                if not hasattr(self, "beta"):
                    self.beta_calculation()
                    
            if column == "alpha":
                if not hasattr(self, "alpha"):
                    self.beta_calculation()
                    
            if column == "r_squared":
                if not hasattr(self, "r_squared"):
                    self.beta_calculation()
                    
            if column == "value_at_risk":
                self.value_at_risk_calculation()
                
            if column == "max_drawdown":
                self.max_drawdown_calculation()
    
    def beta_calculation(self):
        
        # benchmark_return = benchmark_index.history_data['Daily_Perf'][1:]
        stock_return = self.history_data['Daily_Perf'][1:]
        
        # adjust benchmark data according to date of stock trading
        benchmark_array = self.array_adjustment("benchmark_index")
        benchmark_return = benchmark_array['Close'].pct_change()[1:]
        
        # covariance = np.cov(stock_return,benchmark_return) # Calculate covariance between stock and market
        # print(covariance[0,1])
        # self.beta = covariance[0,1] / covariance[1,1]
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(benchmark_return, stock_return)
        
        self.beta = slope
        self.alpha = (1 + intercept) ** 252 - 1
        self.r_squared= r_value ** 2
        
    def standard_deviation_calculation(self):
        
        array_stockprice = self.history_data['Daily_Perf'][1:]
        number_of_days = 252
        
        self.standard_deviation = np.std(array_stockprice, ddof = 1)        # sample standard deviation

        self.standard_deviation = self.standard_deviation * (number_of_days) ** 0.5       # annualize from daily perf

        # print("%s : %.2f%%" %(self.quote, self.standard_deviation))

    def sharpe_ratio_calculation(self):
        
        number_of_days = self.history_data.index[-1] - self.history_data.index[0]
        number_of_days = number_of_days.days     # convert from timedelta to int
        
        cumulative_perf = self.history_data['Close'][-1] / self.history_data['Close'][0] -1
        cumulative_perf = round(cumulative_perf, 6)       # to fix RuntimeWarning: invalid value encountered in scalar power
        annualized_perf = (cumulative_perf + 1) ** (365/number_of_days) - 1
        
        risk_free_rate.history_data['Daily_Perf'] = (1 + risk_free_rate.history_data['Close'] / 100) ** (1/252) - 1
        risk_free_rate.history_data['Cumulative_Return'] = (1 + risk_free_rate.history_data['Daily_Perf']).cumprod() - 1
        annualized_benchmark_perf = (risk_free_rate.history_data['Cumulative_Return'][-1] + 1) ** (365/number_of_days) - 1
        
        annualized_sd = self.standard_deviation
        
        self.sharpe_ratio = (annualized_perf - annualized_benchmark_perf) / annualized_sd
    
    def value_at_risk_calculation(self):
        
        confidence_level = 0.95
        stock_return = self.history_data['Daily_Perf'][1:]
        
        # historical method
        historical_var = np.percentile(stock_return, (1- confidence_level) * 100)
        historical_var = abs(historical_var)
        
        # variance-covariance method
        mean_return = stock_return.mean()
        std_return = stock_return.std()
    
        z_score = stats.norm.ppf(1 - confidence_level)
        vc_var = mean_return + z_score * std_return
        vc_var = abs(vc_var)
        
        # take higher value of the two method
        self.value_at_risk = max(historical_var, vc_var)   
        
    def max_drawdown_calculation(self):

        self.history_data['CumulativeMax'] = self.history_data['Close'].cummax()  # cumulative maximum
        
        self.history_data['Drawdown'] = self.history_data['Close'] / self.history_data['CumulativeMax'] - 1
        
        self.max_drawdown = self.history_data['Drawdown'].min()

# In[benchmark]

class benchmark(YFquote):
    
    def __init__(self, name):
        
        self.quote = name
        
        self.data_download()
    
    def data_download(self):
        
        super().data_download()    # run data_download under YFquote
    
    def calculation(self):
        pass                       # skip for benchmark
    
    def add_daily_perf(self):
        pass                       # skip for benchmark

# In[other functions]

def correlation_matrix(class_yfquote_list):
    
    corr_dict = {}
    
    for i in range(len(class_yfquote_list)):
        class_quote = getattr(class_yfquote_list[i], "quote")
        class_history_data = getattr(class_yfquote_list[i], "history_data")
        class_daily_perf = class_history_data["Daily_Perf"]
        corr_dict[class_quote] = class_daily_perf
    
    df = pd.DataFrame(corr_dict)
    
    correlation_matrix = df.corr()
    
    print(correlation_matrix)
    
    # export_to_csv(correlation_matrix, "_corr")
    export_to_txt(correlation_matrix, "_corr")

# In[output]

def table_generate(class_yfquote_list, column_list):
    
    result_dict = {}
    
    column_list.insert(0, "quote")
    for j in column_list:
        result_value_list = []
        
        for i in range(len(class_yfquote_list)):
            try:
                value = getattr(class_yfquote_list[i], j)
                result_value_list.append(value)
            
            except AttributeError as e:
                print(e)
                e_quote = getattr(class_yfquote_list[i], "quote")
                print("%s : %s" %(e_quote, j))

                result_value_list.append(None)
        
        result_dict[j] = result_value_list
    
    df = pd.DataFrame(result_dict)
    
    print(df)
    
    # export_to_csv(df)
    # export_to_txt(df)

def export_to_csv(df, name=""):
    
    save_path = r"C:\Users\simon\Practice\RiskMetrics_Export%s.csv" %name
    df.to_csv(save_path)
    
def export_to_txt(df, name=""):
    
    save_path = r"C:\Users\simon\Practice\RiskMetrics_Export%s.txt" %name
    df.to_csv(save_path, sep='\t')

# In[initial]

quote_list = ["6811.hk", "1428.hk", "0041.hk", "0752.hk", "6882.hk"]
column_list = ["standard_deviation", "sharpe_ratio", "alpha", "beta", "r_squared", "value_at_risk", "max_drawdown"]
# column_list = ["standard_deviation", "beta", "sharpe_ratio"]

benchmark_index = benchmark("^HSI")
risk_free_rate = benchmark("^IRX")      # 13 week treasury bill

class_yfquote_list = []

# i = 0
for quote in quote_list:
    # i = i + 1
    # globals()["quote_%i" %i] = YFquote(quote, column_list)
    # class_yfquote_list.append(globals()["quote_%i" %i])

    class_yfquote_list.append(YFquote(quote, column_list))
    
for class_yfquote in class_yfquote_list:
    class_yfquote.thread_download.join(timeout = 5)
    
table_generate(class_yfquote_list, column_list)

correlation_matrix(class_yfquote_list)

# In[things to do]

'''
functionality:
- weekly data/  monthly data   
- convenient way to check calculation
- run script by clicking .py

optimization:
    

debug:
- sharpe ratio calculation
'''
