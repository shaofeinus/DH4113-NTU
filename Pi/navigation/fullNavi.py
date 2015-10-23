import math
import distAngleCalc
from p2pNavi import navigation
from jsonParsing import mapParser
from dijkstra import pathFinder
##import RPi.GPIO as GPIO
import math
import time

# API:
# generateFullPath(building, start, end)
# 0 for com1L2, 1 for com2L2, 2 for com2L3
# updateCurLocation(x, y, heading)
# updateEncounterSteps(numSteps)
# updateClearSteps(numSteps)
# setObstacleStartHeading(heading)
# setObstacleEndHeading(heading)
# isInitialAngleCorrect()
# fullNavigate()
# getGeneralTurnDirection()
# reroutePath()

class fullNavi(object) :
    def __init__(self, voiceQueue, voiceSema) :
        self.prev_message_time = 0
        self.message_delay = 5
        self.voiceQueue = voiceQueue
        self.voiceSema = voiceSema
        self.voiceStopSema
        self.ANGLE_TOLERANCE = 13

        self.buildingName = None
        self.levelNumber = 0
        self.mapNumber = 0          # index of map in comMap list
        self.startLocation = 0
        self.endLocation = 0
        self.curX = 0               # cm
        self.curY = 0               # cm
        self.heading = 0            # -180 to 180 degrees

        # prevent going back to obstacle
        self.obstacleEncounteredSteps = 0
        self.obstacleClearedSteps = 0
        self.MAX_STEPS = 2

        self.obstStartHeading = 0
        self.obstEndHeading = 0

        # tolerance
        self.maxTolerance = 200

        # list of json parsing maps
        self.comMap = []
        # path list
        self.pathList = []
        self.pathListIndex = 0
        self.northAt = 0            # 0 to 360 degrees
        self.prevX = 0              # cm
        self.prevY = 0              # cm
        self.nexX = 0               # cm
        self.nexY = 0               # cm
        self.nodeNavi = navigation(self.voiceQueue, self.voiceSema)
        self.angleCorrect = True

        self.leftPin = 9
        self.rightPin = 10

##        # set up GPIO using BCM numbering
##        GPIO.setmode(GPIO.BCM)
##        GPIO.setwarnings(False)
##
##        # GPIO Pins 9 and 10 set to pull up
##        GPIO.setup(self.leftPin, GPIO.OUT)
##        GPIO.setup(self.rightPin, GPIO.OUT)
##
##        # initially turned off
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)

    def updateCurLocation(self, x, y, heading) :
        self.curX = x
        self.curY = y
        self.heading = heading
        self.nodeNavi.updateCurCoord(x, y)
        self.nodeNavi.updateHeading(heading)

    def updateEncounterSteps(self, numSteps) :
        self.obstacleEncounteredSteps = numSteps

    def updateClearSteps(self, numSteps) :
        self.obstacleClearedSteps = numSteps

    def setObstacleStartHeading(self, heading) :
        self.obstStartHeading = heading

    def setObstacleEndHeading(self, heading) :
        self.obstEndHeading = heading


    # returns false if at a node, but not facing in the direction of the next node
    def isInitialAngleCorrect(self):
        return self.angleCorrect

    def generateFullPath(self, buildingName, levelNumber, start, end) :
        self.mapNumber = 0
        self.pathListIndex = 0
        self.comMap.append(mapParser())
        self.comMap[self.mapNumber].setMap(buildingName, levelNumber)
        self.startLocation = start
        self.endLocation = end
        self.buildingName = buildingName
        self.levelNumber = levelNumber
        pathFind = pathFinder()
        pathFind.setMap(buildingName, levelNumber)
        self.pathList = pathFind.getPath(start, end)
##        self.northAt = self.comMap[self.mapNumber].getNorthAt()
        self.northAt = 0
        self.updatePrevNexCoord()
        print "Path: " + str(self.pathList)
        self.provideNexNodeDirections()
        self.angleCorrect = False

    # returns nearest node, excluding the past and current nodes
    def getNearestNextNode(self) :
        nearDist = 1000000
        # if next node is already the destination       
        if ((self.pathListIndex + 2) >= len(self.pathList)) :
            return self.pathListIndex
            
        for i in xrange(self.pathListIndex+2, len(self.pathList)) :
            nodeX = int(self.comMap[self.mapNumber].getLocationXCoord(self.pathList[i]))
            nodeY = int(self.comMap[self.mapNumber].getLocationYCoord(self.pathList[i]))
            distTo = distAngleCalc.distance(self.curX, self.curY, nodeX, nodeY)
            if distTo < nearDist :
                nearestNodeIndex = i
                nearDist = distTo
        return nearestNodeIndex

    # re-route path to the next nearest node
    def reroutePath(self) :
        nextNodeIndex = self.getNearestNextNode()
        if self.pathListIndex != nextNodeIndex :
            self.pathListIndex = nextNodeIndex - 1
            sentence = "Re-routing."
            print sentence
            self.voiceQueue.flush()
            self.voiceQueue.append(sentence)
            self.voiceSema.release()
            self.updatePrevNexCoord()
            self.provideNexNodeDirections()


    def updatePrevNexCoord(self) :
        prevNode = self.pathList[self.pathListIndex]
        nexNode =  self.pathList[self.pathListIndex + 1]
        nexNodeName = self.comMap[self.mapNumber].getLocationName(nexNode)
        self.prevX = int(self.comMap[self.mapNumber].getLocationXCoord(prevNode))
        self.prevY = int(self.comMap[self.mapNumber].getLocationYCoord(prevNode))
        self.nexX = int(self.comMap[self.mapNumber].getLocationXCoord(nexNode))
        self.nexY = int(self.comMap[self.mapNumber].getLocationYCoord(nexNode))
        self.nodeNavi.setNorthAt(self.northAt)
        self.nodeNavi.resetNearingCount()
        self.nodeNavi.setNextNodeName(nexNodeName)
        self.nodeNavi.setPrevCoordinates(self.prevX, self.prevY)
        self.nodeNavi.setNexCoordinates(self.nexX, self.nexY)


    def alertNodeReached(self) :
