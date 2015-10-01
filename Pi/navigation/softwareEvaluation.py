import distAngleCalc
from p2pNavi import navigation
from jsonParsing import mapParser
from dijkstra import pathFinder

#Takes in the building name, start and end point
#Prompts for current coordinates and bearing (-180 to 180)
#Returns the turning angle and distance to the next node

nextNode = 0

def getDistToNearestNode(curX, curY) :
    global nextNode
    nearDist = 100000
    for i in pathList :
        nodeX = comMap.getLocationXCoord(i)
        nodeY = comMap.getLocationYCoord(i)
        distTo = distAngleCalc.distance(curX, curY, nodeX, nodeY)
        if distTo < nearDist :
            nextNode = i
            nearDist = distTo
    return nearDist


def getTurnDirection(curX, curY, nexX, nexY, curAngle, northAt) :
    directionToHead = distAngleCalc.calcAngle(curX, curY, nexX, nexY, northAt)
    turnAngle = directionToHead - curAngle 
    if turnAngle > 180 :
        turnAngle -= 360
    elif turnAngle <= -180 :
        turnAngle += 360
    return turnAngle
            

buildingName = str(raw_input("Enter building name: "))
levelNumber = int(raw_input("Enter level number: "))
startIndex = int(raw_input("Enter starting node: "))
endIndex = int(raw_input("Enter ending node: "))

findPath = pathFinder()
findPath.setMap(buildingName, levelNumber)
pathList = findPath.getPath(startIndex, endIndex)
comMap = mapParser()
comMap.setMap(buildingName, levelNumber)


numNodes = len(pathList)
print "Node list: [",
for i in xrange(numNodes) :
    if i != (numNodes - 1) :
        print str(pathList[i] + 1) + ", ",
    else :
        print str(pathList[i] + 1),
print "]"

northAt = comMap.getNorthAt()
xDest = comMap.getLocationXCoord(endIndex)
yDest = comMap.getLocationYCoord(endIndex)


x = int(raw_input("Enter x: "))
y = int(raw_input("Enter y: "))
heading = int(raw_input("Enter heading: "))

while x != xDest or y != yDest :
    distance = getDistToNearestNode(x, y)
    nexX = comMap.getLocationXCoord(nextNode)
    nexY = comMap.getLocationYCoord(nextNode)
    turnAngle = getTurnDirection(x, y, nexX, nexY, heading, northAt)
    
    print "Nearest node: " + str(nextNode + 1)
    if(distance == 0) :
        print "Turning angle: " + "0"
    else :
        print "Turning angle: " + str(turnAngle)
    print "Distance to nearest node: " + str(distance) + "cm"    

    x = int(raw_input("Enter x: "))
    y = int(raw_input("Enter y: "))
    heading = int(raw_input("Enter heading: "))

    
