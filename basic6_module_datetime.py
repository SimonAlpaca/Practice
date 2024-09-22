# module time

import time as t


print(t.localtime())     # now if blank; return a set of time data

weekday = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
time_now = t.localtime()
print("Today is " + str(weekday[time_now.tm_wday]))    #declare a list and apply



# module datetime
import datetime as dt

print(dt.datetime.now())         # get current time in module datetime
print(dt.date(2021,6,23))
print(dt.time(15,55,30))

date1 = dt.datetime(2021,6,23)   #dt.date works as well
date2 = dt.datetime(2021,6,1)
print(date1 - date2)        # it can calculate directly

date3 = "25/6/2021"
day3, month3, year3 = map(int, date3.split("/"))
print(dt.date(year3, month3, day3))

# date3.split to convert the string into list ["25","6","2021"]
# map function to convert the list into int and declare into 3 variables

date4 = "20/4/2021"
print(dt.datetime.strptime(date4, "%d/%m/%Y"))   # another way to convert str into date

