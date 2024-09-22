# for...else loop

# the upper limit of each test

def count_range(value):
    return int(value**0.5)+1

# In[Input]
# get all prime numbers in a range

while True:
    try:
        input1 = int(input("From : "))
        if input1 <= 1:
            raise ValueError
            
        break
    
    except ValueError:
        print("Error: Please input an interger bigger than 1")

while True:
    try:    
        input2 = int(input("To : "))
        if input2 <= 1:
            raise ValueError
            
        if input2 < input1:
            raise Exception
            
        break  
    
    except ValueError:
        print("Error: Please input an interger bigger than 1")
    
    except Exception:
        print("The latter value should not be smaller than the former value")

# In[Caluation]

print()
print("Prime Numbers from %s to %s" %(input1, input2))
print()

count_prime = 0

for i in range(input1,input2 + 1):
    to_range = count_range(i)
    
    for j in range(2,to_range):
        if i % j == 0:
            break
    
    else:
        print(i, end=", ")
        count_prime = count_prime+1       

total_number = input2 - input1 + 1
percentage = count_prime / total_number

print("End")
print()
print("Number of Prime Number : ", count_prime) 
print("%% of Prime Number : %2.2f%%" %(percentage * 100))

'''
%% to print "%"
import sys, sys.exit()  means exit sub
break means end the loop
continue means skip this loop and continue 
for...else loop : use with break, run else if no break
'''