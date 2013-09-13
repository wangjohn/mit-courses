import Tkinter

if not globals().has_key('__tk_inited'):
    global __tk_inited
    __tk_inited = False

def init():
    global __tk_inited
    if not __tk_inited:
        w = Tkinter.Tk()
        w.withdraw()
    
def setInited():
    global __tk_inited
    __tk_inited = True
