import threading
import queue
import pedometer
import compass
import locationTracker
import random
import time

__author__ = 'Shao Fei'


class DataFeedingThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while 1:
            lock.acquire()
            if dataQueue.empty():
                dataQueue.put('testdata/pedo_testdata.csv')
            lock.release()
            time.sleep(0.5)


class LocationDisplayThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while 1:
            lock.acquire()
            print("Total Steps:", locationTracker.getTotalSteps())
            print("Deviation from N:", locationTracker.getHeadingInDeg())
            print(locationTracker.getLocation())
            lock.release()
            time.sleep(1)


class LocationUpdateThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    @staticmethod
    def updatePedoData():
        lock.acquire()
        if dataQueue.empty():
            lock.release()
            return
        dataDir = dataQueue.get()
        lock.release()

        f = open(dataDir, 'r')
        line = f.readline()

        lock.acquire()
        while line:
            values = line.split(',')
            timeInMillis = values[0]
            accX = values[1]
            accY = values[2]
            accZ = values[3]

            locationTracker.pedometer.updateWindow(int(accX), int(accY), int(accZ), int(timeInMillis))

            line = f.readline()

        lock.release()
        return

    @staticmethod
    def updateCompassData():
        magX = random.randint(-1000, 1000)
        magY = random.randint(-1000, 1000)

        lock.acquire()
        locationTracker.compass.updateReading(magX, magY)
        lock.release()

        return

    def run(self):
        while 1:
            self.updatePedoData()
            self.updateCompassData()

            lock.acquire()
            locationTracker.updateLocation()
            lock.release()

            time.sleep(0.5)

dataQueue = queue.Queue(1)
locationTracker = locationTracker.LocationTracker(pedometer.Pedometer(), compass.Compass(), 0, 0)

lock = threading.Lock()

threads = []

threads.append(DataFeedingThread(1, "data feeding"))
threads.append(LocationUpdateThread(2, "location update"))
threads.append(LocationDisplayThread(3, "location display"))

for thread in threads:
    thread.start()

print("Exiting main thread")

