import obstacleAvoidance
import distAngleCalc
import math
#import RPi.GPIO as GPIO

# Pin 11 is for left, Pin 13 is for right
leftPin = 11
rightPin = 13

# set up GPIO using BCM numbering
##GPIO.setmode(GPIO.BCM)

# setup GPIO using Board numbering
##GPIO.setmode(GPIO.BOARD)

# GPIO Pins 11 and 13 set to pull up
##GPIO.setup(leftPin, GPIO.OUT)
##GPIO.setup(righttPin, GPIO.OUT)

### initially turned off
##GPIO.output(leftPin, True)
##GPIO.output(rightPin, True)

# previous node's coordinates
prevXCoord = 0
prevYCoord = 0

# next node's coordinates
nexXCoord = 150
nexYCoord = 150

# north
northAt = 0

# current coordinates
curXCoord = 0
curYCoord = 0

# deviation tolerance
maxDeviation = 50
# vicinity tolerance
maxTolerance = 10
# angle tolerance
angleTolerance = 15


# calculates which direction (left or right) to turn
def getTurnDirection(curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt) :
    directionToHead = distAngleCalc.calcAngle(
            curXCoord, curYCoord, nexXCoord, nexYCoord, northAt)
    print ("direction to head: " + str(directionToHead) +
           " current angle: " + str(curAngle))
    # convert back to 0 - 360 degrees domain
    if directionToHead < 0 :
        directionToHead += 360
    
    if math.fabs(directionToHead - curAngle) < angleTolerance :
        return "straight"
        print "MOVE " + str(math.fabs(directionToHead - curAngle))
    elif directionToHead > curAngle :
        if (directionToHead - curAngle) < 180 :
            return "right"
        else :
            return "left"
    elif directionToHead < curAngle :
        if (curAngle - directionToHead) < 180 :
            return "left"
        else :
            return "right"


# calculates the deviation from x-coordinate the person
# is supposed to be, based on his current y-coordinate
def getEqnXDeviation(prevX, prevY, nexX, nexY, curX, curY) :
    if (nexY - prevY) == 0 or (nexX - prevX) == 0 :
        return math.fabs(nexX - curX)
    else :
        slope = (nexY - prevY) / (nexX - prevX)
        correctX = nexX - ((nexY - curY) / slope)
        return math.fabs(curX - correctX)

# calculates the y-coordinate the person is supposed to be
# based on his current x-coordinate
def getEqnYDeviation(prevX, prevY, nexX, nexY, curX, curY) :
    if (nexY - prevY) == 0 or (nexX - prevX) == 0 :
        return math.fabs(nexY - curY)
    else :
        slope = (nexY - prevY) / (nexX - prevX)
        correctY = nexY - ((nexX - curX) / slope)
        return math.fabs(curY - correctY)


pathXDisp = math.fabs(nexXCoord - prevXCoord)  
pathYDisp = math.fabs(nexYCoord - prevYCoord)

curXDisp = pathXDisp
curYDisp = pathYDisp

# direction to move
turn = None

# loop until the destination is reached
# angle input from -180 to 180
while ((curXDisp > maxTolerance) or (curYDisp > maxTolerance)) :
    curXCoord = float(raw_input("Enter current x coordinate: "))
    curYCoord = float(raw_input("Enter current y coordinate: "))
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

    yStray = getEqnYDeviation(prevXCoord, prevYCoord,
                                     nexXCoord, nexYCoord, curXCoord, curYCoord)
    print "X stray = " + str(xStray) + " Y stray = " + str(yStray)
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
            print "strayed by: " + str(yStray)
            turn = getTurnDirection(
                curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt)
        elif yTravelled > xTravelled and xStray > maxDeviation :
            print "strayed by: " + str(xStray)
            turn = getTurnDirection(
                curXCoord, curYCoord, nexXCoord, nexYCoord, curAngle, northAt)
    
    if turn == "right" :
        print "Move towards the right!"
##        GPIO.output(rightPin, False)
##        GPIO.output(leftPin, True)
    elif turn == "left" :
        print "Move towards the left!"
##        GPIO.output(leftPin, False)
##        GPIO.output(rightPin, True)
    else :
        print "Keep going in your current direction!"
##        GPIO.output(leftPin, True)
##        GPIO.output(rightPin, True)

print "X disp = " + str(curXDisp) + " Y disp = " + str(curYDisp)

