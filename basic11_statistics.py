# list
# create list, list value
# list.append(i)
# len(list), sum(list), len(list), min(list), max(list), statistics.mean(list)

# using list instead of print

input1 = int(input("From : "))
input2 = int(input("To : "))

if input2 < input1:
    print("Error")
    import sys
    sys.exit()    #exit sub when input error

if input1 < 2:
    input1 = 2     #special case for 0 and 1

list_prime = []  # create a new list

count_prime = 0
for i in range(input1,input2 + 1):
    for j in range(2, int(i ** 0.5) + 1):
        if i % j == 0:
            break
    else:
        list_prime.append(i)  # add prime number into list
          
count_prime= len(list_prime)   # count list

sum_prime = sum(list_prime)   # sum(list) to calculate the sum in the list

import statistics                             # import statistics
median_prime = statistics.median_grouped(list_prime) #statistics.median_grouped to get median
mean_prime = statistics.mean(list_prime)  # statistics.mean to calculate mean

min_prime= min(list_prime)  # min of list

max_prime= max(list_prime)  # max of array

print(list_prime)
print("Number of Prime Number : ", count_prime) 
print("Sum of Prime Number : ",sum_prime)
print("Median of Prime Number : ", int(median_prime))
print("Mean of Prime Number : ", mean_prime)
print("Min of Prime Number : ", min_prime)
print("Max of Prime Number : ", max_prime)
