import time
import math
import distAngleCalc
import RPi.GPIO as GPIO

# API:
# setNextNodeDirection(direction)
# setCurrentLocation(x, y)
# avoidObstacle()
# hasStep()
# stepVibrateMotor()

class obstacleAvoidance (object) :
    def __init__(self) :       
        self.FRONT_OBSTACLE_DISTANCE = 90
        self.FRONT_OBSTACLE_BUFFER = 100
        self.SIDE_OBSTACLE_IR = 75
        self.SIDE_OBSTACLE_SONAR = 70
        self.UPSTEP_THRESHHOLD = 500
        self.DOWNSTEP_THRESHHOLD = 430
        self.VIBRATE_DURATION = 2
        self.OBSTACLE_RADIUS = 70
        self.LARGE_VALUE = 150
        self.SONAR_LARGE_VALUE = 350

        # GPIO Pins for vibration motors
        self.leftPin = 9
        self.rightPin = 10

        self.lastTurnedDirection = 0

        # direction of the next node wrt user heading
        # 1 for right/straight ahead, 2 for left
        self.nextNodeDirection = 0

        # used to check if the same obstacle is encountered
        self.curX = 0
        self.curY = 0
        self.obstacleX = 0
        self.obstacleY = 0

        # used to check if rerouting is necessary
        self.tempObstacleCount = 0
        self.MAX_OBSTACLE_COUNT = 10

        # obstacle cleared count
        self.obstacleClearedCount = 0
        self.CLEARED_MAX_COUNT = 3

        self.irLIndex = -1
        self.irLHistory = 15
        # step detection IR
        self.irLarge = []
        for i in xrange(self.irLHistory) :
            self.irLarge.append(self.LARGE_VALUE)
            
        self.fHistoryIndex = -1
        self.frontNumHistory = 4
        
        # front center Sonar
        self.sonarFC = []
        # front center IR
        self.irFC = []
        # front left IR
        self.irFL = []
        # front right iR
        self.irFR = []
        
        for i in xrange(self.frontNumHistory) :
            self.sonarFC.append(self.LARGE_VALUE)
            self.irFC.append(self.LARGE_VALUE)
            self.irFL.append(self.LARGE_VALUE)
            self.irFR.append(self.LARGE_VALUE)
        
        self.sHistoryIndex = -1
        self.sideNumHistory = 4
        # left side sonar
        self.sonarLS = []
        # left side IR
        self.irLS = []
        # right side sonar
        self.sonarRS = []
        # right side IR
        self.irRS = []

        for i in xrange(self.sideNumHistory) :
            self.sonarLS.append(self.LARGE_VALUE)
            self.sonarRS.append(self.LARGE_VALUE)
            self.irLS.append(self.LARGE_VALUE)
            self.irRS.append(self.LARGE_VALUE)
     

        # set up GPIO using BCM numbering
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # GPIO Pins set to pull up
        GPIO.setup(self.leftPin, GPIO.OUT)
        GPIO.setup(self.rightPin, GPIO.OUT)

        # initially turned off
        GPIO.output(self.leftPin, False)
        GPIO.output(self.rightPin, False)
            

    def setNextNodeDirection(self, direction) :
        self.nextNodeDirection = direction

    def setCurrentLocation(self, x, y) :
        self.curX = x
        self.curY = y
        

    # convert raw IR data to cm
    # removes zero value, change to LARGE_VALUE        
    def convertIRToCm(self, irData) :
        if ((irData > 100) and (irData < 614)):
            return 10650.08 * (math.pow(irData, -0.935)) - 10
        else :
            return self.LARGE_VALUE

    # convert raw sonar data to cm
    # removes zero value, change to LARGE_VALUE
    def convertSonarToCm(self, sonarData) :
        if(sonarData <= 1) :
            return self.SONAR_LARGE_VALUE
        return sonarData / 29 / 2

    # default side to turn if both sides clear
    # 1 for right, 2 for left
    def getSideToTurn(self) :
        turnTo = distAngleCalc.calcAngle(
            self.curXCoord, self.curYCoord, self.nexXCoord, self.nexYCoord, self.northAt)
        if turnTo < 0 :
            return 2
        else :
            return 1

    def printFrontSensorValues(self) :
        print "Large IR: " + str(self.getIrLarge())
        print "Front Center IR: " + str(self.irFC[self.fHistoryIndex])
