import math

__author__ = 'Shao Fei'


class LocationTracker:

    STEP_DISTANCE = 0.5     # in m

    def __init__(self, pedometer, compass, barometer, initX, initY):
        # Dummies
        self.currX = initX
        self.currY = initY
        self.pedometer = pedometer
        self.compass = compass
        self.barometer = barometer
        self.totalSteps = 0
        self.totalDistance = 0

    # Public
    def getLocation(self):
        return {'x': self.currX, 'y': self.currY}

    # Public
    def getXCoord(self):
        return self.currX
    
    # Public
    def getYCoord(self):
        return self.currY

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
    def getHeadingInDeg(self):
        return self.compass.getHeadingInDeg()

    # Public
    def getHeightInCM(self):
        return self.barometer.getHeight()

    # Public
    def getFloor(self):
        return self.barometer.getFloor()

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
    def updateBarometerData(self, reading):
        self.barometer.updateReading(reading)

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
