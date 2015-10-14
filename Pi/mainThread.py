import threading
import time
import math
import datetime
from deadReckoning import compassCalibrator
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
            dataInLock.acquire()
            # print 'receiving'
            dataFeeder.receive_data()
            dataInLock.release()


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


class CalibrationThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

        self.calibrator = locationTracker.compass.calibrator
        self.isDone = {'tilt': False, 'nOffset': False}

        self.accX = 0
        self.accY = 0
        self.accZ = 0
        self.totalAccData = 0
        self.magX = 0
        self.magY = 0
        self.magZ = 0
        self.totalMagData = 0

    def run(self):

        magXrange = (-4328, 5605)
        magYRange = (-5096, 5002)
        magZRange = (-4618, 4655)
        self.calibrator.inputManualRange(magZRange, magYRange, magXrange)

        dataInLock.acquire()
        validInput = False
        while not validInput:
            userInput = raw_input("Press enter to calibrate? y/n ")
            if userInput == 'y':
                validInput = True
            elif userInput == 'n':
                dataInLock.release()
                return
            else:
                print 'Enter y/n'

        for i in range(0, 5):
            print 5 - i
            time.sleep(1)

        print 'Calibrating'
        dataFeeder.serialPort.flushInput()
        dataFeeder.serialPort.flushOutput()
        dataInLock.release()

        while not self.isDone['tilt']:
            self.calibrateTilt()

        while not self.isDone['nOffset']:
            self.calibrateOffset()

        dataInLock.acquire()
        raw_input('Your are ' + str(self.calibrator.getNOffsetAngle() / (2 * math.pi) * 360) + ' from N.')
        dataFeeder.serialPort.flushInput()
        dataFeeder.serialPort.flushOutput()
        dataInLock.release()

    def calibrateTilt(self):
        if len(data[1]) == 0:
            return
        elif self.totalAccData == 0:
            data[1].popleft()
            self.totalAccData += 1
        elif self.totalAccData == 1:
            self.accX = data[1].popleft()
            self.totalAccData += 1
        elif self.totalAccData == 2:
            self.accY = data[1].popleft()
            self.totalAccData += 1
        elif self.totalAccData == 3:
            self.accZ = data[1].popleft()
            self.totalAccData += 1

        if self.totalAccData == 4:
            # x points to front
            # y points to left
            # z points to up
            self.calibrator.calibrateTilt(-self.accZ, self.accY, self.accX, self.isDone)
            self.totalAccData = 0

    def calibrateOffset(self):

        if len(data[2]) == 0:
            return
        elif self.totalMagData == 0:
            data[2].popleft()
            self.totalMagData += 1
        elif self.totalMagData == 1:
            self.magX = data[2].popleft()
            self.totalMagData += 1
        elif self.totalMagData == 2:
            self.magY = data[2].popleft()
            self.totalMagData += 1
        elif self.totalMagData == 3:
            self.magZ = data[2].popleft()
            self.totalMagData += 1

        if self.totalMagData == 4:
            # x points to front
            # y points to left
            # z points to up
            self.calibrator.calibrateNOffset(-self.magZ, self.magY, self.magX, self.isDone)
            self.totalMagData = 0


class LocationDisplayThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while 1:
            locationTrackerLock.acquire()
            locationTracker.updateLocation()
            print "Total Steps:", locationTracker.getTotalSteps()
            print "Total Distance:", locationTracker.getTotalDistance()
            print "Deviation from N:", locationTracker.getHeadingInDeg()
            print "Deviation from Map N:", locationTracker.getHeadingWRTMapInDeg()
            print locationTracker.getLocation()
            print "Height:", locationTracker.getHeightInCM()
            locationTrackerLock.release()
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
            # f = open('accdata.csv', 'a')
            # f.write(str(self.accX) + ',' + str(self.accY) + ',' + str(self.accZ) + '\n')
            # f.close()
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
            # Parameter xReading points left
            # Parameter yReading points forward
            locationTracker.updateCompassData(-self.magZ, self.magY, self.magX)
            self.totalCompData = 0
            # f = open('compdata.csv', 'a')
            # f.write(str(self.magX) + ',' + str(self.magY) + ',' + str(self.magZ) + '\n')
            # f.close()
            # print "timeStamp:", self.timeInMillisComp, "MagX:", self.magX, "MagY:", self.magY, "MagZ:", self.magZ, \
            #     "time:", datetime.datetime.now()

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
            locationTrackerLock.acquire()
            self.updatePedoData()
            self.updateCompassData()
            self.updateBaroData()
            locationTrackerLock.release()


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
            curX = locationTracker.getXCoord()
            curY = locationTracker.getYCoord()
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
                if obstacle.isFrontObstacleDetected(obstacleStatus) is True:
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
# 6 - IR (front bottom) (0)
# 7 - IR (left side) (1)
# 8 - IR (right side) (2)
# 9-10 - unused 
# 11 - sonar (front top) (29 trig 19 echo)
# 12 - sonar (left side) (27 trig 18 echo)
# 13 - sonar (right side) (25 trig  2 echo)

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
locationTracker = locationTracker.LocationTracker(0, 0, 0.0)
dataFeeder = dataFeeder.DataFeeder()

# Locks for various variables
locationTrackerLock = threading.Lock()
obstacleLock = threading.Lock()
obstacleStatusLock = threading.Lock()
dataInLock = threading.Lock()

# Threads to receive data from Arduino
dataThreads = []
dataThreads.append(ReceiveDataThread(1, "data receiving"))
dataThreads.append(ProcessDataThread(2, "data processing"))

for thread in dataThreads:
    thread.start()

### Init threads
##initThreads = []
##initThreads.append(CalibrationThread(-1, "calibrating pedometer and compass"))
##
##for thread in initThreads:
##    thread.start()
##
##for thread in initThreads:
##    thread.join()

# List of threads
mainThreads = []

# mainThreads.append(ReceiveDataThread(1, "data receiving"))
# mainThreads.append(ProcessDataThread(2, "data processing"))
mainThreads.append(LocationUpdateThread(3, "location update"))
mainThreads.append(LocationDisplayThread(4, "location display"))
# mainThreads.append(NavigationThread(5, "navigation"))
mainThreads.append(ObstacleAvoidanceThread(6, "avoid obstacles"))
mainThreads.append(ObstacleClearedThread(7, "ensure obstacles cleared"))

for thread in mainThreads:
    thread.start()

for thread in (mainThreads + dataThreads):
    thread.join()

print("Exiting main thread")
