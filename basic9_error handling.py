# -*- coding: utf-8 -*-
# list of exception type:
# https://docs.python.org/3/library/exceptions.html#exception-hierarchy

import logging

def error1():                                           
    try:
        input_box = int(input("Please input a number: "))
        print("Try: 10/number")
        r=10/input_box                                   # exception when input 0 or non-number
        print("Result: ", r)                             # not run this if exception

    except ValueError as e:                              # if non-number
        print("ValueError: ", e)
                                    # it records exception and continue the script
    
    except ZeroDivisionError as e:                       # if 0
        print("ZeroDivisionError: ", e)
        
    
    else:                                                # if no error
        print("No Error")
    
    finally:                                             # must run whether there is exception
        print("Continue the script")

def error2():                                            # more recommended than error1
    try:
        input_box = int(input("Please input a number: "))
        print("Try: 10/number")
        r=10/input_box                                   # exception when input 0 or non-number
        print("Result: ", r)                             # not run this if exception

    except ValueError as e:                              # if non-number
        logging.exception(e)                             # it records exception and continue the script
    
    except ZeroDivisionError as e:                       # if 0   
        logging.exception(e)
    
    else:                                                # if no error
        print("No Error")
    
    print("Continue the script")                         # continue regardless of the error

def error_handling():
    input_box = int(input("Please input a number: "))
    if input_box == 0:
        raise ZeroDivisionError("Please input a non-zero number")
    return 10/input_box
    
#print(error_handling())
#error1()
error2()