##        print "Front Left IR: " + str(self.irFL[self.fHistoryIndex])
##        print "Front Right IR: " + str(self.irFR[self.fHistoryIndex])

    def printSideSensorValues(self) :
        print "Left sonar: " + str(self.getLeftSonar())
        print "Right sonar: " + str(self.getRightSonar())
        print "Left IR: " + str(self.getLeftIr())
        print "Right IR: " + str(self.getRightIr())

    def updateFrontSensorData(self, irLarge, sonarFC, irFC, irFL, irFR) :
        self.irLIndex = (self.irLIndex + 1) % self.irLHistory
        self.irLarge[self.irLIndex] = self.irLarge
        
        self.fHistoryIndex = (self.fHistoryIndex + 1) % self.frontNumHistory
        self.sonarFC[self.fHistoryIndex] = self.convertSonarToCm(sonarFC)
        self.irFC[self.fHistoryIndex] = self.convertIRToCm(irFC)
        self.irFL[self.fHistoryIndex] = self.convertIRToCm(irFL)
        self.irFR[self.fHistoryIndex] = self.convertIRToCm(irFR)

    def updateSideSensorData(self, sonarLeft, sonarRight, irLeft, irRight) :
        self.sHistoryIndex = (self.sHistoryIndex + 1) % self.sideNumHistory
        self.sonarLS[self.sHistoryIndex] = self.convertSonarToCm(sonarLeft)
        self.sonarRS[self.sHistoryIndex] = self.convertSonarToCm(sonarRight)
        self.irLS[self.sHistoryIndex] = self.convertIRToCm(irLeft)
        self.irRS[self.sHistoryIndex] = self.convertIRToCm(irRight)
        

    def hasFCSonarObstacle(self, isAlreadyDetected) :
