import math
import distAngleCalc
from p2pNavi import navigation
from jsonParsing import mapParser
from dijkstra import pathFinder
##import RPi.GPIO as GPIO
import math
import time

# API:
# generateFullPath(startBuilding, startLevel, start, endBuilding, endLevel, end)
# 0 for com1L2, 1 for com2L2, 2 for com2L3
# updateCurLocation(x, y, heading)
# updateEncounterSteps(numSteps)
# fullNavigate()
# getGeneralTurnDirection()
# reroutePath()
# hasNextPath()
# switchToNextPathList()
# getNorthDifference()
# getFirstCoordinates()
# isDifferentLevel()
# feedbackWalking(currentSteps)


class fullNavi(object) :
    def __init__(self, voiceQueue, voiceSema) :
        self.prev_message_time_turn = 0
        self.prev_message_time_str = 0
        self.message_delay = 0
        self.voiceQueue = voiceQueue
        self.voiceSema = voiceSema
        self.ANGLE_TOLERANCE = 0
        
        self.pathFind = pathFinder()
        self.hasAnotherPath = False
        self.hasTwoPaths = False
        self.hasThreePaths = False
        self.startBuilding = None
        self.endBuilding = None
        self.startLevel = 0
        self.endLevel = 0
        self.midBuilding = None
        self.midLevel = None
        self.mapNumber = 0          # index of map in comMap list
        self.startLocation = 0
        self.endLocation = 0
        self.curX = 0               # cm
        self.curY = 0               # cm
        self.heading = 0            # -180 to 180 degrees

        # used to feedback steps to user
        self.walkingCount = 0
        self.WALKING_VIBRATE_DURATION = 0.1

        # tolerance
        self.maxTolerance = 200

        # list of json parsing maps
        self.comMap = []
        # path lists
        self.pathList = []
        self.pathList2 = []
        self.pathList3 = []
        # north of cuurent map
        self.curMapNorth = 0

        # if connection between the building has stairs
        self.hasStairs1 = 0
        self.hasStairs2 = 0
        
        # parameters to set when switching to new map
        self.hasStairs = 0
        self.northDifference = 0
        self.xFirst = None
        self.yFirst = None

        self.pathListIndex = 0
        self.northAt = 0            # 0 to 360 degrees
        self.prevX = 0              # cm
        self.prevY = 0              # cm
        self.nexX = 0               # cm
        self.nexY = 0               # cm
        self.nodeNavi = navigation(self.voiceQueue, self.voiceSema)

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

    # when a step is detected, right-side vibration motor will activate
    def feedbackWalking(self, currentSteps) :
        if currentSteps > self.walkingCount :
            GPIO.output(self.rightPin, True)
            time.sleep(self.WALKING_VIBRATE_DURATION)
            GPIO.output(self.rightPin, False)

        self.walkingCount = currentSteps

    def hasNextPath (self) :
        return self.hasAnotherPath

    def getNorthDifference(self) :
        return self.northDifference

    def getFirstCoordinates(self) :
        return (self.xFirst, self.yFirst)

    # returns 1 or 0
    def isDifferentLevel(self) :
        return self.hasStairs

    def generateFullPath(self, startBuilding, startLevel, start,
                         endBuilding, endLevel, end) :
        self.mapNumber = 0
        self.pathListIndex = 0
        self.comMap.append(mapParser())
        self.comMap[self.mapNumber].setMap(startBuilding, startLevel)
        self.startBuilding = startBuilding
        self.startLevel = startLevel
        self.endBuilding = endBuilding
        self.endLevel = endLevel
        self.startLocation = start - 1
        self.endLocation = end - 1

        if((startBuilding == endBuilding) and (startLevel == endLevel)) :
            self.generateOnePath()
        elif ((startBuilding != endBuilding) and (startLevel != endLevel)) :
            self.midBuilding = "com2"
            self.midLevel = "2"
            self.generateThreePaths()
        else :
            self.generateTwoPaths()

        # print pathlists
        print "[",
        for i in self.pathList :
            print str(i+1) + ", ",
        print "]"
    
        print "[",
        for i in self.pathList2 :
            print str(i+1) + ", ",
        print "]"

        print "[",
        for i in self.pathList3 :
            print str(i+1) + ", ",
        print "]"
        
        self.northAt = 0
        self.curMapNorth = self.comMap[self.mapNumber].getNorthAt()
        if (len(self.pathList) == 1) :
            self.alertNodeReached()
            return
        self.updatePrevNexCoord()
        self.provideNexNodeDirections()

    def generateOnePath(self) :
        self.hasAnotherPath = False
        self.hasTwoPaths = False
        self.hasThreePaths = False
        self.pathFind.setMap(self.startBuilding, self.startLevel)
        self.pathList = self.pathFind.getPath(self.startLocation, self.endLocation)
        
    def generateTwoPaths(self) :
        self.hasAnotherPath = True
        self.hasTwoPaths = True
        self.hasThreePaths = False
        self.pathFind.setMap(self.startBuilding, self.startLevel)
        conList1 = self.comMap[self.mapNumber].getNodeID()
        # append 2nd map
        self.comMap.append(mapParser())
        self.comMap[self.mapNumber + 1].setMap(self.endBuilding, self.endLevel)
        conList2 = self.comMap[self.mapNumber + 1].getNodeID()
        
        midEnd, midStart, self.hasStairs1 = self.getBuildingConnection(conList1, conList2)
        if (midEnd != 9999 and midStart != 9999) :
            self.pathList = self.pathFind.getPath(self.startLocation, midEnd)
            self.pathFind.setMap(self.endBuilding, self.endLevel)
            self.pathList2 = self.pathFind.getPath(midStart, self.endLocation)

    def generateThreePaths(self) :
        self.hasAnotherPath = True
        self.hasTwoPaths = True
        self.hasThreePaths = True
        self.pathFind.setMap(self.startBuilding, self.startLevel)
        conList1 = self.comMap[self.mapNumber].getNodeID()
        # append 2nd map
        self.comMap.append(mapParser())
        self.comMap[self.mapNumber + 1].setMap(self.midBuilding, self.midLevel)
        conList2 = self.comMap[self.mapNumber + 1].getNodeID()
        # append 3rd map
        self.comMap.append(mapParser())
        self.comMap[self.mapNumber + 2].setMap(self.endBuilding, self.endLevel)
        conList3 = self.comMap[self.mapNumber + 2].getNodeID()
        
        midEnd1, midStart1, self.hasStairs1 = self.getBuildingConnection(conList1, conList2)
        midEnd2, midStart2, self.hasStairs2 = self.getBuildingConnection(conList2, conList3)
        if (midEnd1 != 9999 and midStart1 != 9999) :
            self.pathList = self.pathFind.getPath(self.startLocation, midEnd1)
            self.pathFind.setMap(self.midBuilding, self.midLevel)
            self.pathList2 = self.pathFind.getPath(midStart1, midEnd2)
            self.pathFind.setMap(self.endBuilding, self.endLevel)
            self.pathList3 = self.pathFind.getPath(midStart2, self.endLocation)
          

    # returns the index of the connection node, 9999 if not found
    def getBuildingConnection(self, list1, list2) :
        for i in xrange(len(list1)) :
            for j in xrange(len(list2)) :
                if ((list1[i][0] == list2[j][1]) and
                    (list1[i][1] == list2[j][0])) :
                    return ((list1[i][2], list2[j][2], list1[i][3]))
        return (9999, 9999, 0)

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
        if self.voiceQueue.append_high(sentence, time.time()):
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
        nodeReachedSentence = "You reached node " + str(curNodeName) + "." # str(prevNode + 1) + ", " + str(curNodeName) + "."
        print nodeReachedSentence
        if self.voiceQueue.append_high(nodeReachedSentence, time.time()):
           self.voiceSema.release()
        print "Path index " + str(self.pathListIndex)
