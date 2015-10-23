import distAngleCalc
import time
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
        self.prev_message_time_dist = 0
        self.prev_message_time_turn = 0
        self.prev_message_time_str = 0
        self.message_delay = 5
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
        self.prevObstacleHeading = 360

        # deviation tolerance
        self.maxDeviation = 80       # cm
        # vicinity tolerance
        self.maxTolerance = 200       # cm
        # angle tolerance
        self.angleTolerance = 17     # degrees
        # distance from node for updates
        self.nearingCount = 500

        # boolean whether allowed to turn
        self.canTurn = True

        # heading to check if can stop turning
        self.obstacleClearedHeading = 0

    def setCanTurn(self, canTurn) :
        self.canTurn = canTurn

    def setPrevObstacleHeading(self, angle) :
        self.prevObstacleHeading = angle

    def setObstacleClearedHeading(self, angle) :
        self.obstacleClearedHeading = angle

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
    

    def alertNearingNode(self, distanceTo) :
        if ((distanceTo <= self.nearingCount) and (distanceTo > self.maxTolerance)) :
            sentence = "%s in %.1f metres." %(self.nextNodeName, distanceTo/100.0)
            print sentence
            if time.time() - self.prev_message_time_dist > self.message_delay:
                self.voiceQueue.append(sentence)
                self.voiceSema.release()
                self.prev_message_time_dist = time.time()
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

        if (distanceToNode > self.maxTolerance) :
            print "distance to node is: " + str(distanceToNode)
            turnAngle = self.getTurnAngle()

            # if angle is within tolerance, continue in current direction
            # or if not allowed to turn because already turned 90degrees
            if ((math.fabs(turnAngle) < self.angleTolerance) or
                (self.canTurn is False)):
                sentence = "Go straight"
                if time.time() - self.prev_message_time_str > self.message_delay:
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
                    self.prev_message_time_str = time.time()
                print sentence
                return 0
            
##            # ensure don't turn back into an obstacle 
##            ultimateAngleHeading = turnAngle + self.curAngle
##            angle1 = math.fabs(ultimateAngleHeading - self.prevObstacleHeading)
##            angle2 = 360 - angle1
            
##            if ((self.prevObstacleHeading < 360) and (min(angle1, angle2) < self.maxAllowableAngle)) :
##                if ((turnAngle < 0) and (self.prevObstacleHeading <= 0)):
##                    correctAngle = self.prevObstacleHeading - self.maxAllowableAngle
##                if ((turnAngle < 0) and (self.prevObstacleHeading > 0)):
##                    correctAngle = self.prevObstacleHeading + self.maxAllowableAngle
##                elif ((turnAngle > 0) and (self.prevObstacleHeading <= 0)):
##                    correctAngle = self.prevObstacleHeading + self.maxAllowableAngle
##                else:
##                    correctAngle = self.prevObstacleHeading - self.maxAllowableAngle
##
##                if correctAngle > 180 :
##                    correctAngle -= 360
##                elif correctAngle <= -180 :
##                    correctAngle += 360
##
##                if correctAngle > 0 and math.fabs(correctAngle) > self.angleTolerance:
##                    sentence = "move towards the right by: " + str(correctAngle)
##                elif correctAngle < 0 and math.fabs(correctAngle) > self.angleTolerance:
##                    sentence = "move towards the left by: " + str(math.fabs(correctAngle))
##                else :
##                    sentence = "keep going straight"
##                print sentence
##            else:

            if (turnAngle > 0) :
                if ((self.prevObstacleHeading < 360) and (turnAngle > 90)) :
                    turnAngle = 90
                    if self.canTurn is False :
                        return 0
                    else :
                        if math.fabs(self.curAngle - self.obstacleClearedHeading) > 75:
                            self.canTurn = False
                
                sentence = "Right %.0f" %(turnAngle)
                print sentence
                if time.time() - self.prev_message_time_turn > self.message_delay:
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
                    self.prev_message_time_turn = time.time()
    ##                    GPIO.output(self.rightPin, True)
    ##                    GPIO.output(self.leftPin, False)
            elif (turnAngle < 0) :
                if ((self.prevObstacleHeading < 360) and (turnAngle < -90)) :
                    turnAngle = -90
                    if self.canTurn is False :
                        return 0
                    else :
                        if math.fabs(self.curAngle - self.obstacleClearedHeading) > 75:
                            self.canTurn = False
                sentence = "Left %.0f" %(turnAngle)
                print sentence
                if time.time() - self.prev_message_time_turn > self.message_delay:
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
                    self.prev_message_time_turn = time.time()
    ##                    GPIO.output(self.leftPin, True)
    ##                    GPIO.output(self.rightPin, False)
            else :
                sentence = "Go straight"
                if time.time() - self.prev_message_time_str > self.message_delay:
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
                    self.prev_message_time_str = time.time()
                print sentence
    ##                self.voiceQueue.append(sentence)
    ##                self.voiceSema.release()
    ##                GPIO.output(self.leftPin, False)
    ##                GPIO.output(self.rightPin, False)

            return 0
        else :
            return 1
