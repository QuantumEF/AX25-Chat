from curses import wrapper
from ui import ChatUI
import threading
from kiss import *

destcall = "KN4VHM"
callsign = "KM4YHI"

kiss_iface = kiss_ax25(callsign)
call, message = kiss_iface.recv()
print(call)
print(message)
#kiss_iface.send(destcall,inp)
kiss_iface.s.close()