##        time.sleep(1)
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)


    def provideNexNodeDirections(self) :
        nexNode =  self.pathList[self.pathListIndex + 1]
        nexNodeName = self.comMap[self.mapNumber].getLocationName(nexNode)
        nextNodeSentence = "Next is " + str(nexNode+1) + ", " + nexNodeName + "."
        print nextNodeSentence
        if self.voiceQueue.append_high(nextNodeSentence, time.time()):
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

    def ignoreNodeObstacle(self) :
        distTo = distAngleCalc.distance(self.curX, self.curY, self.nexX, self.nexY)
        if distTo < self.maxTolerance :
            sentence = "Node Reached."
            print sentence
            if self.voiceQueue.append_high(sentence, time.time()):
                self.voiceSema.release()
            self.pathListIndex += 1
            self.alertNodeReached()
            if self.pathListIndex < (len(self.pathList) - 1) :
                self.updatePrevNexCoord()
                self.provideNexNodeDirections()
            else :
                sentence = "Navigation complete."
                print sentence
                if self.voiceQueue.append_high(sentence, time.time()):
                   self.voiceSema.release()
                self.prev_message_time_turn = time.time()

                return True

    def switchToNextPathList(self) :
        if self.hasTwoPaths is True :
            self.hasTwoPaths = False
            self.switchToPathList2()
        else :
            self.switchToPathList3()

    # prepare for traversing the second building/level
    def switchToPathList2(self) :
        sentence = "New building/level!"
        print sentence
        if self.voiceQueue.append_high(sentence, time.time()):
           self.voiceSema.release()
        self.prev_message_time_turn = time.time()

        if self.hasThreePaths is False :
            self.hasAnotherPath = False
        self.pathList = self.pathList2
        self.mapNumber += 1
        self.pathListIndex = 0
        nexMapNorth = self.comMap[self.mapNumber].getNorthAt()
        self.northDifference = nexMapNorth - self.curMapNorth
        self.curMapNorth = nexMapNorth
        self.northAt = 0
        self.hasStairs = self.hasStairs1
        curNode =  self.pathList[self.pathListIndex]
        curNodeName = self.comMap[self.mapNumber].getLocationName(curNode)
        sentence = "At " + curNodeName + "."
        print sentence
        if self.voiceQueue.append_high(sentence, time.time()):
           self.voiceSema.release()
        self.prev_message_time_turn = time.time()

        self.xFirst = int(self.comMap[self.mapNumber].getLocationXCoord(curNode))
        self.yFirst = int(self.comMap[self.mapNumber].getLocationYCoord(curNode))
        if (len(self.pathList) == 1) :
            self.alertNodeReached()
            return
        self.updatePrevNexCoord()
        self.provideNexNodeDirections()


        # prepare for traversing the second building/level
    def switchToPathList3(self) :
        sentence = "New building/level!"
        print sentence
        if self.voiceQueue.append_high(sentence, time.time()):
           self.voiceSema.release()
        self.prev_message_time_turn = time.time()

        self.hasAnotherPath = False
        self.pathList = self.pathList3
        self.mapNumber += 1
        self.pathListIndex = 0
        nexMapNorth = self.comMap[self.mapNumber].getNorthAt()
        self.northDifference = nexMapNorth - self.curMapNorth
        self.curMapNorth = nexMapNorth
        self.northAt = 0
        self.hasStairs = self.hasStairs2
        curNode =  self.pathList[self.pathListIndex]
        curNodeName = self.comMap[self.mapNumber].getLocationName(curNode)
        sentence = "At " + str(curNode+1) + ", " + curNodeName + "."
        print sentence
        if self.voiceQueue.append_high(sentence, time.time()):
           self.voiceSema.release()
        self.prev_message_time_turn = time.time()

        self.xFirst = int(self.comMap[self.mapNumber].getLocationXCoord(curNode))
        self.yFirst = int(self.comMap[self.mapNumber].getLocationYCoord(curNode))

        if (len(self.pathList) == 1) :
            self.alertNodeReached()
            return
        self.updatePrevNexCoord()
        self.provideNexNodeDirections()

        
    # returns true if navigation is complete
    def fullNavigate(self) :
        if (((len(self.pathList) == 1) or
             (self.pathListIndex >= (len(self.pathList) - 1)))) :
            self.alertNodeReached()
            return True
        
        curNode = self.pathList[self.pathListIndex + 1]
        curNodeName = self.comMap[self.mapNumber].getLocationName(curNode)
        print "next node is " + str(curNode + 1) + ", name is: " + str(curNodeName)
        isNodeReached = self.nodeNavi.navigate()

        if isNodeReached == 1 :
            sentence = "Node Reached."
            print sentence
            if self.voiceQueue.append_high(sentence, time.time()):
               self.voiceSema.release()
            self.prev_message_time_turn = time.time()

            self.pathListIndex += 1
            self.alertNodeReached()
            if self.pathListIndex < (len(self.pathList) - 1) :
                self.updatePrevNexCoord()
                self.provideNexNodeDirections()
            else :
                if self.hasAnotherPath is False :
                    sentence = "Navigation complete."
                else :
                    sentence = "Reached end of building"
                print sentence
                if self.voiceQueue.append_high(sentence, time.time()):
                   self.voiceSema.release()
                self.prev_message_time_turn = time.time()
                return True
        return False
