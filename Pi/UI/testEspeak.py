import os
import time
import threading

__author__ = 'Anwar'

class thread1(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            os.system('sudo espeak -q -g 0 -z "" 2>/dev/null')
            time.sleep(0.5)

class thread2(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
             os.system('sudo espeak -k 1 -s 75 -a 300 -p 55 -ven+f2+croak "Nananananananananananananananana" 2>/dev/null')

thread_1 = thread1(1, "T1")
thread_2 = thread2(2, "T2")

thread_1.start()
thread_2.start()
