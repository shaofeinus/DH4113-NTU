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
# isInitialAngleCorrect()
# fullNavigate()

class fullNavi(object) :
    def __init__(self) :
        self.ANGLE_TOLERANCE = 13
        self.comMap = []
        self.buildingName = None
        self.levelNumber = 0
        self.mapNumber = 0          # index of map in comMap list
        self.startLocation = 0
        self.endLocation = 0
        self.curX = 0               # cm
        self.curY = 0               # cm
        self.heading = 0            # -180 to 180 degrees
        
        self.pathList = []
        self.pathListIndex = 0
        self.northAt = 0            # 0 to 360 degrees
        self.prevX = 0              # cm
        self.prevY = 0              # cm
        self.nexX = 0               # cm
        self.nexY = 0               # cm
        self.nodeNavi = navigation()
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

    def updatePrevNexCoord(self) :
        prevNode = self.pathList[self.pathListIndex]
        nexNode =  self.pathList[self.pathListIndex + 1]
        self.prevX = int(self.comMap[self.mapNumber].getLocationXCoord(prevNode))
        self.prevY = int(self.comMap[self.mapNumber].getLocationYCoord(prevNode))
        self.nexX = int(self.comMap[self.mapNumber].getLocationXCoord(nexNode))
        self.nexY = int(self.comMap[self.mapNumber].getLocationYCoord(nexNode))
        self.nodeNavi.setNorthAt(self.northAt)
        self.nodeNavi.setPrevCoordinates(self.prevX, self.prevY)
        self.nodeNavi.setNexCoordinates(self.nexX, self.nexY)


    def alertNodeReached(self) :
##        GPIO.output(self.leftPin, True)
##        GPIO.output(self.rightPin, True)
        prevNode = self.pathList[self.pathListIndex]
        curNodeName = self.comMap[self.mapNumber].getLocationName(prevNode)
        print "You have reached " + curNodeName + "!"
        print "PATHLIST INDEX is: " + str(self.pathListIndex)
##        time.sleep(1)
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)      

    def provideNexNodeDirections(self) :
        nexNode =  self.pathList[self.pathListIndex + 1]
        nexNodeName = self.comMap[self.mapNumber].getLocationName(nexNode)
        print "Next node is: " + nexNodeName

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
                print "Turn right by " + str(directionToHead) + " degrees"
            elif (directionToHead < 0) :
                print "Turn left by " + str(math.fabs(directionToHead)) + " degrees"
            return False
        else :
            print "Move straight ahead"
            return True

    # returns true if navigation is complete
    def fullNavigate(self) :
        if self.angleCorrect is False :
            self.angleCorrect = self.ensureTurnedCorrectDirection()
            return False
        else :
            isNodeReached = self.nodeNavi.navigate()

            if isNodeReached == 1 :
                self.pathListIndex += 1
                self.alertNodeReached()
                if self.pathListIndex < (len(self.pathList) - 1) :
                    self.updatePrevNexCoord()
                    self.provideNexNodeDirections()
                    self.angleCorrect = False
                else :
                    print "NAVIGATION COMPLETE!!!"
                    return True
        return False
        
        
