import threading
import time
import datetime
from deadReckoning import pedometer
from deadReckoning import compass
from deadReckoning import locationTracker
from navigation import fullNavi
from navigation import obstacleAvoidance
from communication import dataFeeder
from communication import dataFeederDum
from collections import deque


__author__ = 'Shao Fei'


class ReceiveDataThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            dataFeeder.receive_data()


class ProcessDataThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            dataFeeder.process_data(data)


class LocationDisplayThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while 1:
            locationTracker.updateLocation()
            print("Total Steps:", locationTracker.getTotalSteps())
            print("Deviation from N:", locationTracker.getHeadingInDeg())
            print(locationTracker.getLocation())
            time.sleep(1)


class LocationUpdateThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.totalPedoData = 0
        self.totalCompData = 0
        self.magX = 1
        self.magY = 1
        self.magZ = 1
        self.timeInMillisComp = 0
        self.accX = 1
        self.accY = 1
        self.accZ = 1
        self.timeInMillisPedo = 0

    def updatePedoData(self):
        if len(data[1]) == 0:
            return
        elif self.totalPedoData == 0:
            self.timeInMillisComp = data[1].popleft()
            self.totalPedoData += 1
        elif self.totalPedoData == 1:
            self.accX = data[1].popleft()
            self.totalPedoData += 1
        elif self.totalPedoData == 2:
            self.accY = data[1].popleft()
            self.totalPedoData += 1
        elif self.totalPedoData == 3:
            self.accZ = data[1].popleft()
            self.totalPedoData += 1

        if self.totalPedoData == 4:
            locationTracker.updatePedoData(float(self.accX), float(self.accY), float(self.accZ),
                                           int(self.timeInMillisPedo))
            # print "timeStamp:", self.timeInMillisComp, "AccX:", self.accX, "AccY:", self.accY, "AccZ:", self.accZ, "time:", datetime.datetime.now()
            self.totalPedoData = 0

    def updateCompassData(self):

        if len(data[2]) == 0:
            return
        elif self.totalCompData == 0:
            self.timeInMillisComp = data[2].popleft()
            self.totalCompData += 1
        elif self.totalCompData == 1:
            self.magX = data[2].popleft()
            self.totalCompData += 1
        elif self.totalCompData == 2:
            self.magY = data[2].popleft()
            self.totalCompData += 1
        elif self.totalCompData == 3:
            self.magZ = data[2].popleft()
            self.totalCompData += 1

        if self.totalCompData == 4:
            # print "timeStamp:", self.timeInMillisComp, "MagX:", self.magX, "MagY:", self.magY, "time:", datetime.datetime.now()
            locationTracker.updateCompassData(self.magY, self.magX)
            self.totalCompData = 0

    def run(self):
        while 1:
            self.updatePedoData()
            self.updateCompassData()
            continue


class NavigationThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        global obstacleDetected
        global checkSideObstacle
        while 1:
            locationTrackerLock.acquire()
            curX = locationTracker.getXCoord() * 100
            curY = locationTracker.getYCoord() * 100
            heading = locationTracker.getHeadingInDeg()
            locationTrackerLock.release()
            if obstacleDetected == 1 or checkSideObstacle == 1:
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
        while 1:
            if (len(data[5]) == 0 or len(data[6]) == 0 or len(data[10]) == 0 or
                    len(data[11]) == 0 or len(data[12]) == 0 or len(data[13]) == 0 or
                    len(data[14]) == 0):
                return

            irL = data[5].popleft()
            irR = data[6].popleft()
            sonarTL = data[10].popleft()
            sonarTR = data[11].popleft()
            sonarC = data[12].popleft()
            sonarLS = data[13].popleft()
            sonarRS = data[14].popleft()

            obstacleLock.acquire()
            obstacle.updateFrontSonarData(sonarTL, sonarTR, sonarC)
            obstacle.updateIRData(irL, irR)
            obstacleLock.release()
            obstacleStatusLock.acquire()
            obstacleStatus = obstacleDetected
            obstacleStatusLock.release()
            if obstacle.isNewObstacleDetected(obstacleStatus) == 1:
                obstacleStatusLock.acquire()
                obstacleDetected = 1
                checkSideObstacle = 0
                obstacleStatusLock.release()
                obstacle.vibrateMotors()

            obstacleStatusLock.acquire()
            obstacleStatus = obstacleDetected
            obstacleStatusLock.release()
            if obstacleStatus == 1:
                obstacleLock.acquire()
                obstacle.updateFrontSonarData(sonarTL, sonarTR, sonarC)
                obstacle.updateIRData(irL, irR)
                obstacle.updateSideSonarData(sonarLS, sonarRS)
                obstacleLock.release()
                if obstacle.isFrontObstacleDetected() == 1:
                    obstacle.turnFromObstacle()
                else:
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
        global checkSideObstacle
        while 1:
            if (len(data[5]) == 0 or len(data[6]) == 0 or len(data[10]) == 0 or
                    len(data[11]) == 0 or len(data[12]) == 0 or len(data[13]) == 0 or
                    len(data[14]) == 0):
                return

            irL = data[5].popleft()
            irR = data[6].popleft()
            sonarTL = data[10].popleft()
            sonarTR = data[11].popleft()
            sonarC = data[12].popleft()
            sonarLS = data[13].popleft()
            sonarRS = data[14].popleft()
            obstacleStatusLock.acquire()
            toMonitorObstacle = checkSideObstacle
            obstacleStatusLock.release()
            if toMonitorObstacle == 1:
                obstacleLock.acquire()
                obstacle.updateFrontSonarData(sonarTL, sonarTR, sonarC)
                obstacle.updateIRData(irL, irR)
                obstacle.updateSideSonarData(sonarLS, sonarRS)
                obstacleLock.release()
                if obstacle.checkObstacleCleared() == 1:
                    obstacleStatusLock.acquire()
                    checkSideObstacle = 0
                    print "obstacle cleared"
                    obstacleStatusLock.release()
            time.sleep(0.5)


# --------------------- START OF MAIN ----------------------- #

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
data = [deque() for x in range(NUM_ID)]

# Obstacle avoidance initialization
obstacle = obstacleAvoidance.obstacleAvoidance()
# 1 if an obstacle avoidance is taking place, else 0
obstacleDetected = 0
checkSideObstacle = 0

# Navigation initialization
navi = fullNavi.fullNavi()
navi.generateFullPath(0, 1, 5)

# Location tracker initialisation
# TODO: Set initial position
locationTracker = locationTracker.LocationTracker(pedometer.Pedometer(), compass.Compass(), 0, 0)
dataFeeder = dataFeeder.DataFeeder()

# Locks for various variables
locationTrackerLock = threading.Lock()
obstacleLock = threading.Lock()
obstacleStatusLock = threading.Lock()

# List of threads
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
