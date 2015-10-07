import threading
import time
import datetime
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
        # print data[6],
        # print data[7],
        # print data[8],
        # print data[11],
        # print data[12],
        # print data[13],


class LocationDisplayThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.steps = 0;

    def run(self):
        while 1:
            locationTracker.updateLocation()
            print("Total Steps:", locationTracker.getTotalSteps())
            print("distance:", locationTracker.getTotalDistance())
            print("Deviation from N:", locationTracker.getHeadingInDeg())
            print(locationTracker.getLocation())
            print("Height:", locationTracker.getHeightInCM())
            time.sleep(1)


class LocationUpdateThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.totalPedoData = 0
        self.totalCompData = 0
        self.totalBaroData = 0
        self.magX = 1
        self.magY = 1
        self.magZ = 1
        self.timeInMillisComp = 0
        self.accX = 1
        self.accY = 1
        self.accZ = 1
        self.timeInMillisPedo = 0
        self.baroReading = 1
        self.timeInMillisBaro = 0

    def updatePedoData(self):
        if len(data[1]) == 0:
            return
        elif self.totalPedoData == 0:
            self.timeInMillisPedo = data[1].popleft()
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
            locationTracker.updatePedoData(self.accX, self.accY, self.accZ, self.timeInMillisPedo)
            self.totalPedoData = 0

            # print "timeStamp:", self.timeInMillisPedo, "AccX:", self.accX, "AccY:", self.accY, "AccZ:", self.accZ, "time:", datetime.datetime.now()


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
            # Parameter xReading points rightward
            # Parameter yReading points forward
            locationTracker.updateCompassData(xReading=-self.magY, yReading=self.magZ)
            self.totalCompData = 0

            # print "timeStamp:", self.timeInMillisComp, "MagX:", self.magX, "MagY:", self.magY, "time:", datetime.datetime.now()

    def updateBaroData(self):

        if len(data[4]) == 0:
            return
        elif self.totalBaroData == 0:
            self.timeInMillisBaro = data[4].popleft()
            self.totalBaroData += 1
        elif self.totalBaroData == 1:
            self.baroReading = data[4].popleft()
            self.totalBaroData += 1

        if self.totalBaroData == 2:
            # print "timeStamp:", self.timeInMillisBaro, "Reading:", self.baroReading, datetime.datetime.now()
            locationTracker.updateBarometerData(self.baroReading)
            self.totalBaroData = 0

    def run(self):
        while 1:
            self.updatePedoData()
            self.updateCompassData()
            self.updateBaroData()
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
            irFB = data[6]
            irLS = data[7]
            irRS = data[8]
            sonarFT = data[11]
            sonarLS = data[12]
            sonarRS = data[13]

            obstacleLock.acquire()
            obstacle.updateFrontSensorData(sonarFT, irFB)
            obstacle.updateSideSensorData(sonarLS, sonarRS, irLS, irRS)
            obstacleLock.release()
            obstacleStatusLock.acquire()
            obstacleStatus = obstacleDetected
            obstacleStatusLock.release()
            if obstacle.isNewObstacleDetected(obstacleStatus) is True:
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
                obstacle.updateFrontSensorData(sonarFT, irFB)
                obstacle.updateSideSensorData(sonarLS, sonarRS, irLS, irRS)
                obstacleLock.release()
                if obstacle.isFrontObstacleDetected() is True:
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
            irFB = data[6]
            irLS = data[7]
            irRS = data[8]
            sonarFT = data[11]
            sonarLS = data[12]
            sonarRS = data[13]
            obstacleStatusLock.acquire()
            toMonitorObstacle = checkSideObstacle
            obstacleStatusLock.release()
            if toMonitorObstacle == 1:
                obstacleLock.acquire()
                obstacle.updateFrontSensorData(sonarFT, irFB)
                obstacle.updateSideSensorData(sonarLS, sonarRS, irLS, irRS)
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
NUM_QUEUED_ID = 5
NUM_SINGLE_ID = 11

# Data from Arduino
# 1 - accelerometer
# 2 - magnetometer
# 3 - unused
# 4 - barometer
# 5 - unused
# 6 - IR (front bottom)
# 7 - IR (left side)
# 8 - IR (right side)
# 9-10 - unused 
# 11 - sonar (front top) (29 trig 19 echo)
# 12 - sonar (left side) (27 trig 18 echo)
# 13 - sonar (right side) (25 trig 2 echo)

data = [deque() for x in range(NUM_QUEUED_ID)]
data_single = [0 for x in range(NUM_SINGLE_ID)]
data.extend(data_single)

# Obstacle avoidance initialization
obstacle = obstacleAvoidance.obstacleAvoidance()
# 1 if an obstacle avoidance is taking place, else 0
obstacleDetected = 0
checkSideObstacle = 0

# Navigation initialization
navi = fullNavi.fullNavi()
navi.generateFullPath("com1", 2, 1, 5)

# Location tracker initialisation
# TODO: Set initial position
locationTracker = locationTracker.LocationTracker(0, 0, 0)
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
# threads.append(NavigationThread(5, "navigation"))
# threads.append(ObstacleAvoidanceThread(6, "avoid obstacles"))
# threads.append(ObstacleClearedThread(7, "ensure obstacles cleared"))

for thread in threads:
    thread.start()

for threads in threads:
    thread.join()

print("Exiting main thread")
