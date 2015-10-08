import RPi.GPIO as GPIO
import time
from collections import deque


class keypad(object):
    def __init__(self):
        self.hori = [25, 8, 7]
        self.vert = [27, 22, 23, 24]
        self.num_map = [[0,1,2],[3,4,5],[6,7,8],[9,10,11]]
        self.deb_time = 0
        self.HOLD_DELAY = 1
        #press_time = 0
        self.key_map = [['.',',','?','!'], ['a','b','c'], ['d','e','f'],
                ['g','h','i'], ['j','k','l'], ['m','n','o'],
                ['p','q','r','s'], ['t','u','v'], ['w','x','y','z'],
                [''],[' '],[''],
                ['1'], ['2'], ['3'],
                ['4'], ['5'], ['6'],
                ['7'], ['8'], ['9'],
                ['\n'], ['0'], ['']]
        self.num_count = 0
        self.prev_num = -3
        self.num_queue = deque()
        self.out_str = ""
        self.curr_chr = ''

        self.GPIO.setwarnings(False)
        self.GPIO.setmode(GPIO.BCM)

        self.GPIO.setup(self.hori, self.GPIO.OUT, initial=self.GPIO.HIGH)
        self.GPIO.setup(self.vert, self.GPIO.IN)

        for x in range(len(self.vert)):
             self.GPIO.add_event_detect(self.vert[x], self.GPIO.RISING, callback=self.getHori)

    def debounce(self, channel):

        if time.time() - self.deb_time < 0.05 or self.GPIO.input(channel) == self.GPIO.LOW:
            return False
        self.deb_time = time.time()
        return True

    def getHori(self, channel):
        if not self.debounce(channel):
            return

        num_pressed = 0;

        for x in range(len(self.vert)):#disable all interrupts to prevent multiple interrupts running at once
             self.GPIO.remove_event_detect(self.vert[x])
        #self.GPIO.remove_event_detect(channel) #disable interrupts

        for x in range(len(self.hori)):
            self.GPIO.output(self.hori[x], self.GPIO.LOW) #clear horizontals one by one
            if self.GPIO.input(channel) == self.GPIO.LOW: #check if channel is pulled low, if yes the row and col match
                #time.sleep(0.01)
                num_pressed = self.num_map[self.vert.index(channel)][x] #update num_pressed
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # set the horizontal

        hold_timer_start = time.time()
        hold_timer_end = hold_timer_start
        while self.GPIO.input(channel) == self.GPIO.HIGH: #check for hold button
            hold_timer_end = time.time()
            if hold_timer_end - hold_timer_start >= self.HOLD_DELAY:
                break

        if hold_timer_end - hold_timer_start >= self.HOLD_DELAY:
            self.num_queue.put(self.num_map[self.vert.index(channel)][x] + 12) #enq extended  num press
        else:
            self.num_queue.put(self.num_map[self.vert.index(channel)][x]) #enq num press

        for x in range(len(self.vert)): #enable all interrupts
             self.GPIO.add_event_detect(self.vert[x], GPIO.RISING, callback=self.getHori)
        #GPIO.add_event_detect(channel, GPIO.RISING, callback=self.getHori)

    def gen_single(self):
        while self.num_queue.empty():
            pass
        return self.num_queue.empty()

    def gen_string(self):
        while self.num_queue.empty():
            pass
        num = self.num_queue.get()

        # print num
        # [0, 1, 2]       =>       [1, 2, 3]
        # [3, 4, 5]       =>       [4, 5, 6]
        # [6, 7, 8]       =>       [7, 8, 9]
        # [9, 10, 11]     =>       [fwd, space, del]

        if num == 11: #del
            #print "del"
            if num == self.prev_num:
                if len(self.out_str)>0:
                    self.out_str = self.out_str[:len(self.out_str)-1]
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 11 #update keypress history

        elif num == 9: #fwd
            #print "next"
            self.out_str += self.key_map[self.prev_num][self.num_count]
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 9 #update keypress history
        elif num == 23: #clear all
            if num == self.prev_num:
                if len(self.out_str)>0:
                    self.out_str = ""
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 23 #update keypress history
        elif num == 21:
            self.out_str += self.key_map[self.prev_num][self.num_count]
            self.curr_chr = '\n' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 21 #update keypress history
        else:
            if num >= 12:
                if self.prev_num != -3: #first press condition
                    self.out_str += self.key_map[self.prev_num][0]
                self.num_count = 0 #reset count on keymap
                self.prev_num = -3 #update clear history
                self.curr_chr = '' #clear curr_char
            if num != self.prev_num: #normal keys, different num
                #print "diff"
                if self.prev_num != -3: #first press condition
                    self.out_str += self.key_map[self.prev_num][self.num_count]
                self.num_count = 0 #reset count on keymap
                self.prev_num = num #update keypress history
                self.curr_chr = self.key_map[self.prev_num][self.num_count] #update curr_char to new value
            else:
                #print "same"
                self.num_count = (self.num_count + 1) % len(self.key_map[num]) #just update num count
                self.curr_chr = self.key_map[self.prev_num][self.num_count] #update curr_chr to new value

        #print "out str:", out_str