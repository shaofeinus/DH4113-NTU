import threading
import Queue
from deadReckoning import pedometer
from deadReckoning import compass
from deadReckoning import locationTracker
# from communication import dataFeeder
from communication import dataFeederDum
import time

__author__ = 'Shao Fei'


class ReceiveDataThread(threading.Thread):

    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            dataFeeder.receive_data(inQueueLock)


class ProcessDataThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            dataFeeder.process_data(data, inQueueLock, dataLock)


class LocationDisplayThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while 1:
            locationTrackerLock.acquire()
            locationTracker.updateLocation()
            print("Total Steps:", locationTracker.getTotalSteps())
            print("Deviation from N:", locationTracker.getHeadingInDeg())
            print(locationTracker.getLocation())
            locationTrackerLock.release()
            time.sleep(1)


class LocationUpdateThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.totalPedoData = 0
        self.totalCompData = 0

    def updatePedoData(self):
        while self.totalPedoData < 4:
            dataLock.acquire()
            if data[1].empty():
                dataLock.release()
                continue
            elif self.totalPedoData == 0:
                timeInMillis = data[1].get()
            elif self.totalPedoData == 1:
                accX = data[1].get()
            elif self.totalPedoData == 2:
                accY = data[1].get()
            elif self.totalPedoData == 3:
                accZ = data[1].get()
            self.totalPedoData += 1
            dataLock.release()

        self.totalPedoData = 0

        #print(timeInMillis, accX, accY, accZ)
        locationTrackerLock.acquire()
        locationTracker.updatePedoData(float(accX), float(accY), float(accZ), int(timeInMillis))
        locationTrackerLock.release()

    def updateCompassData(self):
        while self.totalCompData < 4:
            dataLock.acquire()
            if data[2].empty():
                dataLock.release()
                continue
            elif self.totalCompData == 0:
                timeInMillis = data[2].get()
            elif self.totalCompData == 1:
                magX = data[2].get()
            elif self.totalCompData == 2:
                magY = data[2].get()
            elif self.totalCompData == 3:
                magZ = data[2].get()
            self.totalCompData += 1
            dataLock.release()

        self.totalCompData = 0

        locationTrackerLock.acquire()
        locationTracker.updateCompassData(magY, magZ)
        locationTrackerLock.release()

    def run(self):
        while 1:
            #print("updating")
            self.updatePedoData()
            self.updateCompassData()


# Constants
NUM_ID = 16

# Data from Arduino
data = [Queue.Queue() for x in range(NUM_ID)]

locationTracker = locationTracker.LocationTracker(pedometer.Pedometer(), compass.Compass(), 0, 0)
dataFeeder = dataFeederDum.DataFeederDum()

inQueueLock = threading.Lock()
dataLock = threading.Lock()
locationTrackerLock = threading.Lock()

threads = []

threads.append(ReceiveDataThread(1, "data receiving"))
threads.append(ProcessDataThread(2, "data processing"))
threads.append(LocationUpdateThread(3, "location update"))
threads.append(LocationDisplayThread(4, "location display"))

for thread in threads:
    thread.start()

print("Exiting main thread")

