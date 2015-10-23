import RPi.GPIO as GPIO
import time
import threading
from collections import deque
# from voiceCommands import speak

__author__ = 'Dan'

class keypad(object):
    def __init__(self, chr_queue, voiceSema, speaker):
        #OUTPUT TABLES
        self.hori = [25, 8, 7] #F, E, D
        self.vert = [27, 22, 23, 24] # K, J, I, H
        self.num_map = [[0,1,2],[3,4,5],[6,7,8],[9,10,11]]
        self.key_map = [['.', ', ', '?', '!'], ['a', 'b', 'c'], ['d', 'e', 'f'],
                ['g', 'h', 'i'], ['j', 'k', 'l'], ['m', 'n', 'o'],
                ['p', 'q', 'r', 's'], ['t', 'u', 'v'], ['w', 'x', 'y', 'z'],
                [''],[' '],[''],
                ['1'], ['2'], ['3'],
                ['4'], ['5'], ['6'],
                ['7'], ['8'], ['9'],
                [''], ['0'], ['']]

        #DELAY CONSTANTS
        self.HOLD_DELAY = 0.8
        self.SLEEP_DELAY = 0.02
        self.INACTIVE_DELAY = 1

        #VARIABLES
        self.inactive_delay_start = time.time()
        self.num_count = 0
        self.prev_num = -3
        self.out_str = ""
        self.curr_chr = ''
        self.end_flag = False
        self.str_input = ""
        self.ext_num_input = -1
        self.en_snd = True
        self.chr_queue = chr_queue
        self.voiceSema = voiceSema
        self.speaker = speaker

        #OTHER CONSTANTS
        self.VOID_PRESS = -3

        #GPIO SETUP
        self.GPIO = GPIO
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.hori, self.GPIO.OUT, initial=self.GPIO.LOW) #clear all horizontals
        self.GPIO.setup(self.vert, self.GPIO.IN)

    # def kill_voice_thread(self):
    #     global speakThread
    #     speakThread.stop_thread()
    #     speakThread.join(3)
    #     print "speakThread successfully stopped", (not speakThread.isAlive())

    def toggle_sound(self):
        self.en_snd = not self.en_snd

    def get_input_str(self, prompt):
        while True:
            print prompt
            self.speaker.speak(prompt)
            self.chr_queue.clear()
            self.str_input = self.poll_for_str()
            print "Input is " + self.str_input + ". To confirm, press start. To cancel, press back"

            if self.en_snd:
                self.speaker.speak("Input is " + self.str_input + ". To confirm, press start. To cancel, press back")
            ans = 0
            while True:
                ans = self.poll_for_num()
                if ans == 9 or ans == 11:
                    break
            if ans == 9:
                return self.str_input

    def get_input_ext_num(self, prompt):
        while True:
            print prompt
            self.speaker.speak(prompt)

            self.chr_queue.clear()
            self.ext_num_input = self.poll_for_ext_num()

            print "Input is " + str(self.ext_num_input) + ". To confirm, press start. To cancel, press back"
            if self.en_snd:
                self.speaker.speak("Input is " + str(self.ext_num_input) + ". To confirm, press start. To cancel, press back")
            ans = 0
            while True:
                ans = self.poll_for_num()
                if ans == 9 or ans == 11:
                    break
            if ans == 9:
                return self.ext_num_input

    def get_binary_response(self):
        self.en_snd = False
        while True:
            self.chr_queue.clear()
            userInput = self.poll_for_num()
            if userInput == 9:
                self.en_snd = True
                return False
            elif userInput == 11:
                self.en_snd = True
                return True


    def get_confirmation_binary(self, prompt):
        print str(prompt)
        self.speaker.speak(str(prompt))

        while True:
            self.chr_queue.clear()
            userInput = self.poll_for_num()
            if userInput == 9:
                return

# ===============================NUM POLL==========================================
    def poll_for_num(self):
        x = 0
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)
        #Polling Loops
        while True:
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # test for closed switch by taking turns setting each hori
            num_pressed = -3 # reset num_pressed
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH: # closed switch detected
                    # if self.num_map[y][x] != 9 and self.num_map[y][x] != 11:
                    #     if self.en_snd:
                    #         self.chr_queue.append(self.num_map[y][x])
                    #         self.voiceSema.release()
                    while GPIO.input(self.vert[y]) == GPIO.HIGH:
                        pass
                    return self.num_map[y][x] #update num_pressed
            self.GPIO.output(self.hori[x], self.GPIO.LOW)
            x = (x + 1) % len(self.hori)
            time.sleep(self.SLEEP_DELAY)

        return -1

    def poll_for_num_cond(self):
        x = 0
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)
        #Polling Loops
        while len(self.chr_queue) > 0:
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # test for closed switch by taking turns setting each hori
            num_pressed = -3 # reset num_pressed
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH: # closed switch detected
                    if self.num_map[y][x] != 9 and self.num_map[y][x] != 11:
                        if self.en_snd:
                            self.chr_queue.append(self.num_map[y][x])
                            self.voiceSema.release()
                    while GPIO.input(self.vert[y]) == GPIO.HIGH:
                        pass
                    return self.num_map[y][x] #update num_pressed
            self.GPIO.output(self.hori[x], self.GPIO.LOW)
            x = (x + 1) % len(self.hori)
            time.sleep(self.SLEEP_DELAY)

        return -1

