import RPi.GPIO as GPIO
import time
from collections import deque

deb_time = 0
hori = [25, 8, 7]
vert = [27, 22, 23, 24]
num_map = [[0,1,2],[3,4,5],[6,7,8],[9,10,11]]
HOLD_DELAY = 1
num_queue = deque()

class keypad(object):
    def __init__(self):

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

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(hori, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(vert, GPIO.IN)

        for x in range(len(vert)):
             GPIO.add_event_detect(vert[x], GPIO.RISING, callback=self.getHori)

    def getHori(self, channel):
        # print "deb"
        global deb_time
        if time.time() - deb_time < 0.05 or GPIO.input(channel) == GPIO.LOW: #debounce
            return
        deb_time = time.time()

        global hori
        global vert
        global num_map
        global HOLD_DELAY

        num_pressed = 0;
        # print "enter"
        # for x in range(len(vert)):#disable all interrupts to prevent multiple interrupts running at once
        #     GPIO.remove_event_detect(vert[x])
        GPIO.remove_event_detect(channel) #disable interrupts

        for x in range(len(hori)):
            GPIO.output(hori[x], GPIO.LOW) #clear horizontals one by one
            if GPIO.input(channel) == GPIO.LOW: #check if channel is pulled low, if yes the row and col match
                # time.sleep(0.01)
                num_pressed = num_map[vert.index(channel)][x] #update num_pressed
            GPIO.output(hori[x], GPIO.HIGH) # set the horizontal

        hold_timer_start = time.time()
        hold_timer_end = hold_timer_start
        while GPIO.input(channel) == GPIO.HIGH: #check for hold button
            hold_timer_end = time.time()
            if hold_timer_end - hold_timer_start >= HOLD_DELAY:
                break

        if hold_timer_end - hold_timer_start >= HOLD_DELAY:
            self.num_queue.append(num_pressed + 12) #enq extended  num press
        else:
            self.num_queue.append(num_pressed) #enq num press

        # for x in range(len(vert)): #enable all interrupts
        #      GPIO.add_event_detect(vert[x], GPIO.RISING, callback=self.getHori)
        GPIO.add_event_detect(channel, GPIO.RISING, callback=self.getHori)

    def gen_single(self):
        while len(self.num_queue) == 0:
            pass
        return self.num_queue.popleft()

    def gen_string(self):
        while len(self.num_queue) == 0:
            pass
        num = self.num_queue.popleft()

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
