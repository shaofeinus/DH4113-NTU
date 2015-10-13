import RPi.GPIO as GPIO
import time
from collections import deque
__author__ = 'Dan'

class keypad(object):
    def __init__(self):
        self.deb_time = 0
        self.hori = [25, 8, 7] #F, E, D
        self.vert = [27, 22, 23, 24] # K, J, I, H
        self.num_map = [[0,1,2],[3,4,5],[6,7,8],[9,10,11]]
        self.HOLD_DELAY = 0.8
        self.SLEEP_DELAY = 0.02
        self.INACTIVE_DELAY = 1
        self.VOID_PRESS = -3
        self.inactive_delay_start = time.time()
        # self.num_queue = deque()
        self.key_map = [['.', ', ', '?', '!'], ['a', 'b', 'c'], ['d', 'e', 'f'],
                ['g', 'h', 'i'], ['j', 'k', 'l'], ['m', 'n', 'o'],
                ['p', 'q', 'r', 's'], ['t', 'u', 'v'], ['w', 'x', 'y', 'z'],
                [''],[' '],[''],
                ['1'], ['2'], ['3'],
                ['4'], ['5'], ['6'],
                ['7'], ['8'], ['9'],
                [''], ['0'], ['']]
        self.num_count = 0
        self.prev_num = -3
        self.out_str = ""
        self.curr_chr = ''
        self.end_flag = False

        self.GPIO = GPIO
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(self.GPIO.BCM)

        self.GPIO.setup(self.hori, self.GPIO.OUT, initial=self.GPIO.LOW) #clear all horizontals
        self.GPIO.setup(self.vert, self.GPIO.IN)

    def get_input_str(self, prompt):
        while True:
            print prompt
            user_input = self.poll_for_str()
            print "Is \"", user_input, "\" correct?"
            print "Start = YES, # = NO"
            ans = 0
            while True:
                ans = self.poll_for_num()
                if ans == 9 or ans == 11:
                    break
            if ans == 9:
                return user_input

    def get_input_ext_num(self, prompt):
        while True:
            print prompt
            user_input = self.poll_for_ext_num()
            if user_input == -1:
                return -1
            print "Is \"", str(user_input), "\" correct?"
            print "Start = YES, # = NO"
            ans = 0
            while True:
                ans = self.poll_for_num()
                if ans == 9 or ans == 11:
                    break
            if ans == 9:
                return user_input

    def poll_for_num(self):
        x = 0
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)
#=====================================polling loops=================================================
        while True:
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # test for closed switch by taking turns setting each hori
            num_pressed = -3 # reset num_pressed
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH: # closed switch detected
                    while GPIO.input(self.vert[y]) == GPIO.HIGH:
                        pass
                    return self.num_map[y][x] #update num_pressed
            self.GPIO.output(self.hori[x], self.GPIO.LOW)
            x = (x + 1) % len(self.hori)
            time.sleep(self.SLEEP_DELAY)

        return -1

    def poll_for_ext_num(self):
        x = 0
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)
#=====================================polling loops=================================================
        num_output = ''
        while True:
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # test for closed switch by taking turns setting each hori
            num_pressed = -3 # reset num_pressed
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH: # closed switch detected
                    hold_timer_start = time.time()
                    while GPIO.input(self.vert[y]) == GPIO.HIGH:
                        if self.num_map[y][x] == 11 and time.time() - hold_timer_start >= self.HOLD_DELAY:
                            return -1
                    print "np:", self.num_map[y][x]
                    if self.num_map[y][x] == 11:
                        if len(num_output) > 0: #del
                            num_output = num_output[:len(num_output)-1]
                    elif self.num_map[y][x] == 9:
                        if len(num_output) > 0: #start
                            return int(num_output)
                    elif self.num_map[y][x] == 10: #0
                        num_output += '0'
                    else:
                        num_output += str(self.num_map[y][x] + 1) #update num_pressed
                    print num_output
            self.GPIO.output(self.hori[x], self.GPIO.LOW)
            x = (x + 1) % len(self.hori)
            time.sleep(self.SLEEP_DELAY)

        return -1

    def poll_for_str(self):
        x = 0
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)
        self.out_str = ""
        self.curr_chr = ''
