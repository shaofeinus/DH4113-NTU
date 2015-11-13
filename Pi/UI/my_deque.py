from collections import deque
import time
__author__ = 'Pap'

class my_deque(object):
    def __init__(self):
        self.queue = deque(maxlen=1)
        self.queue_high = deque()
        self.flush_queue = False
        self.curr_time = 0
        self.curr_speak_time = 0
        self.tolerance = 0.5

    def clear(self):
        self.queue.clear()

    def flush(self):
        self.flush_queue = True

    def empty(self):
        return len(self.queue) is 0 and len(self.queue_high) is 0

    def popleft(self):
        print self.curr_speak_time
        print "NQ:", self.queue
        print "HQ:", self.queue_high
        # if len(self.queue_high) > 0:
        #     item = self.queue_high.popleft()
        #     self.curr_speak_time = item[1]
        #     item = [item[0], True]
        # else:
        isFound = False
        while len(self.queue) > 0:
            item = self.queue.popleft()
            if time.time() - item[1] <= self.tolerance:
                item = [item[0], False]
                isFound = True
        if not isFound:
            return [None, False]
        return item
        # item = self.queue.popleft()
        # if self.curr_speak_time > 0 and item[1] < self.curr_speak_time:
        #     print "None"
        #     return [None, False]
        # self.curr_speak_time = item[1]

        if self.flush_queue:
            self.queue.clear()
            self.flush_queue = False
        return [item[0], False]

    def append(self, item, timeStamp):
        if timeStamp < self.curr_time:
            if self.flush_queue:
                self.queue.clear()
                self.flush_queue = False
            return False
        if self.flush_queue:
            self.queue.clear()
            self.flush_queue = False
        item = [item, timeStamp]
        self.queue.append(item)
        return True

    def append_high(self, item, timeStamp):
        #if self.flush_queue:
        self.queue.clear()
        self.flush_queue = False

        item = [item, timeStamp]
        self.queue_high.append(item)
        return True

    # def appendleft(self, item, timeStamp):
    #     if self.flush_queue:
    #         self.queue.clear()
    #         self.flush_queue = False
    #     item = [item, timeStamp]
    #     self.queue.appendleft(item)
    #
    # def appendleft_high(self, item, timeStamp):
    #     if self.flush_queue:
    #         self.queue.clear()
    #         self.flush_queue = False
    #     item = [item, timeStamp]
    #     self.queue_high.appendleft(item)
    #
    # def pop(self):
    #     if len(self.queue_high) > 0:
    #         item = self.queue_high.pop()
    #         self.curr_speak_time = item[1]
    #     else:
    #         item = self.queue.pop()
    #         if self.curr_speak_time > 0 and item[1] < self.curr_speak_time:
    #             return None
    #
    #     if self.flush_queue:
    #         self.queue.clear()
    #         self.flush_queue = False
    #     return item