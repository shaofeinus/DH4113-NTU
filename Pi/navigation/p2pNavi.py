import distAngleCalc
import math
##import RPi.GPIO as GPIO

# API:
# setNorthAt(northAt)
# setPrevObstacleHeading(angle)
# setPrevCoordinates(x, y)
# setNexCoordinates(x, y)
# updateCurCoord(x, y)
# updateHeading(heading)
# setNextNodeName(nodeName)
# resetNearingCount()
# navigate()
# TODO: Change the maxTolerance, maxDeviation, angleTolerance values

class navigation (object) :
    def __init__(self, voiceQueue, voiceSema) :
        self.voiceQueue = voiceQueue
        self.voiceSema = voiceSema
        self.prevXCoord = 0         # cm
        self.prevYCoord = 0         # cm
        self.nexXCoord = 0          # cm
        self.nexYCoord = 0          # cm
        self.northAt = 0            # 0 to 360 degrees
        self.curXCoord = 0          # cm
        self.curYCoord = 0          # cm
        self.curAngle = 0           # -180 to 180 degrees
        self.nextNodeName = None
        self.leftPin = 9
        self.rightPin = 10

        # maximum allowable angle to prevent
        # returning to obstacle
        self.maxAllowableAngle = 15
        # location of previous obstacle
        self.prevObstacleHeading = 0

        # deviation tolerance
        self.maxDeviation = 80       # cm
        # vicinity tolerance
        self.maxTolerance = 200       # cm
        # angle tolerance
        self.angleTolerance = 17     # degrees
        # distance from node for updates
        self.nearingCount = 500

    def setPrevObstacleHeading(self, angle) :
        self.prevObstacleHeading = angle

    def updateCurCoord(self, x, y) :
        self.curXCoord = x
        self.curYCoord = y

    def updateHeading(self, heading) :
        self.curAngle = heading

    def setNorthAt(self, northAt) :
        self.northAt = northAt

    def setNextNodeName(self, nodeName) :
        self.nextNodeName = nodeName

    def resetNearingCount(self) :
        self.nearingCount = 500
    
    def setPrevCoordinates(self, prevXCoord, prevYCoord) :
        self.prevXCoord = prevXCoord
        self.prevYCoord = prevYCoord

    def setNexCoordinates(self, nexXCoord, nexYCoord) :
        self.nexXCoord = nexXCoord
        self.nexYCoord = nexYCoord


    # calculates the deviation from x-coordinate the person
    # is supposed to be, based on his current y-coordinate
    def getEqnXDeviation(self) :
        if ((self.nexYCoord - self.prevYCoord) == 0 or
            (self.nexXCoord - self.prevXCoord) == 0):
            return math.fabs(self.nexXCoord - self.curXCoord)
        else :
            slope = (float(self.nexYCoord - self.prevYCoord)/(self.nexXCoord - self.prevXCoord))
            correctX = self.nexXCoord - ((self.nexYCoord - self.curYCoord) / slope)
            return math.fabs(self.curXCoord - correctX)


    # calculates the y-coordinate the person is supposed to be
    # based on his current x-coordinate
    def getEqnYDeviation(self) :
        if ((self.nexYCoord - self.prevYCoord) == 0 or
            (self.nexXCoord - self.prevXCoord) == 0) :
            return math.fabs(self.nexYCoord - self.curYCoord)
        else :
            slope = (float(self.nexYCoord - self.prevYCoord) / (self.nexXCoord - self.prevXCoord))
            correctY = self.nexYCoord - ((self.nexXCoord - self.curXCoord) * slope)
            return math.fabs(self.curYCoord - correctY)

    # calculates the angle to turn (-180 to 180)
    def getTurnAngle(self) :
        dirToHead = distAngleCalc.calcAngle(
            self.curXCoord, self.curYCoord, self.nexXCoord, self.nexYCoord, self.northAt)
        turnAngle = dirToHead - self.curAngle 
        if turnAngle > 180 :
            turnAngle -= 360
        elif turnAngle <= -180 :
            turnAngle += 360
        return turnAngle

    # returns the angle to turn, after taking tolerances into account 
    def getApproxTurnAngle(self) :
        approxTurnAngle = 0      
