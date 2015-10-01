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

        historyIndex = -1
        
        # side sonar readings (cm):
        self.sonarLS = None         # left side
        self.sonarRS = None         # right side

        # IR readings (cm):   
        self.irLS = None            # left side
        self.irRS = None            # right side


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
##        print sonarData/29/2
        if(sonarData == 0) :
            return self.LARGE_VALUE
        return sonarData / 29 / 2


    def updateFrontSensorData(self, sonarFront, irFront) :
        self.historyIndex = (self.historyIndex + 1) % 3
        self.sonarFT[self.historyIndex] = self.convertSonarToCm(sonarFront)
        self.irFB[self.historyIndex] = self.convertIRToCm(irFront)

    def updateSideSensorData(self, sonarLeft, sonarRight, irLeft, irRight) :
        self.sonarLS = self.convertSonarToCm(sonarLeft)
        self.sonarRS = self.convertSonarToCm(sonarRight)
        self.irLS = self.convertIRToCm(irLeft)
        self.irRS = self.convertIRToCm(irRight)

    def hasSonarObstacle(self) :
        for i in self.sonarFT :
            if i > self.FRONT_OBSTACLE_DISTANCE :
                return False
        return True

    def hasIrObstacle(self) :
        for i in self.irFB :
            if i > self.FRONT_OBSTACLE_DISTANCE :
                return False
        return True

    # indicates which side to turn via motors
    def turnFromObstacle(self) :
        print "ENTER TURN FROM OBSTACLE"
        self.lastTurnedDirection = self.getSideToTurn()
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
    
    # choose which direction to turn, default turn right
    # returns 1 for right, 2 for left, 0 if both sides blocked
    def getSideToTurn(self) :
        # both sides blocked
        if((self.irLS < self.SIDE_WALL_DISTANCE) and (self.irRS < self.SIDE_WALL_DISTANCE)) :
            return 0
        # obstacle on the left, no obstacle on the right
        elif((self.irLS < self.SIDE_WALL_DISTANCE) and (self.irRS > self.SIDE_WALL_DISTANCE)) :
            return 1
        # obstacle on the right, no obstacle on the left
        elif((self.irRS < self.SIDE_WALL_DISTANCE) and (self.irLS > self.SIDE_WALL_DISTANCE)) :
            return 2
        # if no obstacles detected, choose the side with more space
        elif(self.sonarLS > self.sonarRS) :
             return 2
        else :
             return 1

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
        if alreadyDetected == 0 :
            return self.isFrontObstacleDetected()
        else :
            return False

    # returns True if an obstacle is detected in front
    # else return False
    def isFrontObstacleDetected(self) :          
        if ((self.hasSonarObstacle() is True) or
            (self.hasIrObstacle() is True)) :
            return True
        else :
            return False


    # monitor the obstacle from the side while the person walks forward,
    # until the obstacle is completely cleared
    # returns 1 if obstacle is cleared, 0 otherwise
    def checkObstacleCleared(self) :
        print "ENTER CHECK OBSTACLE CLEARED"
        if(self.lastTurnedDirection == 1) :
            sideSonar = self.sonarLS
        else :
            sideSonar = self.sonarRS

        if(sideSonar < self.SIDE_OBSTACLE_DISTANCE) :
            return 0
        else :
            return 1
 
