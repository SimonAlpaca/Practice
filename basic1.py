# while loop
# If...elif...else
# lower() and strip()

i=0
while i==0:
    Input_if=input("Please input here (T/F) : ").lower().strip()
    Input_if = Input_if[0:1]
    if Input_if=="t":
        print("It is true")
        i=1
    elif Input_if=="f":
        print("It is false")
        i=1
    else: 
        print("Please input again (T/F) : ")
        i=0

# combination of while loop and if else
# lower() means changing the whole string to lower letter
# strip() means removing spaces before and after the string
# string with [0:4] means the first 4 letters
# string with [3:10] means the 4th - 10th letters