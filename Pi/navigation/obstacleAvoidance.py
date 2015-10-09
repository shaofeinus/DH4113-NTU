import time
import math
##import RPi.GPIO as GPIO

# API:
# avoidObstacle()
# TODO : change obstacle tolerance values with experimental data
class obstacleAvoidance (object) :
    def __init__(self) :       
        self.FRONT_OBSTACLE_DISTANCE = 75
        self.BOTTOM_OBSTACLE_DISTANCE = 65
        self.SIDE_WALL_DISTANCE = 100
        self.SIDE_OBSTACLE_DISTANCE = 65
        self.VIBRATE_DURATION = 2
        self.LARGE_VALUE = 11111

        # GPIO Pins for vibration motors
        self.leftPin = 9
        self.rightPin = 10

        self.lastTurnedDirection = 0
        
        # front top sonar
        self.sonarFT = [self.LARGE_VALUE, self.LARGE_VALUE, self.LARGE_VALUE]
        # front bottom IR
        self.irFB = [self.LARGE_VALUE, self.LARGE_VALUE, self.LARGE_VALUE]

        # left side sonar
        self.sonarLS = [self.LARGE_VALUE, self.LARGE_VALUE, self.LARGE_VALUE]
        # left side IR
        self.irLS = [self.LARGE_VALUE, self.LARGE_VALUE, self.LARGE_VALUE]

        # right side sonar
        self.sonarRS = [self.LARGE_VALUE, self.LARGE_VALUE, self.LARGE_VALUE]
        # right side IR
        self.irRS = [self.LARGE_VALUE, self.LARGE_VALUE, self.LARGE_VALUE]

        self.fHistoryIndex = -1
        self.sHistoryIndex = -1

        self.frontNumHistory = 3
        self.sideNumHistory = 3

##        # set up GPIO using BCM numbering
##        GPIO.setmode(GPIO.BCM)
##        GPIO.setwarnings(False)
##
##        # GPIO Pins set to pull up
##        GPIO.setup(self.leftPin, GPIO.OUT)
##        GPIO.setup(self.rightPin, GPIO.OUT)
##
##        # initially turned off
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)

    # convert raw IR data to cm
    # removes zero value, change to LARGE_VALUE        
    def convertIRToCm(self, irData) :
        if irData > 0:
##            print "IRValue: " + str(10650.08 * (math.pow(irData, -0.935)) - 10)
            return 10650.08 * (math.pow(irData, -0.935)) - 10
        else :
            return self.LARGE_VALUE

    # convert raw sonar data to cm
    # removes zero value, change to LARGE_VALUE
    def convertSonarToCm(self, sonarData) :
##        print "sonar Value: " + str(sonarData/29/2)
        if(sonarData == 0) :
            return self.LARGE_VALUE
        return sonarData / 29 / 2


    def updateFrontSensorData(self, sonarFront, irFront) :
        self.fHistoryIndex = (self.fHistoryIndex + 1) % self.frontNumHistory
        self.sonarFT[self.fHistoryIndex] = self.convertSonarToCm(sonarFront)
        self.irFB[self.fHistoryIndex] = self.convertIRToCm(irFront)

    def updateSideSensorData(self, sonarLeft, sonarRight, irLeft, irRight) :
        self.sHistoryIndex = (self.sHistoryIndex + 1) % self.sideNumHistory
        self.sonarLS[self.sHistoryIndex] = self.convertSonarToCm(sonarLeft)
        self.sonarRS[self.sHistoryIndex] = self.convertSonarToCm(sonarRight)
        self.irLS[self.sHistoryIndex] = self.convertIRToCm(irLeft)
        self.irRS[self.sHistoryIndex] = self.convertIRToCm(irRight)

    def hasFSonarObstacle(self, isAlreadyDetected) :
        if isAlreadyDetected == 0 :
            for i in self.sonarFT :
                if i > self.FRONT_OBSTACLE_DISTANCE :
                    return False
            return True
        else :
            for i in self.sonarFT :
                if i <= self.FRONT_OBSTACLE_DISTANCE :
                    return True
            return False
        

    def hasFIrObstacle(self, isAlreadyDetected) :
        if isAlreadyDetected == 0 :
            for i in self.irFB :
                if i > self.FRONT_OBSTACLE_DISTANCE :
                    return False
            return True
        else :
            for i in self.irFB :
                if i <= self.FRONT_OBSTACLE_DISTANCE :
                    return True
            return False

    def getLeftSonar(self) :
        average = 0
        for i in self.sonarLS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irLS[2] - average) > 10) :
            return self.sonarLS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return self.sonarLS[self.sHistoryIndex]


    def getRightSonar(self) :
        average = 0
        for i in self.sonarRS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irRS[2] - average) > 10) :
            return self.sonarRS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return self.sonarRS[self.sHistoryIndex]


    def getLeftIr(self) :
        average = 0
        for i in self.irLS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irLS[2] - average) > 10) :
            return self.irLS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return self.irLS[self.sHistoryIndex]


    def getRightIr(self) :
        average = 0
        for i in self.irRS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irLS[2] - average) > 10) :
            return self.irRS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return self.irRS[self.sHistoryIndex]

        

    # indicates which side to turn via motors
    def turnFromObstacle(self) :
        print "ENTER TURN FROM OBSTACLE"
        self.lastTurnedDirection = self.getSideToTurn(self.lastTurnedDirection)
        if self.lastTurnedDirection == 1 :
