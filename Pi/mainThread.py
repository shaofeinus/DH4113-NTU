import threading
import time
import math
import datetime
from deadReckoning import locationTracker
from deadReckoning import calibrationTools
from navigation import fullNavi
from navigation import obstacleAvoidance
from communication import dataFeeder
# from communication import dataFeederDum
from collections import deque
from UI import voiceCommands
from UI import search
from UI import keypad_polling
from UI import pyespeak
from my_deque import my_deque
from UISpeaker import UI_Speaker

__author__ = 'Shao Fei'

#to print sound just call voiceQueue.append(sentence)

skip_pad = keypad_polling.keypad(None, None, None)
skip_init = skip_pad.poll_for_num_timed()
del skip_pad

# VoiceQueue has 2 levels of priority: HIGH is enqueued by append_high, and NORMAL is enqueued by append
#
# ===HIGH PRIORITY===
# Node Reached
# You reached %s node
# Navigation Complete
# Rerouting
#
# ===NORMAL PRIORITY===
# Right %f
# Left %f
# Go
# %s in %f metres
# Normal Priority will be preempted by HIGH Priority

# If NORMAL Prio is enqueued before latest enqueue timing, dropped. Released not called
# If NORMAL Prio is dequeued with timestamp after latest dequeue timing, dropped. Acquire is called successfully, but nothing will be spoken

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
                    speaker.speak(str(voiceQueue.popleft()))
            else:
                time.sleep(1)

class ReceiveDataThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            # print 'receiving'
            userInputLock.acquire()
            dataFeeder.receive_data(dataInSema)
            userInputLock.release()


class ProcessDataThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        while True:
            dataFeeder.process_data(data, dataInSema)

##            print "ir ",
##            print data[6],
##            print data[7],
##            print data[8],
##            print data[9],
##            print data[10],
##            print data[15],
##            print "sonar ",
##            print data[12],
##            print data[13]

class CalibrationThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

        self.calibrator = locationTracker.compass.calibrator
        self.calibrationTools = locationTracker.calibrationTools
        self.isDone = {'tilt': False, 'nOffset': False, 'gyro': False}

        self.accX = 0
        self.accY = 0
        self.accZ = 0
        self.totalAccData = 0
        self.magX = 0
        self.magY = 0
        self.magZ = 0
        self.totalMagData = 0
        self.gyroX = 0
        self.gyroY = 0
        self.gyroZ = 0
        self.totalGyroData = 0

    def run(self):
        # magXrange = (-4328, 5605)
        # magYRange = (-5096, 5002)
        # magZRange = (-4618, 4655)
        # self.calibrator.inputManualRange(magZRange, magYRange, magXrange)
        userInputLock.acquire()

        global keypad
        global UISpeaker
        global data, data_single

        validInput = False
        while not validInput:
            # userInput = raw_input("Press enter to calibrate? y/n ")

            UISpeaker.speak(str("To calibrate gyroscope, press start."))
            userInput = keypad.get_binary_response()
            print userInput
            if not userInput:
                validInput = True
                for i in range(0, 3):
                    num = 3 - i
                    print num
                    UISpeaker.speak(str(num))
                    time.sleep(1)
                dataFeeder.serialPort.flushInput()
                dataFeeder.serialPort.flushOutput()

                data = [deque() for x in range(NUM_QUEUED_ID)]
                data_single = [0 for x in range(NUM_SINGLE_ID)]
                data.extend(data_single)

                userInputLock.release()

        print len(data[1])

        while not self.isDone['gyro']:
            self.calibrateGyro()

        userInputLock.acquire()

        # Update Gyro offset
        self.calibrationTools.initGyroOffset(self.calibrator.initGXOffset,
                                             self.calibrator.initGYOffset,
                                             self.calibrator.initGZOffset)

        temp = 'Gyro calibrated' + \
               str(self.calibrator.initGXOffset) + ' ' + \
               str(self.calibrator.initGYOffset) + ' ' + \
               str(self.calibrator.initGZOffset)
        print temp
        UISpeaker.speak(temp)

        validInput = False
        while not validInput:
            # userInput = raw_input("Press enter to calibrate? y/n ")

            UISpeaker.speak(str("To begin compass calibration, press start. To skip calibration, press back."))
            userInput = keypad.get_binary_response()
            print userInput
            if not userInput:
                validInput = True
            else:
                dataFeeder.serialPort.flushInput()
                dataFeeder.serialPort.flushOutput()

                data = [deque() for x in range(NUM_QUEUED_ID)]
                data_single = [0 for x in range(NUM_SINGLE_ID)]
                data.extend(data_single)

                userInputLock.release()
                return

        for i in range(0, 3):
            num = 3 - i
            print num
            UISpeaker.speak(str(num))
            time.sleep(1)

        # print 'Calibrating'

        data = [deque() for x in range(NUM_QUEUED_ID)]
        data_single = [0 for x in range(NUM_SINGLE_ID)]
        data.extend(data_single)

        dataFeeder.serialPort.flushInput()
        dataFeeder.serialPort.flushOutput()
        userInputLock.release()

        print len(data[1])

        while not self.isDone['tilt']:
            self.calibrateTilt()

        # Update pitch and roll
        locationTracker.pedometer.calibrate(self.calibrator.pitch, self.calibrator.roll)
        locationTracker.gyroCompass.calibrate(self.calibrator.pitch, self.calibrator.roll)

        while not self.isDone['nOffset']:
            self.calibrateNOffset()

        userInputLock.acquire()
        temp = 'Your are ' + str(int(self.calibrator.getNOffsetAngle() / (2 * math.pi) * 360)) + ' from N. To continue, press start'
        print temp
        UISpeaker.speak(temp)
        while keypad.get_binary_response():
           pass
        dataFeeder.serialPort.flushInput()
        dataFeeder.serialPort.flushOutput()

        data = [deque() for x in range(NUM_QUEUED_ID)]
        data_single = [0 for x in range(NUM_SINGLE_ID)]
        data.extend(data_single)

        userInputLock.release()

        print len(data[1])

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
            # Calibrated data is supplied as actual tilt is calibrated
            self.accX, self.accY, self.accZ = self.calibrationTools.transformACC(self.accX, self.accY, self.accZ)
            self.calibrator.calibrateTilt(-self.accZ, self.accY, self.accX, self.isDone)
            self.totalAccData = 0

    def calibrateNOffset(self):

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
            # Calibrated data is supplied as actual angle is calibrated
            self.magX, self.magY, self.magZ = self.calibrationTools.transformMag(self.magX, self.magY, self.magZ)
            self.calibrator.calibrateNOffset(-self.magZ, self.magY, self.magX, self.isDone)
            self.totalMagData = 0

    def calibrateGyro(self):

        if len(data[3]) == 0:
            return
        elif self.totalGyroData == 0:
            data[3].popleft()
            self.totalGyroData += 1
        elif self.totalGyroData == 1:
            self.gyroX = data[3].popleft()
            self.totalGyroData += 1
        elif self.totalGyroData == 2:
            self.gyroY = data[3].popleft()
            self.totalGyroData += 1
        elif self.totalGyroData == 3:
            self.gyroZ = data[3].popleft()
            self.totalGyroData += 1

        if self.totalGyroData == 4:
            # Raw data is supplied for raw to actual calibration
            self.calibrator.calibrateGyro(self.gyroX, self.gyroY, self.gyroZ, self.isDone)
            self.totalGyroData = 0


class GyroDriftTrackingThread(threading.Thread):

    RATE_OF_DRIFT = -2.0E-6     # In % change

    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.gyroCompass = locationTracker.compass.gyroCompass

    def run(self):
        while True:
            self.gyroCompass.driftAngleOffset += self.RATE_OF_DRIFT
            time.sleep(0.1)


class LocationDisplayThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.count = 0

    def run(self):
        while 1:
            locationTrackerLock.acquire()
            locationTracker.updateLocation()

            if self.count == 10:
                print "Total Steps:", locationTracker.getTotalSteps()
                print "Total Distance:", locationTracker.getTotalDistance()
                print "Deviation from N:", locationTracker.getHeadingInDeg()
                print "Deviation from Map N:", locationTracker.getHeadingWRTMapInDeg()
                print locationTracker.getLocation()
                print "Height:", locationTracker.getHeightInCM()
                self.count = 0
            else:
                self.count += 1

            locationTrackerLock.release()
            time.sleep(1.0)


class LocationUpdateThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.totalAccData = 0
        self.totalMagData = 0
        self.totalBaroData = 0
        self.totalGyroData = 0
        self.magX = 1
        self.magY = 1
        self.magZ = 1
        self.timeInMillisMag = 0
        self.accX = 1
        self.accY = 1
        self.accZ = 1
        self.timeInMillisAcc = 0
        self.baroReading = 1
        self.timeInMillisBaro = 0
        self.gyroX = 0
        self.gyroY = 0
        self.gyroZ = 0
        self.timeInMillisGyro = 0
        self.calibrationTools = locationTracker.calibrationTools
        self.count = 0

    def updateAccData(self):
        if len(data[1]) == 0:
            return
        elif self.totalAccData == 0:
            self.timeInMillisAcc = data[1].popleft()
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

            # print self.accX, self.accY, self.accZ

            self.accX, self.accY, self.accZ = self.calibrationTools.transformACC(self.accX, self.accY, self.accZ)
            locationTracker.updatePedoData(-self.accZ, self.accY, self.accX, self.timeInMillisAcc)
            # locationTracker.updateCompassAccData(-self.accZ, self.accY, self.accX)
            self.totalAccData = 0

            # print self.accX, self.accY, self.accZ

            # f = open('accdata.csv', 'a')
            # f.write(str(self.accX) + ',' + str(self.accY) + ',' + str(self.accZ) + '\n')
            # f.close()
            # print "timeStamp:", self.timeInMillisAcc, "AccX:", self.accX, "AccY:", self.accY, "AccZ:", self.accZ, "time:", datetime.datetime.now()

    def updateMagData(self):
        if len(data[2]) == 0:
            return
        elif self.totalMagData == 0:
            self.timeInMillisMag = data[2].popleft()
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
            # Parameter xReading points left
            # Parameter yReading points forward

            # f = open('compdata.csv', 'a')
            # f.write(str(self.magX) + ',' + str(self.magY) + ',' + str(self.magZ) + '\n')
            # f.close()

            self.magX, self.magY, self.magZ = self.calibrationTools.transformMag(self.magX, self.magY, self.magZ)
            locationTracker.updateCompassMagData(-self.magZ, self.magY, self.magX)
            self.totalMagData = 0

            # print "timeStamp:", self.timeInMillisMag, "MagX:", self.magX, "MagY:", self.magY, "MagZ:", self.magZ, \
            #     "time:", datetime.datetime.now()

    def updateGyroData(self):
        if len(data[3]) == 0:
                return
        elif self.totalGyroData == 0:
            self.timeInMillisGyro = data[3].popleft()
            self.totalGyroData += 1
        elif self.totalGyroData == 1:
            self.gyroX = data[3].popleft()
            self.totalGyroData += 1
        elif self.totalGyroData == 2:
            self.gyroY = data[3].popleft()
            self.totalGyroData += 1
        elif self.totalGyroData == 3:
            self.gyroZ = data[3].popleft()
            self.totalGyroData += 1

        if self.totalGyroData == 4:

            if self.count == 9:
                # f = open('gyro.csv', 'a')
                # f.write(str(self.timeInMillisGyro) + ',' + str(self.gyroX) + ',' + str(self.gyroY) + ',' + str(self.gyroZ) + '\n')
                # f.close()
                self.count = 0
            else:
                self.count += 1

            # print self.gyroX, self.gyroY, self.gyroZ
            # self.calibrationTools.adaptGyroOffset(self.gyroX, self.gyroY, self.gyroZ)
            self.gyroX, self.gyroY, self.gyroZ = self.calibrationTools.transformGyro(self.gyroX, self.gyroY, self.gyroZ)
            locationTracker.compass.gyroCompass.queueGyroReadings(-self.gyroZ, self.gyroY, self.gyroX)
            # print "timeStamp:", self.timeInMillisGyro, "GyX:", self.gyroX, "GyY:", self.gyroY, "GyZ:", self.gyroZ, \
            #     "time:", datetime.datetime.now()
            self.totalGyroData = 0

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
            self.updateAccData()
            self.updateMagData()
            self.updateBaroData()
            self.updateGyroData()
            locationTrackerLock.release()
            pass


class NavigationThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        global naviCount
        global obstacleDetected
        global checkSideObstacle
        global isFirstCleared
        while 1:
            naviCount += 1
            locationTrackerLock.acquire()
            curX = locationTracker.getXCoord()
            curY = locationTracker.getYCoord()
            heading = locationTracker.getHeadingInDeg()
            locationTrackerLock.release()
            # update location and next node direction for obstacle avoidance
##            obstacle.setNextNodeDirection(navi.getGeneralTurnDirection())
##            obstacle.setCurrentLocation(curX, curY)
            # every second, check navigation
##            if (naviCount%10 == 0) :
##                navi.updateCurLocation(curX, curY, heading)
##                if obstacleDetected == 1 or checkSideObstacle == 1:
##                    navi.ignoreNodeObstacle()
##                    time.sleep(0.1)
##                    continue
##                if isFirstCleared == 1 :
##                    navi.updateClearSteps(locationTracker.getTotalSteps())
##                    isFirstCleared = 0
##                else :
##                    navi.updateCurrentSteps(locationTracker.getTotalSteps())
                    
            isNavigationDone = navi.fullNavigate()
            if isNavigationDone is True :
                return
            time.sleep(1)

           
class ObstacleAvoidanceThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        global obstacleDetected
        global checkSideObstacle
        global isFirstCleared
        while 1:
            irFC = data[6]
            irLS = data[7]
            irRS = data[8]
            irFL = data[9]
            irFR = data[10]
            sonarFC = data[11]
            sonarLS = data[12]
            sonarRS = data[13]
            irLarge = data[15]

            # update sensor data
            obstacleLock.acquire()
            obstacle.updateFrontSensorData(irLarge, sonarFC, irFC, irFL, irFR)
            obstacle.updateSideSensorData(sonarLS, sonarRS, irLS, irRS)
            obstacleLock.release()

            obstacleStatusLock.acquire()
            obstacleStatus = obstacleDetected
            obstacleStatusLock.release()

            if obstacle.isFrontObstacleDetected(obstacleStatus) is True :
                obstacleStatusLock.acquire()
                obstacleDetected = 1
                obstacleStatusLock.release()
                obstacle.vibrateMotors()
            
            # up/down step
##            stepType = obstacle.hasStep()
##            if ((stepType == 1) or (stepType == 2)) :
##                obstacle.stepVibrateMotor(stepType)
            
