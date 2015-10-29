__author__ = 'Pap'

import time
import threading
from collections import deque
# from voiceCommands import speak

__author__ = 'Dan'

class keypad(object):
    def __init__(self, chr_queue, voiceSema, speaker):
        #OUTPUT TABLES
        self.chr_queue = chr_queue
        self.voiceSema = voiceSema
        self.speaker = speaker

    def toggle_sound(self):
        self.en_snd = not self.en_snd

    def get_input_str(self, prompt):
        print prompt
        return input("Enter string: ")

    def get_input_ext_num(self, prompt):
        print prompt
        return input("Enter Number: ")

    def get_binary_response(self):
        while True:
            chr = input("Enter \'y\' for yes, \'n\' for no")
            if chr == 'y':
                return False
            elif chr == 'n':
                return True

    def get_confirmation_binary(self, prompt):
        print str(prompt)
        input("Press enter to continue: ")

    def poll_for_num_timed(self):
        while True:
            chr = input("Enter \'y\' to skip UI, \'n\' to continue")
            if chr == 'y':
                return False
            elif chr == 'n':
                return True

#=============================DEBUG FUNCTIONS================================================
    def print_intermediate(self, debug_mode):
        if debug_mode:
            print "Current String:", self.out_str, "Active Char:", self.curr_chr
        else:
            print self.out_str+self.curr_chr