##            GPIO.output(self.leftPin, False)
##            GPIO.output(self.rightPin, True)
            print "Turn right! Right vibrator activated"
        elif self.lastTurnedDirection == 2 :
##            GPIO.output(self.leftPin, True)
##            GPIO.output(self.rightPin, False)
            print "Turn left! Left vibrator activated"
        else :
##            GPIO.output(self.leftPin, True)
##            GPIO.output(self.rightPin, True)
            print "Both side blocked! Both vibration motors activated"
    

    # choose which direction to turn, default turn same as lastTurned
    # returns 1 for right, 2 for left, 0 if both sides blocked
    def getSideToTurn(self, lastTurned) :
        # both sides blocked
        if((self.getLeftIr() < self.SIDE_OBSTACLE_DISTANCE) and (self.getRightIr() < self.SIDE_OBSTACLE_DISTANCE)) :
            return 0
        # if both sides have ample space to turn
        elif((self.getRightSonar() > self.SIDE_WALL_DISTANCE) and (self.getLeftSonar() > self.SIDE_WALL_DISTANCE)):
            if(lastTurned != 0) :
                return lastTurned
            else :
                return 1
        # free space on right detected
        elif(self.getRightSonar() > self.SIDE_WALL_DISTANCE) :
            return 1            
        # free space on left detected
        elif(self.getLeftSonar() > self.SIDE_WALL_DISTANCE) :
            return 2
        # not much rooom to turn, but right obstacle not too near
        elif(self.getRightIr() >= self.SIDE_OBSTACLE_DISTANCE) :
            return 1
        # not much rooom to turn, but left obstacle not too near
        else :
            return 2


    def vibrateMotors(self) :
##        GPIO.output(self.leftPin, True)
##        GPIO.output(self.rightPin, True)
        print "Obstacle encountered! Vibrate both sensors for " + str(self.VIBRATE_DURATION) + " seconds"
        # wait for VIBRATE_DURATION before proceeding
        time.sleep(self.VIBRATE_DURATION)

    def turnOffMotors(self) :
        print "Vibration motors turned off"
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)

    # detects new obstacles:
    # if alreadyDetected is 1, return False, else
    # if an obstacle is detected, returns True
    # else returns False
    def isNewObstacleDetected(self, alreadyDetected) :
        self.lastTurnedDirection = 0
        if alreadyDetected == 0 :
            return self.isFrontObstacleDetected(alreadyDetected)
        else :
            return False

    # returns True if an obstacle is detected in front
    # else return False
    def isFrontObstacleDetected(self, isAlreadyDetected) :          
        if ((self.hasFSonarObstacle(isAlreadyDetected) is True) or
            (self.hasFIrObstacle(isAlreadyDetected) is True)) :
            return True
        else :
            return False


    # monitor the obstacle from the side while the person walks forward,
    # until the obstacle is completely cleared
    # returns 1 if obstacle is cleared, 0 otherwise
    def checkObstacleCleared(self) :
        print "ENTER CHECK OBSTACLE CLEARED"
        if(self.lastTurnedDirection == 1) :
            sideSonar = self.getLeftIr()
        else :
            sideSonar = self.getRightIr()

        if(sideSonar < self.SIDE_OBSTACLE_DISTANCE) :
            return 0
        else :
            return 1
 
