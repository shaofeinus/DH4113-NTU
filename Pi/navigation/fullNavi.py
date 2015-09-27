import distAngleCalc
from p2pNavi import navigation
from jsonParsing import mapParser
from dijkstra import pathFinder
import math
import time
#import RPi.GPIO as GPIO

# API:
# generateFullPath(building, start, end)
# 0 for com1L2, 1 for com2L2, 2 for com2L3
# updateCurLocation(x, y, heading)
# fullNavigate()

class fullNavi(object) :
    def __init__(self) :
        self.comMap = []
        self.comMap.append(mapParser("com1L2"))
        self.comMap.append(mapParser("com2L2"))
        self.comMap.append(mapParser("com2L3"))
        
        # 0 for com1L2, 1 for com2L2, 2 for com2L3
        self.mapNumber = 0
        self.startLocation = 0
        self.endLocation = 0
        self.curX = 0
        self.curY = 0
        self.heading = 0
        
        self.pathList = []
        self.pathListIndex = 0
        self.northAt = 0            # 0 to 360 degrees
        self.prevX = 0              # cm
        self.prevY = 0              # cm
        self.nexX = 0               # cm
        self.nexY = 0               # cm
        self.nodeNavi = navigation()

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

    def updateCurLocation(self, x, y, heading) :
        self.curX = x
        self.curY = y
        self.heading = heading
        self.nodeNavi.updateCurCoord(x, y)
        self.nodeNavi.updateHeading(heading)

    def generateFullPath(self, building, start, end) :
        self.startLocation = start
        self.endLocation = end
        self.mapNumber = building
        pathFind = pathFinder()
        pathFind.setMap(building)
        self.pathList = pathFind.getPath(start, end)
        self.northAt = self.comMap[building].getNorthAt()
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
##        GPIO.output(leftPin, False)
##        GPIO.output(rightPin, False)
        prevNode = self.pathList[self.pathListIndex]
        curNodeName = self.comMap[self.mapNumber].getLocationName(prevNode)
        print "You have reached " + curNodeName + "!"
##        time.sleep(1)
##        GPIO.output(leftPin, True)
##        GPIO.output(rightPin, True)      

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
        
