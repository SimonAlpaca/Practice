#module random

import random as rad
import statistics


def countif(list_name,find_name):
    count_number = 0
    for list_no in range(len(list_name)):
        if list_name[list_no] == find_name:
            count_number = count_number + 1
    return count_number

def random_diminish(total, percentage):
    trial = 0
    while total > 0 :
        random_generator = rad.random()

        if random_generator > (1-percentage):
            total = total - 2
       
        elif random_generator > percentage:
            total = total - 1
        
        else:
            total = total - 0
        
        trial = trial + 1
        
    print("Total trial : %i" %trial)
    
    return trial

def trial_loop(loop):
    
    list_trial = []
    list_trial = [0] * 40

    for i in range(loop):
        trial = random_diminish(20,0.15)
        
        # for j in range(trial):
        #     list_trial = [0] * max(0, (trial - len(list_trial) + 1))
                             
        list_trial[trial] = list_trial[trial] + 1
    
    print(list_trial)
    
    for j in range(len(list_trial)):
        print("%i : %i" %(j,list_trial[j]))

trial_loop(1000)

# list_random = []


# for i in range(1000):
#     i = rad.randint(1,6)             # randomly choose from 1 to 6, same result as rad.choice([1,2,3,4,5,6])
#     list_random.append(i)

# print("1: " , countif(list_random,1)) # same result as print(list_random.count(1))
# print("2: " , countif(list_random,2))
# print("3: " , countif(list_random,3))
# print("4: " , countif(list_random,4))
# print("5: " , countif(list_random,5))
# print("6: " , countif(list_random,6))

