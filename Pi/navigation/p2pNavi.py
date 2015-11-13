import distAngleCalc
import time
import math

# API:
# setNorthAt(northAt)
# setPrevCoordinates(x, y)
# setNexCoordinates(x, y)
# updateCurCoord(x, y)
# updateHeading(heading)
# setNextNodeName(nodeName)
# navigate()
# TODO: Change the maxTolerance, maxDeviation, angleTolerance values

class navigation (object) :
    def __init__(self, voiceQueue, voiceSema) :
        self.prev_message_time_dist = 0
        self.prev_message_time_turn = 0
        self.prev_message_time_str = 0
        self.message_delay = 0
        self.sentence = ""
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

        # deviation tolerance
        self.maxDeviation = 80       # cm
        # vicinity tolerance
        self.maxTolerance = 200       # cm
        # angle tolerance
        self.angleTolerance = 0     # degrees
        # if already notified that nearing node
        self.alreadyAlerted = False
        self.NEARING_DISTANCE = 400

    def updateCurCoord(self, x, y) :
        self.curXCoord = x
        self.curYCoord = y

    def updateHeading(self, heading) :
        self.curAngle = heading

    def setNorthAt(self, northAt) :
        self.northAt = northAt

    def setNextNodeName(self, nodeName) :
        self.nextNodeName = nodeName
    
    def setPrevCoordinates(self, prevXCoord, prevYCoord) :
        self.prevXCoord = prevXCoord
        self.prevYCoord = prevYCoord

    def setNexCoordinates(self, nexXCoord, nexYCoord) :
        self.nexXCoord = nexXCoord
        self.nexYCoord = nexYCoord

    def stringNumbers(self, numInput) :
        temp = int(numInput)
        outputString = ""
        while temp > 0 :
            outputString = str(temp%10) + " " + outputString
            temp/=10
        return outputString

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
    
    # alert the user once when he is less than 4m from the node
    def alertNearingNode(self, distanceTo) :
        if ((distanceTo <= self.NEARING_DISTANCE) and (distanceTo > self.maxTolerance)) :
            if self.alreadyAlerted is False:
                self.alreadyAlerted = True
                sentence = "%s in %d m" %(self.nextNodeName, int(distanceTo/100))
                print sentence
                self.voiceQueue.append_high(sentence, time.time())


    # navigation algorithm:
    # If the destination node has been reached, return 1
    # else return 0
    def navigate(self) :
        distanceToNode = distAngleCalc.distance(self.curXCoord, self.curYCoord, self.nexXCoord, self.nexYCoord)

        self.alertNearingNode(distanceToNode)

        if (distanceToNode > self.maxTolerance) :
            print "distance to node is: " + str(distanceToNode)
            turnAngle = self.getTurnAngle()

            # if angle is within tolerance, continue in current direction
            # or if not allowed to turn because already turned 90degrees
            if (math.fabs(turnAngle) < self.angleTolerance):
                sentence = "Go"
                print sentence
                if time.time() - self.prev_message_time_turn > self.message_delay:
                   if self.voiceQueue.append(sentence, time.time()):
                       self.voiceSema.release()
                   self.prev_message_time_turn = time.time()
                return 0
        
            if (turnAngle > 0) :
                sentence = "Right " + self.stringNumbers(turnAngle)
                print sentence
                if time.time() - self.prev_message_time_turn > self.message_delay:
                   if self.voiceQueue.append(sentence, time.time()):
                       self.voiceSema.release()
                   self.prev_message_time_turn = time.time()
            elif (turnAngle < 0) :
                sentence = "Left " + self.stringNumbers(math.fabs(turnAngle))
                print sentence
                if time.time() - self.prev_message_time_turn > self.message_delay:
                   if self.voiceQueue.append(sentence, time.time()):
                       self.voiceSema.release()
                   self.prev_message_time_turn = time.time()
            else :
                sentence = "Go"
                print sentence
                if time.time() - self.prev_message_time_str > self.message_delay:
                   if self.voiceQueue.append(sentence, time.time()):
                       self.voiceSema.release()
                   self.prev_message_time_turn = time.time()

            return 0
        else :
            self.alreadyAlerted = False
            return 1
