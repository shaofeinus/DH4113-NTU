import time
import Queue

__author__ = 'Shao Fei'


class DataFeederDum:

    PEDO_INTERVAL = 300         # ms

    def __init__(self):
        self.in_queue = Queue.Queue()
        self.startTime = 0

    def receive_data(self, inQueueLock):

        inQueueLock.acquire()

        # Pedometer
        self.in_queue.put(1)        # Dev id
        self.in_queue.put(self.startTime)       # Time
        if self.startTime % self.PEDO_INTERVAL != 0:
            self.in_queue.put(1000)
            self.in_queue.put(1000)
            self.in_queue.put(1000)
        else:
            self.in_queue.put(2000)
            self.in_queue.put(2000)
            self.in_queue.put(1800)

        # Compass
        self.in_queue.put(2)        # Dev id
        self.in_queue.put(self.startTime)       # Time

        self.in_queue.put(2000)
        self.in_queue.put(0)
        self.in_queue.put(2000)

        inQueueLock.release()

        self.startTime += 10

        time.sleep(0.01)

    def process_data(self, data, inQueueLock, dataLock):

        printArray = []

        while self.in_queue.empty():
            continue

        inQueueLock.acquire()
        devId = self.in_queue.get()
        inQueueLock.release()

        printArray.append(devId)

        while self.in_queue.empty():
            continue

        # Time stamp
        inQueueLock.acquire()
        timeStamp = self.in_queue.get()
        inQueueLock.release()
        printArray.append(timeStamp)

        dataLock.acquire()
        data[devId].put(timeStamp)
        dataLock.release()

        # x, y, z data
        while self.in_queue.empty():
            continue

        inQueueLock.acquire()
        x = self.in_queue.get()
        inQueueLock.release()
        printArray.append(x)

        dataLock.acquire()
        data[devId].put(x)
        dataLock.release()

        while self.in_queue.empty():
            continue

        inQueueLock.acquire()
        y = self.in_queue.get()
        inQueueLock.release()
        printArray.append(y)

        dataLock.acquire()
        data[devId].put(y)
        dataLock.release()

        while self.in_queue.empty():
            continue

        inQueueLock.acquire()
        z = self.in_queue.get()
        inQueueLock.release()
        printArray.append(z)

        dataLock.acquire()
        data[devId].put(z)
        dataLock.release()