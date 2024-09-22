# for loop
# print and its format

def multi_table_eq(start_no, end_no, eq):
    end_no = end_no + 1
    if eq == True:
        for i in range(start_no, end_no):
            for j in range(start_no, end_no):
                product = i*j
                print("%2d*%d=%d" %(i,j,product), end=" ")
            print() # next line
            
    else:
        for i in range(start_no,end_no): 
            for j in range(start_no,end_no):
                product = i*j
                print("%3d" %product, end=" ") 
            print() # next line
        
        '''
        # range(1,11) means i = 1 to 10
        # end=" " means adding a space after each cell
        # print() means starting in a new line
        # "%-3d" %product means 3 space for each cell and align to the left
        # "%3d" &product means 3 space for each cell and align to the right

        #"%2d*%2d=%3d" %(a,b,product2) % to insert multiple variables
        '''
        
START = 1
END = 10
EQ = True

multi_table_eq(START, END, EQ)