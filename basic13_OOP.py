# -*- coding: utf-8 -*-

tax_id = "n/a"

class Company():
    def __init__(self, id):                    # contructor
        #global address                         # global variable works for def in same class
        global tax_id
        self.address = "Hong Kong"
        self.id = id
        tax_id = "Cayman Islands"
        
    def print_address(self):
        print(self.address + "(main office)")
        
class Employee(Company):                    # inheritance of all def of company
    def __init__(self, id):
        super().__init__("OG-285035")        # inheritance of all attributes of company
        self.id = id                         # override company id with employee id
    
    def print_tax_id(self):
        print_stuff()
        print(tax_id)

    

def print_stuff():
    print(GP.id)
    print(simon.id)

if __name__ == "__main__":                   # run this part if execute locally only
    print(__name__)                          # __main__ means executing locally, otherwise it shows the name of the calling module 
    print(tax_id)
    GP = Company("OG-285035")
    print(GP.id)
    print(GP.address)
    GP.print_address()

simon = Employee("123")                      # this part will run when it is run locally or remotely
print(simon.id)
simon.print_tax_id()
simon.print_address()




        
        
