import keypad_polling
import UISpeaker
import my_deque
import threading

__author__ = 'Dan'

# temp = deque()
sema = threading.Semaphore(0)
q =  my_deque.my_deque()
speaker = UISpeaker.UI_Speaker()
key_pad = keypad_polling.keypad(q, sema, speaker)


while True:
    print key_pad.get_input_ext_num("ENTER EXTENDED NUMBER")
print "exit"