##            if obstacle.isNewObstacleDetected(obstacleStatus) is True:
##                obstacleStatusLock.acquire()
##                obstacleDetected = 1
##                checkSideObstacle = 0
##                isFirstCleared = 0
##                obstacleStatusLock.release()
##                obstacle.vibrateMotors()
##            # existing obstacle
##            obstacleStatusLock.acquire()
##            obstacleStatus = obstacleDetected
##            obstacleStatusLock.release()
##            if obstacleStatus == 1:
##                obstacleLock.acquire()
##                obstacle.updateFrontSensorData(irLarge, sonarFC, irFC, irFL, irFR)
##                obstacle.updateSideSensorData(sonarLS, sonarRS, irLS, irRS)
##                obstacleLock.release()
##                if obstacle.isFrontObstacleDetected(obstacleStatus) is True:
##                    obstacle.turnFromObstacle()
##                else:
##                    obstacle.turnOffMotors()
##                    obstacleStatusLock.acquire()
##                    obstacleDetected = 0
##                    checkSideObstacle = 1
##                    obstacleStatusLock.release()
            time.sleep(0.1)


##class ObstacleClearedThread(threading.Thread):
##    def __init__(self, threadID, threadName):
##        threading.Thread.__init__(self)
##        self.threadID = threadID
##        self.threadName = threadName
##
##    def run(self):
##        global checkSideObstacle
##        global isFirstCleared
##        while 1:
##            irFC = data[6]
##            irLS = data[7]
##            irRS = data[8]
##            irFL = data[9]
##            irFR = data[10]
##            sonarFC = data[11]
##            sonarLS = data[12]
##            sonarRS = data[13]
##            irLarge = data[15]
##
##            obstacleStatusLock.acquire()
##            toMonitorObstacle = checkSideObstacle
##            obstacleStatusLock.release()
##            if toMonitorObstacle == 1:
##                obstacleLock.acquire()
##                obstacle.updateFrontSensorData(irLarge, sonarFC, irFC, irFL, irFR)
##                obstacle.updateSideSensorData(sonarLS, sonarRS, irLS, irRS)
##                obstacleLock.release()
##                # re-route if necessary
##                if obstacle.isRerouteNeeded() is True :
##                    navi.reroutePath()
##                if obstacle.checkObstacleCleared() == 1:
##                    obstacleStatusLock.acquire()
##                    checkSideObstacle = 0
##                    isFirstCleared = 1
##                    print "obstacle cleared"
##                    obstacleStatusLock.release()
##            time.sleep(0.5)

class UIThread(threading.Thread):
    def __init__(self, threadID, threadName):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName

    def run(self):
        global data
        global keypad
        global startLocation
        global endLocation
        global UISpeaker


        userInputLock.acquire()

        # get start location
        startLocation = search.locationSetting(False, keypad, voiceSema, UIspeaker)
        startLocation.run()

        # get end location
        endLocation = search.locationSetting(True, keypad, voiceSema, UIspeaker)
        endLocation.setBuildingAndLevel(startLocation.buildingName, startLocation.levelNumber)
        endLocation.run()

        # flush serial port
        dataFeeder.serialPort.flushInput()
        dataFeeder.serialPort.flushOutput()

        # reset data
        data = []
        data = [deque() for x in range(NUM_QUEUED_ID)]
        data_single = [0 for x in range(NUM_SINGLE_ID)]
        data.extend(data_single)

        userInputLock.release()

##class CollectIRThread(threading.Thread):
##    def __init__(self, threadID, threadName):
##        threading.Thread.__init__(self)
##        self.threadID = threadID
##        self.threadName = threadName
##
##    def run(self):
##        global irCount
##        global irSum
##        while 1:
##            if irCount == 0 :
##                print "Starting!"
##                time.sleep(2)
##            irCount += 1
##            irSum += data[15]
##            if irCount == 15 :
##                irSum /= 15
##                with open("Output.txt", "a") as text_file:
##                    text_file.write("\n")
##                    text_file.write(str(irSum))
##                    print irSum
##                irCount = 0
##                irSum = 0
##                print "NEXT VALUE PLEASE"
##                time.sleep(2)
##            time.sleep(0.1)
##
##irCount = 0
##irSum = 0

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
# 9 - IR (front left)
# 10 - IR (front right)
# 11 - sonar (front) (29 trig echo)
# 12 - sonar (left side) (27 trig 18 echo)
# 13 - sonar (right side) (25 trig  2 echo)
# 15 - IR (large)


