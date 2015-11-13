from collections import deque
import math
import compassCalibrator
import gyroCompass

__author__ = 'Shao Fei'


# Compass assumes that the IMU is places such that
# z-axis is pointing upward
# y-axis is pointing forward
# x-axis is pointing rightwards TODO: left or right to be calibrated
# Compass reading is in radians clockwise from North
class Compass:

    WINDOW_SIZE = 1
    REJECT_THRESHOLD = 13000
    CAL_DEV_PERIOD = 25     # In counts

    def __init__(self):
        self.currHeading = 0.0
        self.magXWindow = deque(maxlen=self.WINDOW_SIZE)
        self.magYWindow = deque(maxlen=self.WINDOW_SIZE)
        self.magZWindow = deque(maxlen=self.WINDOW_SIZE)
        self.accXWindow = deque(maxlen=self.WINDOW_SIZE)
        self.accYWindow = deque(maxlen=self.WINDOW_SIZE)
        self.accZWindow = deque(maxlen=self.WINDOW_SIZE)
        self.calibrator = compassCalibrator.CompassCalibrator()
        self.firstTimeCount = 0
        self.prevHeadingInRad = 0.0
        self.currDev = 0.0
        self.count = 0

    def queueMagReadings(self, xReading, yReading, zReading):

        if math.fabs(xReading) > self.REJECT_THRESHOLD \
                or math.fabs(yReading) > self.REJECT_THRESHOLD \
                or math.fabs(zReading) > self.REJECT_THRESHOLD:
            return

        self.magXWindow.append(xReading)
        self.magYWindow.append(yReading)
        self.magZWindow.append(zReading)

        self.count += 1
        if self.count == self.CAL_DEV_PERIOD:
            self.updateAngleDevInRad()
            self.count = 0

    def updateAngleDevInRad(self):
        # new heading is wrt to map north
        newHeading = self.calculateHeadingInRad()

        print "new heading is", self.getHeadingInDeg(newHeading)

        self.currDev += newHeading - self.prevHeadingInRad
        self.prevHeadingInRad = newHeading

        # Converts to [0, 2 pi]
        self.currDev = self.getHeadingInPRad(self.currDev)

    # Public
    # x points to front
    # y points to left
    # z points to up
    def updateMagReading(self, xReading, yReading, zReading):

        self.queueMagReadings(xReading, yReading, zReading)

    # Returns in [0, 2pi]
    def calculateHeadingInRad(self):

        # accX = float(sum(self.accXWindow))/len(self.accXWindow)
        # accY = float(sum(self.accYWindow))/len(self.accYWindow)
        # accZ = float(sum(self.accZWindow))/len(self.accZWindow)

        if not len(self.magXWindow) == 0:
            magX = float(sum(self.magXWindow))/float(len(self.magXWindow))
            magY = float(sum(self.magYWindow))/float(len(self.magYWindow))
            magZ = float(sum(self.magZWindow))/float(len(self.magZWindow))

            # Heading in [0, 2 * pi]
            currHeading = self.calibrator.calculateDeviceHeading(float(magX), float(magY), float(magZ))

            # movingOffset = self.calibrator.calculateMovingOffset(accX, accY, accZ)
            return currHeading
        else:
            return 0.0

    # Public
    # New function
    def getAngleDevInRad(self):
        ans = self.currDev
        self.currDev = 0
        return ans

    # Public
    # Parameter is [0, 2 pi]
    # Reading is in degrees of [-180, 180] clockwise from North
    @staticmethod
    def getHeadingInDeg(rad):
        if rad < math.pi:
            return rad / (2 * math.pi) * 360
        else:
            return -1 * (2 * math.pi - rad) / (2 * math.pi) * 360

    @staticmethod
    def getHeadingInPMRad(rad):
        if rad < math.pi:
            return rad
        else:
            return -(2 * math.pi - rad)

    @staticmethod
    def getHeadingInPRad(rad):
        rad %= 2 * math.pi
        if rad < 0:
            return 2 * math.pi + rad
        else:
            return rad
# --------------------------------------------------------------------------------------------------------------------#
    # Public
    # Get absolute heading
    # Reading is in radians of [0, 2 * pi] clockwise from North
    # Old function
    def getHeadingInRad(self):
        if self.firstTimeCount < 25:
            self.currHeading = self.calculateHeadingInRad()
            self.gyroCompass.resetRefAngle()
            self.firstTimeCount += 1

        else:
            # In [0, 2 * pi]
            newHeading = self.calculateHeadingInRad()
            gyroHeading = (self.gyroCompass.angleDeviation + self.currHeading)\
                        % (2 * math.pi)

            # print 'Mag compass:', self.getHeadingInDeg(newHeading)
            # print 'Gyro compass:', self.getHeadingInDeg(gyroHeading)

            self.gyroCompass.resetRefAngle()

            # Convert angle from [0, 2 pi] to [-pi, pi]
            newHeading = self.getHeadingInPMRad(newHeading)
            gyroHeading = self.getHeadingInPMRad(gyroHeading)

            finalHeading = (1.0 * gyroHeading + 0.0 * newHeading)

            # Convert angle from [-pi, pi] to [0, 2 pi]
            self.currHeading = self.getHeadingInPRad(finalHeading)

        self.gyroCompass.updateOffset()
        return self.currHeading
