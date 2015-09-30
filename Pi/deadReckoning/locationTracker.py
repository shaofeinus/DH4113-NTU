import math

__author__ = 'Shao Fei'


class LocationTracker:

    HALF_STEP_DISTANCE = 25     # in cm

    def __init__(self, pedometer, compass, barometer, initX, initY):
        self.currX = initX      # Points eastwards
        self.currY = initY      # Points northwards
        self.pedometer = pedometer
        self.compass = compass
        self.barometer = barometer
        self.totalHalfSteps = 0
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
        return math.ceil(self.totalHalfSteps / 1.0)

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
    # Called when there is a need to recalibrate location
    def setLocation(self, x, y):
        self.currX = x
        self.currY = y
        return

    # Public
    def updatePedoData(self, accY, accZ, timeInMillis):
        self.pedometer.updateWindow(accY, accZ, timeInMillis)

    # Public
    def updateCompassData(self, xReading, yReading):
        self.compass.updateReading(xReading, yReading)

    # Public
    def updateBarometerData(self, reading):
        self.barometer.updateReading(reading)

    # Public
    def updateLocation(self):
        currHalfSteps = self.pedometer.getStepCount()
        self.totalHalfSteps += currHalfSteps

        # Reflects true steps, 1/2 of what is recorded (pseudo steps)
        currDistance = currHalfSteps * self.HALF_STEP_DISTANCE

        heading = self.compass.getHeadingInRad()

        # x points to the East
        xCurrDistance = currDistance * math.sin(heading)
        # y points to the North
        yCurrDistance = currDistance * math.cos(heading)

        self.currX += xCurrDistance
        self.currY += yCurrDistance
        self.totalDistance += currDistance
        return