# Queue for sound
voiceQueue = my_deque()

# Data lists for raw data
data = [deque() for x in range(NUM_QUEUED_ID)]
data_single = [0 for x in range(NUM_SINGLE_ID)]
data.extend(data_single)

# Obstacle avoidance initialization
obstacle = obstacleAvoidance.obstacleAvoidance()
# 1 if an obstacle avoidance is taking place, else 0
obstacleDetected = 0
checkSideObstacle = 0
# 1 if just cleared, 0 if cleared a while ago
isFirstCleared = 0

# Location tracker initialisation
# TODO: Set initial position
# locationTracker = locationTracker.LocationTracker(7065.0, 1787.0, 0.0)
locationTracker = locationTracker.LocationTracker(0, 0, 0.0)
dataFeeder = dataFeeder.DataFeeder()

# Speaker object
speaker = pyespeak.Speaker()
UISpeaker = UI_Speaker()

# Locks for various variables
locationTrackerLock = threading.Lock()
obstacleLock = threading.Lock()
obstacleStatusLock = threading.Lock()
dataInSema = threading.Semaphore(0)
userInputLock = threading.Lock()
voiceSema = threading.Semaphore(0)
voiceStopSema = False

# Location variables
startLocation = None
endLocation = None

# Keypad initialization
keypad = keypad_polling.keypad(voiceQueue, voiceSema, speaker)

# Threads to receive data from Arduino
dataThreads = []
dataThreads.append(ReceiveDataThread(1, "data receiving"))
dataThreads.append(ProcessDataThread(2, "data processing"))

for thread in dataThreads:
    thread.start()

# Init threads
initThreads = []
initThreads.append(CalibrationThread(-1, "calibrating pedometer and compass"))

for thread in initThreads:
    thread.start()

for thread in initThreads:
    thread.join()

# voice threads
voiceThreads = []
voiceThreads.append(voiceThread(8, "play sound notification"))

for thread in voiceThreads:
    thread.start()

if not skip_init:
    # UI threads
    UIThreads = []
    UIThreads.append(UIThread(-2, "Run UI"))

    for thread in UIThreads:
       thread.start()

    for thread in UIThreads:
       thread.join()

    locationTracker.setLocation(startLocation.getLocationXCoord(), startLocation.getLocationYCoord())
else:
    locationTracker.setLocation(0,0)

# Navigation initialization
naviCount = 0
navi = fullNavi.fullNavi(voiceQueue, voiceSema)
# navi.generateFullPath("com1", 2, 14, 26)

if skip_init:
    navi.generateFullPath("com1", 2, 1, 10)
else:
    navi.generateFullPath(startLocation.getBuildingName(),
                         startLocation.getLevelNumber(),
                         startLocation.getLocationPointIndex(), endLocation.getLocationPointIndex())

# List of threads
mainThreads = []

if skip_init:
    mainThreads.append(LocationUpdateThread(3, "location update"))
    mainThreads.append(LocationDisplayThread(4, "location display"))
    # mainThreads.append(NavigationThread(5, "navigation"))
    # mainThreads.append(ObstacleAvoidanceThread(6, "avoid obstacles"))
    # mainThreads.append(ObstacleClearedThread(7, "ensure obstacles cleared"))
else:
    mainThreads.append(LocationUpdateThread(3, "location update"))
    mainThreads.append(LocationDisplayThread(4, "location display"))
    mainThreads.append(NavigationThread(5, "navigation"))
    mainThreads.append(ObstacleAvoidanceThread(6, "avoid obstacles"))
##    mainThreads.append(ObstacleClearedThread(7, "ensure obstacles cleared"))
##    mainThreads.append(collectIRThread(9, "collect ir data"))


for thread in mainThreads:
    thread.start()

for thread in (mainThreads + dataThreads + voiceThreads):
    thread.join()


print("Exiting main thread")
