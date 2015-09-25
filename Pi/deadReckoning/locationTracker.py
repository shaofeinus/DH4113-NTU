import math

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
    def getHeadingInRad(self):
        return self.compass.getHeadingInRad()

    # Public
    def setLocation(self, x, y):
        self.currX = x
        self.currY = y
        return

    # Public
    def updatePedoData(self, accX, accY, accZ, timeInMillis):
        self.pedometer.updateWindow(accX, accY, accZ, timeInMillis)

    # Public
    def updateCompassData(self, xReading, yReading):
        self.compass.updateReading(xReading, yReading)

    # Public
    def updateLocation(self):
        currSteps = self.pedometer.getStepCount()
        self.totalSteps += currSteps

        distance = currSteps * self.STEP_DISTANCE
        self.totalDistance += distance

        heading = self.compass.getHeadingInRad()

        xDistance = distance * math.sin(heading)
        yDistance = distance * math.cos(heading)

        self.currX += xDistance
        self.currY += yDistance
        return
