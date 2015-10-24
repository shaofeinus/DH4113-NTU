import timeclass1
import timeclass2

import threading

class thread1(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            timeclass1.act()

class thread2(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            timeclass2.act()

thread_1 = thread1(1, "T1")
thread_2 = thread2(2, "T2")

thread_1.start()
thread_2.start()

__author__ = 'Pap'
