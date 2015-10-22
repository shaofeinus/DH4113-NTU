import keypad_polling
import threading
import pyespeak
from collections import deque

__author__ = 'Dan'

temp = deque()
sema = threading.Semaphore(0)
key_pad = keypad_polling.keypad(temp, sema)


while True:
    print temp
    print key_pad.get_input_str("ENTER EXTENDED NUMBER")
    print temp
print "exit"