import keypad_polling

__author__ = 'Dan'

key_pad = keypad_polling.keypad()

while True:
    key_pad.poll_number()
    print key_pad.out_str, key_pad.curr_chr

print "exit"