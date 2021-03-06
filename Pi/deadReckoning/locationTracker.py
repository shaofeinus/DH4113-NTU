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
    MOVE_ANGLE_TOLERANCE = 5.0 / 180.0 * math.pi

    def __init__(self, initX, initY, northAt):
        self.currX = initX      # Points eastwards
        self.currY = initY      # Points northwards

        self.pedometer = pedometer2.Pedometer2()
        self.compass = compass.Compass()
        self.gyroCompass = gyroCompass.GyroCompass()
        self.barometer = barometer.Barometer()
        self.calibrationTools = calibrationTools.CalibrationTools()

        self.totalSteps = 0
        self.totalDistance = 0
        self.northAt = northAt / 180 * math.pi      # In rad
        self.firstUpdate = True

        self.trueHeadingWRTNorthInDeg = 0
        self.headingWRTNorthInDeg = 0
        self.trueHeadingWRTNorthInRad = 0
        self.headingWRTNorthInRad = 0

        self.isFirstStep = True
        self.isLastStep = False
        self.prevGyroDev = 0
        self.prevCompDev = 0
        self.prevMode = ''

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

    def getTrueHeadingInDeg(self):
        return self.trueHeadingWRTNorthInDeg

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
    def updateLocation(self, stop, recalibrating):

        currSteps = self.pedometer.getStepCount()
        self.totalSteps += currSteps

        # Reflects true steps, 1/2 of what is recorded (pseudo steps)
        currDistance = currSteps * self.STEP_DISTANCE

        compAngleDev = self.compass.getAngleDevInRad()
        gyroAngleDev = self.gyroCompass.getAngleDevInRad()

        if not stop and not recalibrating:
            if currSteps != 0:
                angleDev = gyroAngleDev
                mode = 'gyro'
                self.isLastStep = True
            else:
                self.isFirstStep = True
                angleDev = compAngleDev
                mode = 'compass'

            if currSteps != 0 and self.isFirstStep:
                self.isFirstStep = False
                if not self.prevMode == 'change next dev':
                    self.updateCurrHeading(self.headingWRTNorthInRad - self.prevCompDev + self.prevGyroDev)
                mode = 'change prev dev'

            self.prevGyroDev = gyroAngleDev
            self.prevCompDev = compAngleDev

            if currSteps == 0 and self.isLastStep:
                self.isLastStep = False
                angleDev = gyroAngleDev
                mode = 'change next dev'

                # angleDev = gyroAngleDev
                # mode = 'gyro'

            self.prevMode = mode

            self.updateCurrHeading(angleDev + self.trueHeadingWRTNorthInRad)

            # Heading wrt to North
            # self.headingWRTNorthInRad = self.compass.getHeadingInRad()
            # self.headingWRTNorthInDeg = self.compass.Compass.getHeadingInDeg(self.headingWRTNorthInRad)

            # print "heading ", compass.Compass.getHeadingInDeg(self.compass.calculateHeadingInRad())

            if currSteps != 0:
                # headingToUse = round(self.headingWRTNorthInRad / self.MOVE_ANGLE_TOLERANCE) * self.MOVE_ANGLE_TOLERANCE
                headingToUse = self.headingWRTNorthInRad
                # x points to the East
                xCurrDistance = currDistance * math.sin(headingToUse)
                # y points to the North
                yCurrDistance = currDistance * math.cos(headingToUse)

                self.currX += xCurrDistance
                self.currY += yCurrDistance
                self.totalDistance += currDistance
        elif stop:
            mode = 'stop'
            gyroAngleDev = 0
            compAngleDev = 0

        elif recalibrating:
            mode = 'recalibrating'
            gyroAngleDev = 0
            compAngleDev = 0

        f = open('locationdata.csv', 'a')
        if self.firstUpdate:
            f.write('distance covered,true angle, est angle,gyro dev, comp dev, mode,steps,currX,currY\n')
            self.firstUpdate = False

        f.write(str(currDistance) + ',' +
                str(self.trueHeadingWRTNorthInDeg) + ',' +
                str(self.headingWRTNorthInDeg) + ',' +
                str(self.compass.getHeadingInDeg(gyroAngleDev)) + ',' +
                str(self.compass.getHeadingInDeg(compAngleDev)) + ',' +
                str(mode) + ',' +
                str(self.totalSteps) + ',' +
                str(self.currX) + ',' +
                str(self.currY) + '\n')
        f.close()

    def updateCurrHeading(self, angleInRad):
        angleInRad %= 2 * math.pi

        if angleInRad < 0:
            angleInRad += 2 * math.pi

        self.trueHeadingWRTNorthInRad = angleInRad
        self.trueHeadingWRTNorthInDeg = compass.Compass.getHeadingInDeg(self.trueHeadingWRTNorthInRad)

        self.updateEstHeading()

    def updateEstHeading(self):
        self.headingWRTNorthInRad = round(self.trueHeadingWRTNorthInRad / self.MOVE_ANGLE_TOLERANCE) * self.MOVE_ANGLE_TOLERANCE
        self.headingWRTNorthInDeg = compass.Compass.getHeadingInDeg(self.headingWRTNorthInRad)

    # Called by Navigation
    # Offset parameter in Deg
    def updateMapNorth(self, degOffset):
        if degOffset < 0:
            radOffset = 2 * math.pi + degOffset / 180.0 * math.pi
        else:
            radOffset = degOffset / 180.0 * math.pi

        self.updateCurrHeading(self.headingWRTNorthInRad - radOffset)

    # Called by Navigation
    # Coordinate parameters in com
    def setLocation(self, xCoordinate, yCoordinate):
        self.currX = xCoordinate
        self.currY = yCoordinate

    def resetHeading(self):
        self.trueHeadingWRTNorthInDeg = 0
        self.headingWRTNorthInDeg = 0
        self.trueHeadingWRTNorthInRad = 0
        self.headingWRTNorthInRad = 0
