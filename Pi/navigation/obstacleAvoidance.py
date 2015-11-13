import time
import math
import distAngleCalc
import RPi.GPIO as GPIO

# API:
# isFrontObstacleDetected()
# vibrateMotors()
# turnOffMotors()
# detectStep()

class obstacleAvoidance (object) :
    def __init__(self) :       
        self.FRONT_OBSTACLE_DISTANCE = 90
        self.FRONT_OBSTACLE_BUFFER = 90
        self.FRONT_OBSTACLE_SONAR = 80
        self.FRONT_SONAR_BUFFER = 80
        self.BOTTOM_OBSTACLE_DISTANCE = 50
        self.BOTTOM_OBSTACLE_BUFFER = 50
        self.SIDE_OBSTACLE_IR = 60
        self.SIDE_OBSTACLE_BUFFER = 60
        self.UPSTEP_MAX = 500
        self.UPSTEP_THRESHHOLD = 460
        self.DOWNSTEP_THRESHHOLD = 430
        self.DOWNSTEP_MIN = 400
        self.VIBRATE_DURATION = 0.1
        self.LARGE_VALUE = 150
        self.SONAR_LARGE_VALUE = 350

        # GPIO Pins for vibration motors
        self.leftPin = 9
        self.rightPin = 10

        self.irLIndex = -1
        self.irLHistory = 5
        # step detection IR
        self.irLarge = []
        for i in xrange(self.irLHistory) :
            self.irLarge.append(self.LARGE_VALUE)
            
        self.fHistoryIndex = -1
        self.frontNumHistory = 5
        
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


    def printFrontSensorValues(self) :
        print "Large IR: " + str(self.getIrLarge())
        print "Front Center IR: " + str(self.getIrFC())
        print "Front Left IR: " + str(self.getIrFL())
        print "Front Right IR: " + str(self.getIrFR())
        print "Front Center Sonar: " + str(self.getSonarFC())


    def printSideSensorValues(self) :
        print "Left sonar: " + str(self.getLeftSonar())
        print "Right sonar: " + str(self.getRightSonar())
        print "Left IR: " + str(self.getLeftIr())
        print "Right IR: " + str(self.getRightIr())

    def updateFrontSensorData(self, irLarge, sonarFC, irFC, irFL, irFR) :
        self.irLIndex = (self.irLIndex + 1) % self.irLHistory
        self.irLarge[self.irLIndex] = irLarge
        
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
        sonarAverage = sum(self.sonarFC) / len(self.sonarFC)
        if isAlreadyDetected == 0 :
            if (sonarAverage < self.FRONT_OBSTACLE_SONAR) :
                print self.sonarFC
                print "front sonar:" + str(sonarAverage)
                return True
            else :
                return False
        else :
            if (sonarAverage < self.FRONT_SONAR_BUFFER) :
                print self.sonarFC
                print "front sonar:" + str(sonarAverage)
                return True
            else :
                return False


    def hasFCIrObstacle(self, isAlreadyDetected) :
        irAverage = sum(self.irFC) / len(self.irFC)
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
        irAverage = sum(self.irFL) / len(self.irFL)
        if isAlreadyDetected == 0 :
            if (irAverage < self.SIDE_OBSTACLE_IR) :
                print "front ir left: " + str(irAverage)
                print self.irFL
                return True
            else :
                return False
        else :
            if (irAverage < self.SIDE_OBSTACLE_BUFFER) :
                print "front ir left: " + str(irAverage)
                print self.irFL
                return True
            else :
                return False
      
    def hasFRIrObstacle(self, isAlreadyDetected) :
        irAverage = sum(self.irFR) / len(self.irFR)
        if isAlreadyDetected == 0 :
            if (irAverage < self.SIDE_OBSTACLE_IR) :
                print "front ir right: " + str(irAverage)
                print self.irFR
                return True
            else :
                return False
        else :
            if (irAverage < self.SIDE_OBSTACLE_BUFFER) :
                print "front ir right: " + str(irAverage)
                print self.irFR
                return True
            else :
                return False

    def hasLeftSonarObstacle(self, isAlreadyDetected) :
        sonarAverage = sum(self.sonarLS) / len(self.sonarLS)
        if isAlreadyDetected == 0 :
            if (sonarAverage < self.BOTTOM_OBSTACLE_DISTANCE) :
                print "left leg sonar: " + str(sonarAverage)
                print self.sonarLS
                return True
            else :
                return False
        else :
            if (sonarAverage < self.BOTTOM_OBSTACLE_BUFFER) :
                print "left leg sonar: " + str(sonarAverage)
                print self.sonarLS
                return True
            else :
                return False

    def hasRightSonarObstacle(self, isAlreadyDetected) :
        sonarAverage = sum(self.sonarRS) / len(self.sonarRS)
        if isAlreadyDetected == 0 :
            if (sonarAverage < self.BOTTOM_OBSTACLE_DISTANCE) :
                print "right leg sonar: " + str(sonarAverage)
                print self.sonarRS
                return True
            else :
                return False
        else :
            if (sonarAverage < self.BOTTOM_OBSTACLE_BUFFER) :
                print "right leg sonar: " + str(sonarAverage)
                print self.sonarRS
                return True
            else :
                return False

    def hasLeftIrObstacle(self, isAlreadyDetected) :
        irAverage = sum(self.irLS) / len(self.irLS)
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
        irAverage = sum(self.irRS) / len(self.irRS)
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
    
    def getSonarFC(self) :
        return sum(self.sonarFC) / len(self.sonarFC)

    def getIrFC(self) :
        return sum(self.irFC) / len(self.irFC)

    def getIrFL(self) :
        return sum(self.irFL) / len(self.irFL)

    def getIrFR(self) :
        return sum(self.irFR) / len(self.irFR)
            
    def getLeftSonar(self) :
        return sum(self.sonarLS) / len(self.sonarLS)

    def getRightSonar(self) :
        return sum(self.sonarRS) / len(self.sonarRS)

    def getLeftIr(self) :
        return sum(self.irLS) / len(self.irLS)

    def getRightIr(self) :
        return sum(elf.irRS) / len(elf.irRS)
        
    def vibrateMotors(self) :
        GPIO.output(self.leftPin, True)
        GPIO.output(self.rightPin, True)
        print "Obstacle encountered! Vibrate both sensors for " + str(self.VIBRATE_DURATION) + " seconds"
        # wait for VIBRATE_DURATION before proceeding
        time.sleep(self.VIBRATE_DURATION)

    def turnOffMotors(self) :
        GPIO.output(self.leftPin, False)
        GPIO.output(self.rightPin, False)

    # if up step, vibrate right side
    # if down step,  vibrate left side
    def detectStep(self) :
        longIRAverage = sum(self.irLarge) / len(self.irLarge)
        if ((longIRAverage > self.UPSTEP_THRESHHOLD) and (longIRAverage < self.UPSTEP_MAX)) :
            print "\n\n*********************UPSTEP******************\n\n" + str(longIRAverage)
            GPIO.output(self.leftPin, False)
            GPIO.output(self.rightPin, True)
        elif ((longIRAverage < self.DOWNSTEP_THRESHHOLD)  and (longIRAverage > self.DOWNSTEP_MIN)):
            print "\n\n*********************DOWNSTEP******************\n\n" + str(longIRAverage)
            GPIO.output(self.leftPin, True)
            GPIO.output(self.rightPin, False)
        else :
##            print "\n\n*********************NO STEP******************\n\n" + str(longIRAverage)
            GPIO.output(self.leftPin, False)
            GPIO.output(self.rightPin, False)



    # returns True if an obstacle is detected in front
    # else return False
    def isFrontObstacleDetected(self, isAlreadyDetected) :          
        if ((self.hasFCSonarObstacle(isAlreadyDetected) is True) or
            (self.hasFCIrObstacle(isAlreadyDetected) is True) or
            (self.hasFLIrObstacle(isAlreadyDetected) is True) or
            (self.hasFRIrObstacle(isAlreadyDetected) is True) or
            (self.hasLeftSonarObstacle(isAlreadyDetected) is True) or
            (self.hasRightSonarObstacle(isAlreadyDetected) is True) or
            (self.hasLeftIrObstacle(isAlreadyDetected) is True) or
            (self.hasRightIrObstacle(isAlreadyDetected) is True)) :
            return True
        else :
            return False


        
 
