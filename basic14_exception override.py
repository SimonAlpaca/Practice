import sys
import traceback
from IPython.core.interactiveshell import InteractiveShell

def exception_override(code = None, **running_compiled_code):
    traceback_lines = traceback.format_exception(*sys.exc_info())
    del traceback_lines[1]
    print("testing")
    message = ''.join(traceback_lines)

    sys.stderr.write(message)


InteractiveShell.showtraceback = exception_override 

raise IOError

'''
tkinter has its callback for exception

import tk
import traceback

def exception_override(self, *args):
    err = traceback.format_exception(*args)
    for err_line in err:
        print(err_line)

tk.Tk.report_callback_exception = exception_override 
'''        

'''
sys.excepthook can no longer work
'''