__author__ = 'Pap'
import threading
import my_deque
import pyespeak
import time

class voiceThread(threading.Thread):
    def __init__(self,threadID,threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        global voiceQueue
        global voiceSema
        global speaker

        while True:
            voiceSema.acquire()
            if not voiceQueue.empty():
                item = voiceQueue.popleft()
                if item is not None:
                    speaker.speak(item)
                    print item
            else:
                time.sleep(1)

thread = voiceThread(1, "VQ")
thread.start()

voiceQueue = my_deque.my_deque()
voiceSema = threading.Semaphore(0)
speaker = pyespeak.Speaker()

while True:
    voiceQueue.append(1, time.time())
    voiceSema.release()
    voiceQueue.append_high('a', time.time())
    voiceSema.release()
    voiceQueue.append(2, time.time())
    voiceSema.release()
    voiceQueue.append(3, time.time())
    voiceSema.release()
    voiceQueue.append_high('b', time.time())
    voiceSema.release()
    voiceQueue.append(4, time.time()-10)
    voiceSema.release()
    voiceQueue.append(5, time.time())
    voiceSema.release()
    voiceQueue.append(6, time.time()-10)
    voiceSema.release()
    voiceQueue.append(7, time.time())
    voiceSema.release()
    voiceQueue.append_high('c', time.time())
    voiceSema.release()
    voiceQueue.append(1, time.time())
    voiceSema.release()
    voiceQueue.append(8, time.time())
    voiceSema.release()
    voiceQueue.append(9, time.time())
    voiceSema.release()
    voiceQueue.append(10, time.time())
    voiceSema.release()
    voiceQueue.append(11, time.time())
    voiceSema.release()
    voiceQueue.flush()
    voiceQueue.append(12, time.time())
    voiceSema.release()
    voiceQueue.append(13, time.time()+10)
    voiceSema.release()
    voiceQueue.append(14, time.time())
    voiceSema.release()
    voiceQueue.append_high('d', time.time())
    voiceSema.release()
    voiceQueue.append(15, time.time())
    voiceSema.release()

    time.sleep(20)