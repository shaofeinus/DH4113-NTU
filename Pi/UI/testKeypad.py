import keypad_polling
from collections import deque

__author__ = 'Dan'

temp = deque()

key_pad = keypad_polling.keypad(temp)

while True:
    print temp
    print key_pad.get_input_ext_num("ENTER EXTENDED NUMBER")
    print temp
print "exit"