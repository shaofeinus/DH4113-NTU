import threading
import Queue
import FindMyWay.Pi.deadReckoning.pedometer
import FindMyWay.Pi.deadReckoning.compass
import FindMyWay.Pi.deadReckoning.locationTracker
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
            print("Total Steps:", FindMyWay.Pi.deadReckoning.locationTracker.getTotalSteps())
            print("Deviation from N:", FindMyWay.Pi.deadReckoning.locationTracker.getHeadingInDeg())
            print(FindMyWay.Pi.deadReckoning.locationTracker.getLocation())
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

            FindMyWay.Pi.deadReckoning.locationTracker.updatePedoData(float(accX), float(accY), float(accZ), int(timeInMillis))

            line = f.readline()

        lock.release()
        return

    @staticmethod
    def updateCompassData():
        magX = random.randint(-1000, 1000)
        magY = random.randint(-1000, 1000)

        lock.acquire()
        FindMyWay.Pi.deadReckoning.locationTracker.updateCompassData(magX, magY)
        lock.release()

        return

    def run(self):
        while 1:
            self.updatePedoData()
            self.updateCompassData()

            lock.acquire()
            FindMyWay.Pi.deadReckoning.locationTracker.updateLocation()
            lock.release()

            time.sleep(0.5)

dataQueue = queue.Queue(1)

locationTracker = FindMyWay.Pi.deadReckoning.locationTracker.LocationTracker(FindMyWay.Pi.deadReckoning.pedometer.Pedometer(), FindMyWay.Pi.deadReckoning.compass.Compass(), 0, 0)

lock = threading.Lock()

threads = []

threads.append(DataFeedingThread(1, "data feeding"))
threads.append(LocationUpdateThread(2, "location update"))
threads.append(LocationDisplayThread(3, "location display"))

for thread in threads:
    thread.start()

print("Exiting main thread")

