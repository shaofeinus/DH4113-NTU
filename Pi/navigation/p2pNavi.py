import obstacleAvoidance
import distAngleCalc
import math
#import RPi.GPIO as GPIO

# API:
# startNavi()

class navigation (object) :
    def __init__(self, prevXCoord, prevYCoord, nexXCoord, nexYCoord, northAt) :
        self.prevXCoord = int(prevXCoord)
        self.prevYCoord = int(prevYCoord)
        self.nexXCoord = int(nexXCoord)
        self.nexYCoord = int(nexYCoord)
        self.northAt = int(northAt)
        self.curXCoord = 0
        self.curYCoord = 0
        self.leftPin = 9
        self.rightPin = 10

        # deviation tolerance
        self.maxDeviation = 50
        # vicinity tolerance
        self.maxTolerance = 10
        # angle tolerance
        self.angleTolerance = 15
        
##        # set up GPIO using BCM numbering
##        GPIO.setmode(GPIO.BCM)
##
##        # GPIO Pins 9 and 10 set to pull up
##        GPIO.setup(leftPin, GPIO.OUT)
##        GPIO.setup(rightPin, GPIO.OUT)
##
##        # initially turned off
##        GPIO.output(leftPin, True)
##        GPIO.output(rightPin, True)


    # calculates which direction (left or right) to turn
    def getTurnDirection(self, curXCoord, curYCoord, curAngle) :
        directionToHead = distAngleCalc.calcAngle(
                curXCoord, curYCoord, self.nexXCoord, self.nexYCoord, self.northAt)
        print ("direction to head: " + str(directionToHead) +
               " current angle: " + str(curAngle))
        # convert back to 0 - 360 degrees domain
        if directionToHead < 0 :
            directionToHead += 360
        
        if math.fabs(directionToHead - curAngle) < self.angleTolerance :
            return "straight"
            print "MOVE " + str(math.fabs(directionToHead - curAngle))
        elif directionToHead > curAngle :
            if (directionToHead - curAngle) < 180 :
                return "right"
            else :
                return "left"
        elif directionToHead < curAngle :
            if (curAngle - directionToHead) < 180 :
                return "left"
            else :
                return "right"


    # calculates the deviation from x-coordinate the person
    # is supposed to be, based on his current y-coordinate
    def getEqnXDeviation(self, curX, curY) :
        if ((self.nexYCoord - self.prevYCoord) == 0 or
            (self.nexXCoord - self.prevXCoord) == 0):
            return math.fabs(self.nexXCoord - curX)
        else :
            slope = (float(self.nexYCoord - self.prevYCoord)/(self.nexXCoord - self.prevXCoord))
            correctX = self.nexXCoord - ((self.nexYCoord - curY) / slope)
            return math.fabs(curX - correctX)

    # calculates the y-coordinate the person is supposed to be
    # based on his current x-coordinate
    def getEqnYDeviation(self, curX, curY) :
        if ((self.nexYCoord - self.prevYCoord) == 0 or
            (self.nexXCoord - self.prevXCoord) == 0) :
            return math.fabs(self.nexYCoord - curY)
        else :
            slope = (float(self.nexYCoord - self.prevYCoord) / (self.nexXCoord - self.prevXCoord))
            correctY = self.nexYCoord - ((self.nexXCoord - curX) * slope)
            print "corY: " + str(correctY)
            return math.fabs(curY - correctY)

    # navigation algorithm
    def startNavi(self) :
        pathXDisp = math.fabs(self.nexXCoord - self.prevXCoord)  
        pathYDisp = math.fabs(self.nexYCoord - self.prevYCoord)

        curXDisp = pathXDisp
        curYDisp = pathYDisp

        # direction to move
        turn = None

        # loop until the destination is reached
        # angle input from -180 to 180
        while ((curXDisp > self.maxTolerance) or (curYDisp > self.maxTolerance)) :
            curXCoord = float(raw_input("Enter current x coordinate: "))
            curYCoord = float(raw_input("Enter current y coordinate: "))
            curAngle = float(raw_input("Enter angle direction: "))

            curXDisp = math.fabs(self.nexXCoord - curXCoord)  
            curYDisp = math.fabs(self.nexYCoord - curYCoord)

            turn = None
            # check if the path to be traversed is more horizontal or vertical
            # if horizontal, check the y displacement
            # if vertical, check the x displacement
            # if neither, check the current x and y displacement and use the larger

            # horizontal and vertical displacements from correct path
            xStray = self.getEqnXDeviation(curXCoord, curYCoord)
            yStray = self.getEqnYDeviation(curXCoord, curYCoord)
            
            print "X stray = " + str(xStray) + " Y stray = " + str(yStray)
            if pathXDisp > pathYDisp :
                if yStray > self.maxDeviation :
                    print "strayed in y-direction by: " + str(yStray)
                    turn = self.getTurnDirection(curXCoord, curYCoord, curAngle)     
            elif pathXDisp < pathYDisp :
                if xStray > self.maxDeviation :
                    print "strayed in x-direction by: " + str(xStray)
                    turn = self.getTurnDirection(curXCoord, curYCoord, curAngle)
            else :
                xTravelled = math.fabs(curXCoord - self.prevXCoord)
                yTravelled = math.fabs(curYCoord - self.prevYCoord)
                if xTravelled > yTravelled and yStray > self.maxDeviation :            
                    print "strayed by: " + str(yStray)
                    turn = self.getTurnDirection(curXCoord, curYCoord, curAngle)
                elif yTravelled > xTravelled and xStray > self.maxDeviation :
                    print "strayed by: " + str(xStray)
                    turn = self.getTurnDirection(curXCoord, curYCoord, curAngle)            
            if turn == "right" :
                print "Move towards the right!"
        ##        GPIO.output(rightPin, False)
        ##        GPIO.output(leftPin, True)
            elif turn == "left" :
                print "Move towards the left!"
        ##        GPIO.output(leftPin, False)
        ##        GPIO.output(rightPin, True)
            else :
                print "Keep going in your current direction!"
        ##        GPIO.output(leftPin, True)
        ##        GPIO.output(rightPin, True)

        obstacleAvoidance.avoidObstacle()
        print "Your destination has been reached!"
