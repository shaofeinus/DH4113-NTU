import keypad
import threading

__author__ = 'Anwar'


class UI(object):
    def __init__(self):
        self.key_pad = keypad.keypad();
        self.out_str = ""
        self.curr_chr = ''
        self.run()

    def run(self):
        while True:
            if self.confirm_string():
                print "confirm"
                break
            else:
                print "cancel"

        self.search(out_str)
        return

    def gen_string(self):
        if not self.key_pad.num_queue.empty():
            self.key_pad.num_queue.clear()
        while True:
            self.key_pad.gen_string()
            if self.curr_chr != key_pad.curr_chr:
                self.curr_chr = key_pad.curr_chr
                self.show_output()
                if self.curr_chr == '\n':
                    break
            elif self.out_str != key_pad.out_str:
                self.out_str = key_pad.out_str
                self.show_output()

    def show_output(self):
        print self.out_str, self.curr_chr
        #sound out curr_chr

    def confirm_string(self):
        if not self.key_pad.num_queue.empty():
            self.key_pad.num_queue.clear()
        print "Are you sure?" #sound out confirmation msg
        while True:
            num = self.key_pad.gen_single()
            if num == 0:
                return true
            elif num == 1:
                return 1;

    def search(self):
        print "Search here"