##        pathXDisp = math.fabs(self.nexXCoord - self.prevXCoord)  
##        pathYDisp = math.fabs(self.nexYCoord - self.prevYCoord)
##
##        # horizontal and vertical displacements from correct path
##        xStray = self.getEqnXDeviation()
##        yStray = self.getEqnYDeviation()
##
##        # check if the path to be traversed is more horizontal or vertical
##        # if horizontal, check the y displacement
##        # if vertical, check the x displacement
##        # if neither, check the current x and y displacement and use the larger            
##        if pathXDisp > pathYDisp :
##            if yStray > self.maxDeviation :
##                print "strayed in y-direction by: " + str(yStray)
##                approxTurnAngle = self.getTurnAngle()     
##        elif pathXDisp < pathYDisp :
##            if xStray > self.maxDeviation :
##                print "strayed in x-direction by: " + str(xStray)
##                approxTurnAngle = self.getTurnAngle()
##        else :
##            xTravelled = math.fabs(curXCoord - self.prevXCoord)
##            yTravelled = math.fabs(curYCoord - self.prevYCoord)
##            if xTravelled > yTravelled and yStray > self.maxDeviation :            
##                print "strayed by: " + str(yStray)
##                approxTurnAngle = self.getTurnAngle()
##            elif yTravelled > xTravelled and xStray > self.maxDeviation :
##                print "strayed by: " + str(xStray)
##                approxTurnAngle = self.getTurnAngle()
        return approxTurnAngle
    

    def alertNearingNode(self, distanceTo) :
        if ((distanceTo <= self.nearingCount) and (distanceTo > self.maxTolerance)) :
            sentence = "You are now %.1f meters away from %s" %(distanceTo/100.0, self.nextNodeName)
            print sentence
            self.voiceQueue.append(sentence)
            self.voiceSema.release()
            while (self.nearingCount >= distanceTo) :
                self.nearingCount -= 100


    # navigation algorithm:
    # If the destination node has been reached, return 1
    # else return 0.  Guides the user which way to turn
    # using the vibration motors
    def navigate(self) :
##        curXDisp = math.fabs(self.nexXCoord - self.curXCoord)  
##        curYDisp = math.fabs(self.nexYCoord - self.curYCoord)
        distanceToNode = distAngleCalc.distance(self.curXCoord, self.curYCoord, self.nexXCoord, self.nexYCoord)

        self.alertNearingNode(distanceToNode)

        if (distanceToNode < self.maxTolerance) :
            turnAngle = self.getTurnAngle()
            ultimateAngleHeading = turnAngle + self.curAngle
            angle1 = math.fabs(ultimateAngleHeading - self.prevObstacleHeading)
            angle2 = 360 - angle1

            if min(angle1, angle2) < self.maxAllowableAngle :
                if turnAngle < 0 :
                    correctAngle = self.prevObstacleHeading - self.maxAllowableAngle
                    sentence = "Move towards the right by " + str(correctAngle)
                else :
                    correctAngle = self.prevObstacleHeading + self.maxAllowableAngle
                    sentence = "Move towards the left by " + str(correctAngle)
                print sentence
            else:
                if turnAngle > 0 :
                    sentence = "Move towards the right by " + str(turnAngle)
                    print sentence
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
    ##                    GPIO.output(self.rightPin, True)
    ##                    GPIO.output(self.leftPin, False)
                elif turnAngle < 0 :
                    sentence = "Move towards the left by " + str(math.fabs(turnAngle))
                    print sentence
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
    ##                    GPIO.output(self.leftPin, True)
    ##                    GPIO.output(self.rightPin, False)
                else :
                    sentence = "Keep going in your current direction!"
                    print sentence
        ##                self.voiceQueue.append(sentence)
        ##                self.voiceSema.release()
        ##                GPIO.output(self.leftPin, False)
        ##                GPIO.output(self.rightPin, False)

            return 0
        else :
            return 1
