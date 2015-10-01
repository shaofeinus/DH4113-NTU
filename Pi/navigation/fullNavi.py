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
# fullNavigate()

class fullNavi(object) :
    def __init__(self) :
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

    def generateFullPath(self, buildingName, levelNumber, start, end) :
        self.mapNumber = 0
        self.comMap.append(mapParser())
        self.comMap[self.mapNumber].setMap(buildingName, levelNumber)
        self.startLocation = start
        self.endLocation = end
        self.buildingName = buildingName
        self.levelNumber = levelNumber
        pathFind = pathFinder()
        pathFind.setMap(buildingName, levelNumber)
        self.pathList = pathFind.getPath(start, end)
        self.northAt = self.comMap[self.mapNumber].getNorthAt()
        self.updatePrevNexCoord()
        print "Path: " + str(self.pathList)

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
##        time.sleep(1)
##        GPIO.output(self.leftPin, False)
##        GPIO.output(self.rightPin, False)      

    def provideNexNodeDirections(self) :
        nexNode =  self.pathList[self.pathListIndex + 1]
        nexNodeName = self.comMap[self.mapNumber].getLocationName(nexNode)
        print "Next node is: " + nexNodeName
        directionToHead = self.nodeNavi.getTurnAngle()
        if directionToHead > 0 :
            print "Turn right by " + str(directionToHead) + " degrees"
        elif directionToHead < 0 :
            print "Turn left by " + str(math.fabs(directionToHead)) + " degrees"
        else :
            print "Move straight ahead"

    def fullNavigate(self) :
        isNodeReached = self.nodeNavi.navigate()
        if isNodeReached == 1 :
            self.pathListIndex += 1
            self.alertNodeReached()
            if self.pathListIndex < (len(self.pathList) - 1) :
                self.updatePrevNexCoord()
                self.provideNexNodeDirections()
            else :
                print "NAVIGATION COMPLETE!!!"
        