##        if isAlreadyDetected == 0 :
##            for i in self.irFC :
##                if i > self.FRONT_OBSTACLE_DISTANCE :
##                    return False
##            return True
##        else :
##            for i in self.irFC :
##                if i <= self.FRONT_OBSTACLE_DISTANCE :
##                    return True
##            return False
        sonarAverage = 0
        for i in self.sonarFC :
            sonarAverage += i
        sonarAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (sonarAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print self.sonarFC
                print "front sonar:" + str(sonarAverage)
                return True
            else :
                return False
        else :
            if (sonarAverage < self.FRONT_OBSTACLE_BUFFER) :
                print self.sonarFC
                print "front sonar:" + str(sonarAverage)
                return True
            else :
                return False


    def hasFCIrObstacle(self, isAlreadyDetected) :
        irAverage = 0
        for i in self.irFC :
            irAverage += i
        irAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (irAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print "front ir center: " + str(irAverage)
                print self.irFC
                return True
            else :
                return False
        else :
            if (irAverage < self.FRONT_OBSTACLE_BUFFER) :
                print "front ir center: " + str(irAverage)
                print self.irFC
                return True
            else :
                return False


    def hasFLIrObstacle(self, isAlreadyDetected) :
        irAverage = 0
        for i in self.irFL :
            irAverage += i
        irAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (irAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print "front ir left: " + str(irAverage)
                print self.irFL
                return True
            else :
                return False
        else :
            if (irAverage < self.FRONT_OBSTACLE_BUFFER) :
                print "front ir left: " + str(irAverage)
                print self.irFL
                return True
            else :
                return False
      
    def hasFRIrObstacle(self, isAlreadyDetected) :
        irAverage = 0
        for i in self.irFR :
            irAverage += i
        irAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (irAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print "front ir right: " + str(irAverage)
                print self.irFR
                return True
            else :
                return False
        else :
            if (irAverage < self.FRONT_OBSTACLE_BUFFER) :
                print "front ir right: " + str(irAverage)
                print self.irFR
                return True
            else :
                return False

    def hasLeftSonarObstacle(self) :
        sonarAverage = 0
        for i in self.sonarLS :
            sonarAverage += i
        sonarAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (sonarAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print "left leg sonar: " + str(sonarAverage)
                print self.sonarLS
                return True
            else :
                return False
        else :
            if (sonarAverage < self.FRONT_OBSTACLE_BUFFER) :
                print "left leg sonar: " + str(sonarAverage)
                print self.sonarLS
                return True
            else :
                return False

    def hasRightSonarObstacle(self) :
        sonarAverage = 0
        for i in self.sonarRS :
            sonarAverage += i
        sonarAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (sonarAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print "right leg sonar: " + str(sonarAverage)
                print self.sonarRS
                return True
            else :
                return False
        else :
            if (sonarAverage < self.FRONT_OBSTACLE_BUFFER) :
                print "right leg sonar: " + str(sonarAverage)
                print self.sonarRS
                return True
            else :
                return False

    def hasLeftIrObstacle(self, isAlreadyDetected) :
        irAverage = 0
        for i in self.irLS :
            irAverage += i
        irAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (irAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print "left leg ir: " + str(irAverage)
                print self.irLS
                return True
            else :
                return False
        else :
            if (irAverage < self.FRONT_OBSTACLE_BUFFER) :
                print "left leg ir: " + str(irAverage)
                print self.irLS
                return True
            else :
                return False

    def hasRightIrObstacle(self, isAlreadyDetected) :
        irAverage = 0
        for i in self.irRS :
            irAverage += i
        irAverage /= self.frontNumHistory
        if isAlreadyDetected == 0 :
            if (irAverage < self.FRONT_OBSTACLE_DISTANCE) :
                print "right leg ir: " + str(irAverage)
                print self.irRS
                return True
            else :
                return False
        else :
            if (irAverage < self.FRONT_OBSTACLE_BUFFER) :
                print "right leg ir: " + str(irAverage)
                print self.irRS
                return True
            else :
                return False
            

    def getLeftSonar(self) :
        average = 0
        for i in self.sonarLS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irLS[2] - average) > 10) :
            return self.sonarLS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return average

    def getRightSonar(self) :
        average = 0
        for i in self.sonarRS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irRS[2] - average) > 10) :
            return self.sonarRS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return average

    def getLeftIr(self) :
        average = 0
        for i in self.irLS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irLS[2] - average) > 10) :
            return self.irLS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return average

    def getRightIr(self) :
        average = 0
        for i in self.irRS :
            average+= i
        average /= self.sideNumHistory
        if (math.fabs(self.irLS[2] - average) > 10) :
            return self.irRS[(self.sHistoryIndex-1)%self.sideNumHistory]
        else :
            return average

    
    def getIrLarge(self) :
        average = 0
        for i in self.irLarge :
            average+= i
        average /= self.sideNumHistory
        return self.irLarge[self.fHistoryIndex]


    def hasLeftObstacle(self) :
        if ((self.getLeftIr() < self.SIDE_OBSTACLE_IR) or
            (self.getLeftSonar() < self.SIDE_OBSTACLE_SONAR)) :
            print "LEFT OBSTACLE"
            return True
        else :
            return False

    def hasRightObstacle(self) :
        if ((self.getRightIr() < self.SIDE_OBSTACLE_IR) or
            (self.getRightSonar() < self.SIDE_OBSTACLE_SONAR)) :
            print "RIGHT OBSTACLE"
            return True
        else :
            return False
    
    # choose which direction to turn:
    # default turn towards the next node, or last turned direction
    # returns 1 for right, 2 for left, 0 if both sides blocked
    def getSideToTurn(self) :
        # both sides blocked
        if((self.hasLeftObstacle() is True) and (self.hasRightObstacle() is True)):
            print "LEFT and RIGHT obstacles!"
            return 0
        
        print "TURN DIRECTION " + str(self.lastTurnedDirection)

        # first time turning, if no obstacle detected, choose based on 
        if(self.lastTurnedDirection == 0) :
            if((self.hasLeftObstacle() is False) and (self.hasRightObstacle() is False)):
                return self.nextNodeDirection

        # check both sides and base result on previous direction turned
        if (self.lastTurnedDirection == 1) :
            if (self.hasRightObstacle() is False) :
                return 1
            else :
                return 2
        else :
            if (self.hasLeftObstacle() is False) :
                return 2
            else :
                return 1

        
    # indicates which side to turn via motors
    def turnFromObstacle(self) :
        print "ENTER TURN FROM OBSTACLE"
        self.printSideSensorValues()
        self.lastTurnedDirection = self.getSideToTurn()
        if self.lastTurnedDirection == 1 :
            GPIO.output(self.leftPin, False)
            GPIO.output(self.rightPin, True)
            print "Turn right! Right vibrator activated"
        elif self.lastTurnedDirection == 2 :
            GPIO.output(self.leftPin, True)
            GPIO.output(self.rightPin, False)
            print "Turn left! Left vibrator activated"
        else :
            GPIO.output(self.leftPin, True)
            GPIO.output(self.rightPin, True)
            print "Both side blocked! Both vibration motors activated"

    def vibrateMotors(self) :
        GPIO.output(self.leftPin, True)
        GPIO.output(self.rightPin, True)
        print "Obstacle encountered! Vibrate both sensors for " + str(self.VIBRATE_DURATION) + " seconds"
        # wait for VIBRATE_DURATION before proceeding
        time.sleep(self.VIBRATE_DURATION)

    def turnOffMotors(self) :
        print "Vibration motors turned off"
        GPIO.output(self.leftPin, False)
        GPIO.output(self.rightPin, False)

    # returns 0 if no step, 1 if up, 2 if down
    def hasStep(self) :
        irAverage = 0
        for i in self.irLarge :
            irAverage += i
        irAverage /= self.irLHistory

        if irAverage > self.UPSTEP_THRESHHOLD :
            if self.isFrontObstacleDetected() is False:
                return 1
            else :
                return 0
        elif irAverage < self.DOWNSTEP_THRESHHOLD :
            return 2
        else :
            return 0   


    # if up step (1), vibrate right-left-right
    # if down step (2),  vibrate left-right-left
    def stepVibrateMotor(self, stepType) :
        if stepType == 1 :
            hasUp = True
        else :
            hasUp = False
        
        print "STEP ENCOUNTERED!"
##        GPIO.output(self.leftPin, not hasUp)
##        GPIO.output(self.rightPin, hasUp)
##        time.sleep(0.2)
##        GPIO.output(self.leftPin, hasUp)
##        GPIO.output(self.rightPin, not hasUp)
##        time.sleep(0.2)
##        GPIO.output(self.leftPin, not hasUp)
##        GPIO.output(self.rightPin, hasUp)
##        time.sleep(0.2)
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)

    # increment count if same obstacle is detected
    def updateObstacleCount(self) :    
        print "CurX = " + str(self.curX)
        print "CurY = " + str(self.curY)
        print "Obstacle X = " + str(self.obstacleX)
        print "Obstacle Y = " + str(self.obstacleY)
        dist = distAngleCalc.distance(self.curX, self.curY, self.obstacleX, self.obstacleY)
        print "distance from last obstacle is: " + str(dist)
        
        if dist <= self.OBSTACLE_RADIUS :
            self.tempObstacleCount += 1
        else :
            self.obstacleX = self.curX
            self.obstacleY = self.curY
            self.tempObstacleCount = 1

        print "Number of times this obstacle was encountered: " + str(self.tempObstacleCount)

    # detects new obstacles:
    # if alreadyDetected is 1, return False, else
    # if an obstacle is detected, returns True
    # else returns False
    def isNewObstacleDetected(self, alreadyDetected) :
        self.lastTurnedDirection = 0
        if alreadyDetected == 0 :
            if self.isFrontObstacleDetected(alreadyDetected) is True :
                self.updateObstacleCount()
                return True
            else :
                return False
        else :
            return False


    # returns True if an obstacle is detected in front
    # else return False
    def isFrontObstacleDetected(self, isAlreadyDetected) :          
        if ((self.hasFCSonarObstacle(isAlreadyDetected) is True) or
            (self.hasFCIrObstacle(isAlreadyDetected) is True) or
            (self.hasFLIrObstacle(isAlreadyDetected) is True) or
            (self.hasFRIrObstacle(isAlreadyDetected) is True)
            (self.hasLeftSonarObstacle(isAlreadyDetected) is True) or
            (self.hasRightSonarObstacle(isAlreadyDetected) is True) or
            (self.hasLeftIrObstacle(isAlreadyDetected) is True) or
            (self.hasRightIrObstacle(isAlreadyDetected) is True)) :
            return True
        else :
            return False


    # monitor the obstacle from the side while the person walks forward,
    # until the obstacle is completely cleared
    # returns 1 if obstacle is cleared, 0 otherwise
    def checkObstacleCleared(self) :
        print "ENTER CHECK OBSTACLE CLEARED"
        if(self.lastTurnedDirection == 1) :
            sideIR = self.getLeftIr()
            sideSonar = self.getLeftSonar()
        else :
            sideIR = self.getRightIr()
            sideSonar = self.getRightSonar()

        if((sideIR > self.SIDE_OBSTACLE_IR) and (sideSonar > self.SIDE_OBSTACLE_SONAR)) :
            print "count is: " + str(self.obstacleClearedCount)
            if (self.obstacleClearedCount >= self.CLEARED_MAX_COUNT) :
                self.obstacleClearedCount= 0
                return 1
            else :
                self.obstacleClearedCount += 1
                return 0
        else :
            self.obstacleClearedCount = 0
            return 0

    # If path re-routing is necessary, reset values and return True
    def isRerouteNeeded(self) :
        if (self.tempObstacleCount >= self.MAX_OBSTACLE_COUNT) :
            print "REROUTING!"
            self.tempObstacleCount = 0
            self.obstacleX = self.curX
            self.obstacleY = self.curY
            return True
        else :
            return False
            

        
 