##        GPIO.output(self.leftPin, True)
##        GPIO.output(self.rightPin, True)
        prevNode = self.pathList[self.pathListIndex]
        curNodeName = self.comMap[self.mapNumber].getLocationName(prevNode)
        nodeReachedSentence = "You reached" + str(curNodeName) + "."
        print nodeReachedSentence
        self.voiceQueue.flush()
        self.voiceQueue.append(nodeReachedSentence)
        self.voiceSema.release()
        print "Path index " + str(self.pathListIndex)
##        time.sleep(1)
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)


    def provideNexNodeDirections(self) :
        nexNode =  self.pathList[self.pathListIndex + 1]
        nexNodeName = self.comMap[self.mapNumber].getLocationName(nexNode)
        nextNodeSentence = "Next is" + nexNodeName + "."
        print nextNodeSentence
        self.voiceQueue.append(nextNodeSentence)
        self.voiceSema.release()

    # returns 1 for right (and straight ahead), 2 for left
    def getGeneralTurnDirection(self) :
        direction = self.nodeNavi.getTurnAngle()
        if direction > 0 :
            return 1
        elif direction < 0 :
            return 2
        else :
            return 0

    # before moving to next node, ensure turn in correct direction
    # returns True if correct, False otherwise
    def ensureTurnedCorrectDirection(self) :
        directionToHead = self.nodeNavi.getTurnAngle()
        if (math.fabs(directionToHead) > self.ANGLE_TOLERANCE) :
            if (directionToHead > 0) :
                sentence = "Right %.0f." %(directionToHead)
                print sentence
                if time.time() - self.prev_message_time > self.message_delay:
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
                    self.prev_message_time = time.time()
            elif (directionToHead < 0) :
                sentence = "Left %.0f." %(math.fabs(directionToHead))
                print sentence
                if time.time() - self.prev_message_time > self.message_delay:
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
                    self.prev_message_time = time.time()
            return False
        else :
            sentence = "Move straight ahead"
            return True

    def ignoreNodeObstacle(self) :
        distTo = distAngleCalc.distance(self.curX, self.curY, self.nexX, self.nexY)
        if distTo < self.maxTolerance :
            print "PSEUDO Node reached!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            self.pathListIndex += 1
            self.alertNodeReached()
            if self.pathListIndex < (len(self.pathList) - 1) :
                self.updatePrevNexCoord()
                self.provideNexNodeDirections()
                self.angleCorrect = False
            else :
                sentence = "Navigation complete."
                print sentence
                self.voiceQueue.flush()
                self.voiceQueue.append(sentence)
                self.voiceSema.release()
                return True


    # returns true if navigation is complete
    def fullNavigate(self) :
        if self.angleCorrect is False :
            self.angleCorrect = self.ensureTurnedCorrectDirection()
            return False
        else :
            if ((self.obstacleClearedSteps - self.obstacleEncounteredSteps) <= self.MAX_STEPS):
                angleDisp = self.obstStartHeading - self.obstEndHeading
                self.nodeNavi.setPrevObstacleHeading(angleDisp)
            else :
                self.nodeNavi.setPrevObstacleHeading(360)
##
            curNode =  self.pathList[self.pathListIndex + 1]
            curNodeName = self.comMap[self.mapNumber].getLocationName(curNode)
            print "next node name is: " + str(curNodeName)
            isNodeReached = self.nodeNavi.navigate()

            if isNodeReached == 1 :
                print "NODE REACHED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                self.pathListIndex += 1
                self.alertNodeReached()
                if self.pathListIndex < (len(self.pathList) - 1) :
                    self.updatePrevNexCoord()
                    self.provideNexNodeDirections()
                    self.angleCorrect = False
                else :
                    sentence = "Navigation complete."
                    print sentence
                    self.voiceQueue.flush()
                    self.voiceQueue.append(sentence)
                    self.voiceSema.release()
                    return True
        return False
        
        