# ===============================Ext Num POLL==========================================
    def poll_for_ext_num(self):
        x = 0
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)

        #Polling Loop
        num_output = ''
        while True:
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # test for closed switch by taking turns setting each hori
            num_pressed = -3 # reset num_pressed
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH: # closed switch detected
                    #print "np:", self.num_map[y][x]

                    # Check hold button condition
                    hold_timer_start = time.time()

                    if self.num_map[y][x] == 11:
                        if self.en_snd:
                            self.chr_queue.append("delete")
                            self.voiceSema.release()
                    elif self.num_map[y][x] != 9:
                        if self.en_snd:
                            if self.num_map[y][x] == 10:
                                self.chr_queue.append(0)
                                self.voiceSema.release()
                            else:
                                self.chr_queue.append(self.num_map[y][x] + 1)
                                self.voiceSema.release()

                    while GPIO.input(self.vert[y]) == GPIO.HIGH:
                        if self.num_map[y][x] == 11 and time.time() - hold_timer_start >= self.HOLD_DELAY:
                            num_output = ""

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

# ===============================STRING POLL==========================================
    def poll_for_str(self):
        # #GPIO tester
        # self.GPIO.output(self.hori[2], self.GPIO.HIGH)
        # while True:
        #     for x in range(len(self.vert)):
        #         print self.GPIO.input(self.vert[x]),
        #     print ""

        x = 0
        self.end_flag = False
        for y in range(len(self.hori)): #check input at each vert
            self.GPIO.output(self.hori[y], self.GPIO.LOW)
        self.out_str = ""
        self.curr_chr = ''
        #Polling loop
        while True:
            self.GPIO.output(self.hori[x], self.GPIO.HIGH) # test for closed switch by taking turns setting each hori
            num_pressed = -3 # reset num_pressed
            for y in range(len(self.vert)): #check input at each vert
                if self.GPIO.input(self.vert[y]) == self.GPIO.HIGH: # closed switch detected
                    num_pressed = self.num_map[y][x] #update num_pressed

                    #Check for hold button condition
                    hold_timer_start = time.time()
                    hold_thres_met = False
                    while GPIO.input(self.vert[y]) == GPIO.HIGH:
                        if time.time() - hold_timer_start >= self.HOLD_DELAY and not hold_thres_met: #checks if button is help sufficiently long
                            num_pressed += 12
                            self.string_gen(num_pressed) #held button press
                            if num_pressed == 21:
                                return self.out_str
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
                return self.out_str

    def string_gen(self, num_pressed):
        ## print num
        # [0, 1, 2]       =>       [1, 2, 3]
        # [3, 4, 5]       =>       [4, 5, 6]
        # [6, 7, 8]       =>       [7, 8, 9]
        # [9, 10, 11]     =>       [fwd, space, del]
        ##print "np:", num_pressed

        if num_pressed == self.VOID_PRESS:
            if self.curr_chr != '':
                self.out_str += self.curr_chr
                if self.en_snd:
                    self.chr_queue.append(str(self.curr_chr))
                    self.voiceSema.release()
            self.curr_chr = ''
            self.prev_num = -3
            self.num_count = 0
        elif num_pressed == 11: #del
            if self.curr_chr == '':
                if len(self.out_str)>0:
                    self.out_str = self.out_str[:len(self.out_str)-1]
            if self.en_snd and (self.curr_chr != '' or len(self.out_str) > 0):
                self.chr_queue.append("delete")
                self.voiceSema.release()
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = -3 #update keypress history
        elif num_pressed == 9: #fwd
            self.out_str += self.curr_chr
            if self.en_snd:
                self.chr_queue.append(self.curr_chr)
                self.voiceSema.release()
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = -3 #update keypress history
        elif num_pressed == 23: #clear all
            self.out_str = ""
            if self.en_snd:
                self.chr_queue.append("clear")
                self.voiceSema.release()
            self.curr_chr = '' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = -3 #update keypress history
        elif num_pressed == 21: #enter string
            self.out_str += self.curr_chr
            self.curr_chr = '\n' #clear curr_chr
            self.num_count = 0 #reset count on key map
            self.prev_num = 21 #update keypress history
            self.end_flag = True
        else:
            if num_pressed >= 12: #hold down keys
                if self.curr_chr != '':
                    self.out_str += self.curr_chr
                    if self.en_snd:
                        self.chr_queue.append(self.curr_chr)
                        self.voiceSema.release()
                self.out_str += self.key_map[num_pressed][0]
                if self.en_snd:
                    self.chr_queue.append(self.key_map[num_pressed][0])
                    self.voiceSema.release()
                self.num_count = 0 #reset count on keymap
                self.prev_num = -3 #update clear history
                self.curr_chr = '' #clear curr_char
            elif num_pressed != self.prev_num: #normal keys, different num
                if self.prev_num != -3: #first press condition
                    self.out_str += self.curr_chr
                    if self.en_snd:
                        self.chr_queue.append(self.curr_chr) ##self.speaker.speak(self.key_map[self.prev_num][self.num_count])
                        self.voiceSema.release()
                self.num_count = 0 #reset count on keymap
                self.prev_num = num_pressed #update keypress history
                self.curr_chr = self.key_map[self.prev_num][self.num_count] #update curr_char to new value
            else: #normal keys, same num
                self.num_count = (self.num_count + 1) % len(self.key_map[num_pressed]) #just update num count
                self.curr_chr = self.key_map[self.prev_num][self.num_count] #update curr_chr to new value
        self.print_intermediate(False) # debugging print

#=============================DEBUG FUNCTIONS================================================
    def print_intermediate(self, debug_mode):
        if debug_mode:
            print "Current String:", self.out_str, "Active Char:", self.curr_chr
        else:
            print self.out_str+self.curr_chr