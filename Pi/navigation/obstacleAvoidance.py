import time
#import RPi.GPIO as GPIO

# API:
# avoidObstacle()

FRONT_OBSTACLE_DISTANCE = 60
SIDE_WALL_DISTANCE = 100
SIDE_OBSTACLE_DISTANCE = 70
VIBRATE_DURATION = 3

# Pin 9 is for left, Pin 10 is for right
leftPin = 9
rightPin = 10

lastTurnedDirection = 0

# set up GPIO using BCM numbering
##GPIO.setmode(GPIO.BCM)

# GPIO Pins set to pull up
##GPIO.setup(leftPin, GPIO.OUT)
##GPIO.setup(righttPin, GPIO.OUT)

### initially turned off
##GPIO.output(leftPin, True)
##GPIO.output(rightPin, True)

# dummy function to get sonar data
def getSonarData(input) :
    return int(raw_input("Enter value of " + input + " sonar: "))


def turnFromObstacle() :
    print "ENTER TURN FROM OBSTACLE"
    global lastTurnedDirection
    lastTurnedDirection = getSideToTurn()
    if lastTurnedDirection == 1 :
##        GPIO.output(leftPin, True)
##        GPIO.output(rightPin, False)
         print "Turn right! Right vibrator activated"
    elif lastTurnedDirection == 2 :
##        GPIO.output(leftPin, False)
##        GPIO.output(rightPin, True)
        print "Turn left! Left vibrator activated"
    else :
##        GPIO.output(leftPin, False)
##        GPIO.output(rightPin, False)
        print "Both side blocked! Both vibration motors activated"
    
# choose which direction to turn, default turn right
# returns 1 for right, 2 for left, 0 if both sides blocked
def getSideToTurn() :
    if getSonarData("rightShoulder") > SIDE_WALL_DISTANCE :
        return 1
    elif getSonarData("leftShoulder") > SIDE_WALL_DISTANCE :
        return 2
    else :
        return 0


def avoidObstacle() :
    print "ENTER AVOID OBSTACLE"
    fSonarTL = getSonarData("topLeft")
    fSonarTR = getSonarData("topRight")
    fSonarC = getSonarData("center")

    if ((fSonarTL < FRONT_OBSTACLE_DISTANCE) or
        (fSonarTR < FRONT_OBSTACLE_DISTANCE) or
        (fSonarC < FRONT_OBSTACLE_DISTANCE)) :

##        GPIO.output(leftPin, False)
##        GPIO.output(rightPin, False)
        print "Obstacle encountered! Vibrate both sensors for 3 seconds"
        # wait for VIBRATE_DURATION before proceeding
        time.sleep(VIBRATE_DURATION)
    else :
        return


    while ((fSonarTL < FRONT_OBSTACLE_DISTANCE) or
        (fSonarTR < FRONT_OBSTACLE_DISTANCE) or
        (fSonarC < FRONT_OBSTACLE_DISTANCE)) :

        turnFromObstacle()

        fSonarTL = getSonarData("topLeft")
        fSonarTR = getSonarData("topRight")
        fSonarC = getSonarData("center")


    # turn off vibration motors
##    GPIO.output(leftPin, True)
##    GPIO.output(rightPin, True)
    checkObstacleCleared()


# monitor the obstacle from the side while the person walks forward,
# until the obstacle is completely cleared	
def checkObstacleCleared() :
    print "ENTER CHECK OBSTACLE CLEARED"
    if(lastTurnedDirection == 1) :
        sideSonar = getSonarData("leftShoulder")
    else :
        sideSonar = getSonarData("rightShoulder")

    while(sideSonar < SIDE_OBSTACLE_DISTANCE) :
        fSonarTL = getSonarData("topLeft")
        fSonarTR = getSonarData("topRight")
        fSonarC = getSonarData("center")
        
        # if a front obstacle is encountered
        if ((fSonarTL < FRONT_OBSTACLE_DISTANCE) or
            (fSonarTR < FRONT_OBSTACLE_DISTANCE) or
            (fSonarC < FRONT_OBSTACLE_DISTANCE)) :
            avoidObstacle();

        if(lastTurnedDirection == 1) :
            sideSonar = getSonarData("leftShoulder")
        else :
            sideSonar = getSonarData("rightShoulder")

 
