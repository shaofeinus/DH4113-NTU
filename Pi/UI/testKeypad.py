import keypad_polling

__author__ = 'Dan'

key_pad = keypad_polling.keypad()

while True:
    print key_pad.get_input_str("ENTER STRING")
print "exit"