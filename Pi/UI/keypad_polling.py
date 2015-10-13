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
        self.HOLD_DELAY = 1
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
        self.num_queue = deque()
        self.out_str = ""
        self.curr_chr = ''

        self.GPIO = GPIO
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(self.GPIO.BCM)

        self.GPIO.setup(self.hori, self.GPIO.OUT, initial=self.GPIO.LOW) #clear all horizontals
        self.GPIO.setup(self.vert, self.GPIO.IN)

    def poll_number(self):
        x = 0
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)
        self.out_str = ""
        self.curr_chr = ''
        while True:
#=====================================polling loops=================================================
            self.GPIO.output(self.hori[x], self.GPIO.HIGH)
            num_pressed = -3
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH:
                    num_pressed = self.num_map[y][x] #update num_pressed
                    print num_pressed + 1
# ==============================check for hold button condition=====================================
                    hold_timer_start = time.time()
                    hold_timer_end = hold_timer_start
                    while False and GPIO.input(self.vert[y]) == GPIO.HIGH:
                        hold_timer_end = time.time()
                    if hold_timer_end - hold_timer_start >= self.HOLD_DELAY:
                        num_pressed += 12
                    if num_pressed != -3:
                        self.string_gen(num_pressed)

                    print self.out_str, self.curr_chr
                    break
            self.GPIO.output(self.hori[x], self.GPIO.LOW)
            x = (x + 1) % len(self.hori)
            time.sleep(0.05)

    def string_gen(self, num_pressed):
        # print num
        # [0, 1, 2]       =>       [1, 2, 3]
        # [3, 4, 5]       =>       [4, 5, 6]
        # [6, 7, 8]       =>       [7, 8, 9]
        # [9, 10, 11]     =>       [fwd, space, del]

        if num_pressed == 11: #del
            #print "del"
            if num_pressed == self.prev_num:
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
            return
        else:
            if num_pressed >= 12: #hold down keys
                self.out_str += self.key_map[self.prev_num][0]
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
