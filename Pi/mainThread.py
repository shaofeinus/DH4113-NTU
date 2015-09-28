import threading
import Queue
from deadReckoning import pedometer
from deadReckoning import compass
from deadReckoning import locationTracker
from navigation import fullNavi
from navigation import obstacleAvoidance
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

class NavigationThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while (1):
            locationTrackerLock.acquire()
            curX = locationTracker.getXCoord() * 100
            curY = locationTracker.getYCoord() * 100
            heading = locationTracker.getHeadingInDeg()
            locationTrackerLock.release()
            if((obstacleDetected == 1) or (checkSideObstacle == 1)) :
                time.sleep(0.5)
                continue
            navi.updateCurLocation(curX, curY, heading)
            navi.fullNavigate()
            time.sleep(1)


class ObstacleAvoidanceThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        global obstacleDetected
        global checkSideObstacle
        while (1):
            dataLock.acquire()
            if (data[5].empty() or data[6].empty() or data[10].empty() or
                data[11].empty() or data[12].empty() or data[13].empty() or
                data[14].empty()) :
                dataLock.release()
                continue
            irL = data[5].get()
            irR = data[6].get()
            sonarTL = data[10].get()
            sonarTR = data[11].get()
            sonarC = data[12].get()
            sonarLS = data[13].get()
            sonarRS = data[14].get()
            dataLock.release()
            obstacleLock.acquire()
            obstacle.updateFrontSonarData(sonarTL, sonarTR, sonarC)
            obstacle.updateIRData(irL, irR)
            obstacleLock.release()
            obstacleStatusLock.acquire()
            obstacleStatus = obstacleDetected
            obstacleStatusLock.release()
            if obstacle.isNewObstacleDetected(obstacleStatus) == 1 :
                obstacleStatusLock.acquire()
                obstacleDetected = 1
                checkSideObstacle = 0
                obstacleStatusLock.release()
                obstacle.vibrateMotors()
                
            obstacleStatusLock.acquire()
            obstacleStatus = obstacleDetected
            obstacleStatusLock.release()
            if obstacleStatus == 1 :
                obstacleLock.acquire()
                obstacle.updateFrontSonarData(sonarTL, sonarTR, sonarC)
                obstacle.updateIRData(irL, irR)
                obstacle.updateSideSonarData(sonarLS, sonarRS)
                obstacleLock.release()
                if obstacle.isFrontObstacleDetected() == 1 :
                    obstacle.turnFromObstacle()
                else :
                    obstacle.turnOffMotors()
                    obstacleStatusLock.acquire()
                    obstacleDetected = 0
                    checkSideObstacle = 1
                    obstacleStatusLock.release()
            time.sleep(0.1)

class ObstacleClearedThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while (1):
            dataLock.acquire()
            if (data[5].empty() or data[6].empty() or data[10].empty() or
                data[11].empty() or data[12].empty() or data[13].empty() or
                data[14].empty()) :
                dataLock.release()
                continue
            irL = data[5].get()
            irR = data[6].get()
            sonarTL = data[10].get()
            sonarTR = data[11].get()
            sonarC = data[12].get()
            sonarLS = data[13].get()
            sonarRS = data[14].get()
            dataLock.release()
            obstacleStatusLock.acquire()
            toMonitorObstacle = checkSideObstacle
            obstacleStatusLock.release()
            if toMonitorObstacle == 1 :
                obstacleLock.acquire()
                obstacle.updateFrontSonarData(sonarTL, sonarTR, sonarC)
                obstacle.updateIRData(irL, irR)
                obstacle.updateSideSonarData(sonarLS, sonarRS)
                obstacleLock.release()
                if obstacle.checkObstacleCleared() == 1 :
                    obstacleStatusLock.acquire()
                    checkSideObstacle = 0
                    print "obstacle cleared"
                    obstacleStatusLock.release()
            time.sleep(0.5)



# Obstacle avoidance initialization
obstacle = obstacleAvoidance.obstacleAvoidance()
# 1 if an obstacle avoidance is taking place, else 0
obstacleDetected = 0
checkSideObstacle = 0

# Navigation initialization
navi = fullNavi.fullNavi()
navi.generateFullPath(0, 1, 5)



# Constants
NUM_ID = 16

# Data from Arduino
# 1 - accelerometer
# 2 - magnetometer
# 3 - unused
# 4 - barometer
# 5 - IR (left)
# 6 - IR (right)
# 7-9 - unused
# 10 - sonar (front top left)
# 11 - sonar (front top right)
# 12 - sonar (front center)
# 13 - sonar (left shoulder)
# 14 - sonar (right shoulder)
data = [Queue.Queue() for x in range(NUM_ID)]

locationTracker = locationTracker.LocationTracker(pedometer.Pedometer(), compass.Compass(), 0, 0)
dataFeeder = dataFeederDum.DataFeederDum()

inQueueLock = threading.Lock()
dataLock = threading.Lock()
locationTrackerLock = threading.Lock()
obstacleLock = threading.Lock()
obstacleStatusLock = threading.Lock()

threads = []

threads.append(ReceiveDataThread(1, "data receiving"))
threads.append(ProcessDataThread(2, "data processing"))
threads.append(LocationUpdateThread(3, "location update"))
threads.append(LocationDisplayThread(4, "location display"))
threads.append(NavigationThread(5, "navigation"))
threads.append(ObstacleAvoidanceThread(6, "avoid obstacles"))
threads.append(ObstacleClearedThread(7, "ensure obstacles cleared"))

for thread in threads:
    thread.start()

print("Exiting main thread")

