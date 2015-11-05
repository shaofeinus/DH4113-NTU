import math
import barometer
import compass
import gyroCompass
import pedometer
import pedometer2
import calibrationTools

__author__ = 'Shao Fei'


class LocationTracker:

    STEP_DISTANCE = 45.0     # in cm

    def __init__(self, initX, initY, northAt):
        self.currX = initX      # Points eastwards
        self.currY = initY      # Points northwards
        self.pedometer = pedometer2.Pedometer2()
        self.compass = compass.Compass()
        self.gyroCompass = gyroCompass.GyroCompass()
        self.barometer = barometer.Barometer()
        self.totalSteps = 0
        self.totalDistance = 0
        self.northAt = northAt / 180 * math.pi      # In rad
        self.firstUpdate = True
        self.headingWRTMapInRad = 0
        self.headingWRTMapInDeg = 0
        self.headingWRTNorthInRad = 0
        self.headingWRTNorthInDeg = 0
        self.calibrationTools = calibrationTools.CalibrationTools()

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
        return self.headingWRTNorthInRad

    # Public
    def getHeadingInDeg(self):
        return self.headingWRTNorthInDeg

    # Public
    def getHeadingWRTMapInDeg(self):
        return self.headingWRTMapInDeg

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
    def updatePedoData(self, accX, accY, accZ, timeInMillis):
        self.pedometer.insertData(accX, accY, accZ, timeInMillis)

    # Public
    def updateCompassMagData(self, magX, magY, magZ):
        self.compass.updateMagReading(magX, magY, magZ)

    # Public
    def updateCompassAccData(self, accX, accY, accZ):
        self.compass.updateAccReading(accX, accY, accZ)

    # Public
    def updateBarometerData(self, reading):
        self.barometer.updateReading(reading)

    # Public
    def updateLocation(self):

        currSteps = self.pedometer.getStepCount()
        self.totalSteps += currSteps

        # Reflects true steps, 1/2 of what is recorded (pseudo steps)
        currDistance = currSteps * self.STEP_DISTANCE

        compAngleDev = self.compass.getAngleDevInRad()
        gyroAngleDev = self.gyroCompass.getAngleDevInRad()

        if currSteps != 0:
            angleDev = gyroAngleDev
        else:
            angleDev = compAngleDev

        self.updateCurrHeading(angleDev + self.headingWRTNorthInRad)

        # Heading wrt to North
        # self.headingWRTNorthInRad = self.compass.getHeadingInRad()
        # self.headingWRTNorthInDeg = self.compass.Compass.getHeadingInDeg(self.headingWRTNorthInRad)

        # x points to the East
        xCurrDistance = currDistance * math.sin(self.headingWRTNorthInRad)
        # y points to the North
        yCurrDistance = currDistance * math.cos(self.headingWRTNorthInRad)

        self.currX += xCurrDistance
        self.currY += yCurrDistance
        self.totalDistance += currDistance

        f = open('locationdata.csv', 'a')
        if self.firstUpdate:
            f.write('distance covered,degrees from top of map,rad,currX,currY\n')
            self.firstUpdate = False

        f.write(str(currDistance) + ',' +
                str(self.headingWRTNorthInDeg) + ',' +
                str(self.totalSteps) + ',' +
                str(self.currX) + ',' +
                str(self.currY) + '\n')
        f.close()

    def updateCurrHeading(self, angleInRad):
        angleInRad %= 2 * math.pi

        if angleInRad < 0:
            angleInRad += 2 * math.pi

        self.headingWRTNorthInRad = angleInRad
        self.headingWRTNorthInDeg = compass.Compass.getHeadingInDeg(self.headingWRTNorthInRad)
