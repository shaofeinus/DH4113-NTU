import time
import math
#import RPi.GPIO as GPIO

# API:
# avoidObstacle()
# TODO : change obstacle tolerance values with experimental data
class obstacleAvoidance (object) :
    def __init__(self) :       
        self.FRONT_OBSTACLE_DISTANCE = 60
        self.BOTTOM_OBSTACLE_DISTANCE = 60
        self.SIDE_WALL_DISTANCE = 100
        self.SIDE_OBSTACLE_DISTANCE = 70
        self.VIBRATE_DURATION = 3

        # GPIO Pins for vibration motors
        self.leftPin = 9
        self.rightPin = 10

        self.lastTurnedDirection = 0
        # sonar readings (cm):
        self.sonarT = None          # front top
        self.sonarB = None          # front bottom
        self.sonarLS = None         # left shoulder
        self.sonarRS = None         # right shoulder

        # IR readings (cm):
        self.irL = None             # bottom left
        self.irR = None             # bottom right

        # set up GPIO using BCM numbering
        ##GPIO.setmode(GPIO.BCM)

        # GPIO Pins set to pull up
        ##GPIO.setup(leftPin, GPIO.OUT)
        ##GPIO.setup(righttPin, GPIO.OUT)

        ### initially turned off
        ##GPIO.output(leftPin, True)
        ##GPIO.output(rightPin, True)
    def convertIRToCm(self, irData) :
        if irData > 0:
            return 10650.08 * (math.pow(irData, -0.935)) - 10
        return 0

    def convertSonarToCm(self, sonarData) :
        return sonarData / 29 / 2

    # update sonar data
    def updateFrontSonarData(self, top, bottom) :
        self.sonarT = self.convertSonarToCm(top)
        self.sonarB = self.convertSonarToCm(bottom)

    def updateSideSonarData(self, left, right) :
        self.sonarLS = self.convertSonarToCm(left)
        self.sonarRS = self.convertSonarToCm(right)

    def updateIRData(self, left, right) :
        self.irL = self.convertIRToCm(left)
        self.irR = self.convertIRToCm(right)

    # indicates which side to turn via motors
    def turnFromObstacle(self) :
##        print "ENTER TURN FROM OBSTACLE"
        self.lastTurnedDirection = self.getSideToTurn()
        if self.lastTurnedDirection == 1 :
    ##        GPIO.output(leftPin, True)
    ##        GPIO.output(rightPin, False)
             print "Turn right! Right vibrator activated"
        elif self.lastTurnedDirection == 2 :
    ##        GPIO.output(leftPin, False)
    ##        GPIO.output(rightPin, True)
            print "Turn left! Left vibrator activated"
        else :
    ##        GPIO.output(leftPin, False)
    ##        GPIO.output(rightPin, False)
            print "Both side blocked! Both vibration motors activated"

    
    # choose which direction to turn, default turn right
    # returns 1 for right, 2 for left, 0 if both sides blocked
    def getSideToTurn(self) :
        if ((self.sonarRS > self.SIDE_WALL_DISTANCE) or (self.sonarRS == 0))  :
            return 1
        elif ((self.sonarLS > self.SIDE_WALL_DISTANCE)  or (self.sonarLS == 0)):
            return 2
        else :
            return 0


    def vibrateMotors(self) :
##        GPIO.output(leftPin, False)
##        GPIO.output(rightPin, False)
        print "Obstacle encountered! Vibrate both sensors for 3 seconds"
        # wait for VIBRATE_DURATION before proceeding
        time.sleep(self.VIBRATE_DURATION)

    def turnOffMotors(self) :
        print "Vibration motors turned off"
##        GPIO.output(leftPin, True)
##        GPIO.output(rightPin, True)


    # detects new obstacles:
    # if alreadyDetected is 1, return 0, else
    # if an obstacle is detected, vibrates both motors
    # and returns 1, else returns 0
    def isNewObstacleDetected(self, alreadyDetected) :
##        print "ENTER NEW AVOID OBSTACLE"
        if alreadyDetected == 0 :
            if (((self.sonarT < self.FRONT_OBSTACLE_DISTANCE) and (self.sonarT != 0)) or
                ((self.sonarB < self.FRONT_OBSTACLE_DISTANCE) and (self.sonarB != 0))or
                ((self.irL < self.BOTTOM_OBSTACLE_DISTANCE) and (self.irL != 0)) or
                ((self.irR < self.BOTTOM_OBSTACLE_DISTANCE) and (self.irR != 0))) :
                return 1
            else :
                return 0
        else :
            return 0

    # returns 1 if an obstacle is detected in front
    # else return 0
    def isFrontObstacleDetected(self) :
##        print "ENTER FRONT AVOID OBSTACLE"
        if (((self.sonarT < self.FRONT_OBSTACLE_DISTANCE) and (self.sonarT != 0)) or
            ((self.sonarB < self.FRONT_OBSTACLE_DISTANCE) and (self.sonarB != 0))or
            ((self.irL < self.BOTTOM_OBSTACLE_DISTANCE) and (self.irL != 0)) or
            ((self.irR < self.BOTTOM_OBSTACLE_DISTANCE) and (self.irR != 0))) :
            return 1
        else :
            return 0


    # monitor the obstacle from the side while the person walks forward,
    # until the obstacle is completely cleared
    # returns 1 if obstacle is cleared, 0 otherwise
    def checkObstacleCleared(self) :
##        print "ENTER CHECK OBSTACLE CLEARED"
        if(self.lastTurnedDirection == 1) :
            sideSonar = self.sonarLS
        else :
            sideSonar = self.sonarRS

        if((sideSonar < self.SIDE_OBSTACLE_DISTANCE) and (sideSonar != 0)) :
            return 0
        else :
            return 1
 
