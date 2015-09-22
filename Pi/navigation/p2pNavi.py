from jsonParsing import mapParser
import distAngleCalc
import math
#import RPi.GPIO as GPIO

# set up GPIO using BCM numbering
#GPIO.setmode(GPIO.BCM)

# setup GPIO using Board numbering
#GPIO.setmode(GPIO.BOARD)

# GPIO Pins 11 and 13 set to pull up
# Pin 11 is for left, Pin 13 is for right
##GPIO.setup(11, GPIO.OUT)
##GPIO.setup(13, GPIO.OUT)
##
### initially turned off
##GPIO.output(11, True)
##GPIO.output(13, True)

# calculates which direction (left or right to turn)
def getTurnDirection(curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt) :
    directToHead = distAngleCalc.calcAngle(
            curXCoord, curYCoord, nexXCoord, nexYCoord, northAt)
    # convert back to 0 - 360 degrees domain
    if directToHead < 0 :
        directToHead += 360

    if directToHead > curAngle :
        if (directToHead - curAngle) < 180 :
            return "right"
            #GPIO.output(13, False)
            #GPIO.output(11, True)
        else :
            #GPIO.output(11, False)
            #GPIO.output(13, True)
            return "left"
    else :
        if (curAngle - directToHead) < 180 :
            #GPIO.output(11, False)
            #GPIO.output(13, True)            
            return "left"
        else :
            #GPIO.output(13, False)
            #GPIO.output(11, True)
            return "right"


# calculates the x-coordinate the person is supposed to be at,
# based on his current y-coordinate
def getEqnXDeviation(prevX, prevY, nexX, nexY, curX, curY) :
    slope = (nexY - prevY) / (nexX - prevX)
    correctX = nexX - ((nexY - curY) / slope)
    return math.fabs(curX - correctX)

# calculates the y-coordinate the person is supposed to be
# based on his current x-coordinate
def getEqnYDeviation(prevX, prevY, nexX, nexY, curX, curY) :
    slope = (nexY - prevY) / (nexX - prevX)
    correctY = nexY - ((nexX - curX) / slope)
    return math.fabs(curY - correctY)
        

# previous node's coordinates
prevXCoord = 0
prevYCoord = 0

#prevXCoord = com1L2.getLocationXCoord(prev)
#prevYCoord = com1L2.getLocationYCoord(prev)

# next node's coordinates
nexXCoord = 150
nexYCoord = 150

# north
northAt = 0

#com1L2 = mapParser("com1L2")
#nexXCoord = com1L2.getLocationXCoord(nex)
#nexYCoord = com1L2.getLocationYCoord(nex)

# current coordinates
curXCoord = 0
curYCoord = 0

# deviation tolerance
maxDeviation = 50

# vicinity tolerance
maxTolerance = 10


pathXDisp = math.fabs(nexXCoord - prevXCoord)  
pathYDisp = math.fabs(nexYCoord - prevYCoord)

curXDisp = pathXDisp
curYDisp = pathYDisp

# direction to move
turn = None

# loop until the destination is reached
while (curXDisp > maxTolerance and curYDisp > maxTolerance) :
    curXCoord = float(raw_input("Enter x coordinate: "))
    curYCoord = float(raw_input("Enter y coordinate: "))
    curAngle = float(raw_input("Enter angle direction: "))

    curXDisp = math.fabs(nexXCoord - curXCoord)  
    curYDisp = math.fabs(nexYCoord - curYCoord)

    turn = None
    # check if the path to be traversed is more horizontal or vertical
    # if horizontal, check the y displacement
    # if vertical, check the x displacement
    # if neither, check the current x and y displacement and use the larger

    # horizontal and vertical displacements from correct path
    xStray = getEqnXDeviation(prevXCoord, prevYCoord,
                                     nexXCoord, nexYCoord, curXCoord, curYCoord)

    yStray = getEqnXDeviation(prevXCoord, prevYCoord,
                                     nexXCoord, nexYCoord, curXCoord, curYCoord)

    if pathXDisp > pathYDisp :
        if yStray > maxDeviation :
            print "strayed in y-direction by: " + str(yStray)
            turn = getTurnDirection(
                curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt)          
    elif pathXDisp < pathYDisp :
        if xStray > maxDeviation :
            print "strayed in x-direction by: " + str(xStray)
            turn = getTurnDirection(
                curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt) 
    else :
        xTravelled = math.fabs(curXCoord - prevXCoord)
        yTravelled = math.fabs(curYCoord - prevYCoord)
        if xTravelled > yTravelled and yStray > maxDeviation :            
            print "strayed in y-direction by: " + str(yStray)
            turn = getTurnDirection(
                curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt)
        elif yTravelled < xTravelled and xStray > maxDeviation :
            print "strayed in x-direction by: " + str(xStray)            
            turn = getTurnDirection(
                curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt)

    if not turn :
        print "Keep going in your current direction!"
##        GPIO.output(11, True)
##        GPIO.output(13, True)
    elif turn == "right" :
        print "Move to the right!"
##        GPIO.output(13, False)
##        GPIO.output(11, True)
    elif turn == "left" :
        print "Move to the left!"
##        GPIO.output(11, False)
##        GPIO.output(13, True)
        

