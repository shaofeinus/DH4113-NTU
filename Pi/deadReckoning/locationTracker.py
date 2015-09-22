import math
import pedometer
import compass

__author__ = 'Shao Fei'


class LocationTracker:

    STEP_DISTANCE = 0.5     # in m

    def __init__(self, pedometer, compass, initX, initY):
        # Dummies
        self.currX = initX
        self.currY = initY
        self.pedometer = pedometer
        self.compass = compass
        self.totalSteps = 0
        self.totalDistance = 0

    # Public
    def getLocation(self):
        return {'x': self.currX, 'y': self.currY}

    # Public
    def getTotalSteps(self):
        return self.totalSteps

    # Public
    def getTotalDistance(self):
        return self.totalDistance

    # Public
    def getHeadingInDeg(self):
        return self.compass.getHeadingInDeg()

    # Public
    def setLocation(self, x, y):
        self.currX = x
        self.currY = y
        return

    # Public
    def updateLocation(self):
        currSteps = self.pedometer.getStepCount()
        self.totalSteps += currSteps

        distance = currSteps * self.STEP_DISTANCE
        self.totalDistance += distance

        heading = self.compass.currHeading

        xDistance = distance * math.sin(heading)
        yDistance = distance * math.cos(heading)

        self.currX += xDistance
        self.currY += yDistance
        return