#=====================================polling loops=================================================
        while True:
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # test for closed switch by taking turns setting each hori
            num_pressed = -3 # reset num_pressed
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH: # closed switch detected
                    num_pressed = self.num_map[y][x] #update num_pressed
                    #print num_pressed + 1
# ==============================check for hold button condition=====================================
                    hold_timer_start = time.time()
                    hold_thres_met = False
                    while GPIO.input(self.vert[y]) == GPIO.HIGH:
                        if time.time() - hold_timer_start >= self.HOLD_DELAY and not hold_thres_met: #checks if button is help sufficiently long
                            num_pressed += 12
                            self.string_gen(num_pressed) #held button press
                            hold_thres_met = True

                    if num_pressed != -3 and not hold_thres_met: #normal button press
                        self.string_gen(num_pressed)

                    self.inactive_delay_start = time.time()
                    break
            self.GPIO.output(self.hori[x], self.GPIO.LOW)
            x = (x + 1) % len(self.hori)
            time.sleep(self.SLEEP_DELAY)

            #checks if there is an active character, appends character after specified timeout
            if self.curr_chr != '' and time.time() - self.inactive_delay_start >= self.INACTIVE_DELAY:
                self.string_gen(self.VOID_PRESS)
                self.inactive_delay_start = time.time()

            if self.end_flag:
                self.end_flag = False
                return self.out_str

    def string_gen(self, num_pressed):
        # print num
        # [0, 1, 2]       =>       [1, 2, 3]
        # [3, 4, 5]       =>       [4, 5, 6]
        # [6, 7, 8]       =>       [7, 8, 9]
        # [9, 10, 11]     =>       [fwd, space, del]
        print "np:", num_pressed
        if num_pressed == self.VOID_PRESS:
            self.out_str += self.curr_chr
            self.curr_chr = ''
            self.prev_num = -3
            self.num_count = 0
        elif num_pressed == 11: #del
            #print "del"
            if self.curr_chr == '':
                if len(self.out_str)>0:
                    self.out_str = self.out_str[:len(self.out_str)-1]
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 11 #update keypress history

        elif num_pressed == 9: #fwd
            #print "next"
            self.out_str += self.key_map[self.prev_num][self.num_count]
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 9 #update keypress history
        elif num_pressed == 23: #clear all
            self.out_str = ""
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 23 #update keypress history
        elif num_pressed == 21:
            self.out_str += self.key_map[self.prev_num][self.num_count]
            self.curr_chr = '\n' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 21 #update keypress history
            self.end_flag = True
            return
        else:
            if num_pressed >= 12: #hold down keys
                if self.curr_chr != '':
                    self.out_str += self.curr_chr
                self.out_str += self.key_map[num_pressed][0]
                self.num_count = 0 #reset count on keymap
                self.prev_num = -3 #update clear history
                self.curr_chr = '' #clear curr_char
            elif num_pressed != self.prev_num: #normal keys, different num
                #print "diff"
                if self.prev_num != -3: #first press condition
                    self.out_str += self.key_map[self.prev_num][self.num_count]
                self.num_count = 0 #reset count on keymap
                self.prev_num = num_pressed #update keypress history
                self.curr_chr = self.key_map[self.prev_num][self.num_count] #update curr_char to new value
            else:
                #print "same"
                self.num_count = (self.num_count + 1) % len(self.key_map[num_pressed]) #just update num count
                self.curr_chr = self.key_map[self.prev_num][self.num_count] #update curr_chr to new value
        self.print_intermediate(False) #print for debugging

#=============================DEBUG FUNCTIONS================================================
    def print_intermediate(self, debug_mode):
        if debug_mode:
            print "Current String:", self.out_str, "Active Char:", self.curr_chr
        else:
            print self.out_str+self.curr_chr