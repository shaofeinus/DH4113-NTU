from collections import deque
import math
import compassCalibrator

__author__ = 'Shao Fei'


# Compass assumes that the IMU is places such that
# z-axis is pointing upward
# y-axis is pointing forward
# x-axis is pointing rightwards TODO: left or right to be calibrated
# Compass reading is in radians clockwise from North
class Compass:

    WINDOW_SIZE = 50

    def __init__(self):
        self.currHeading = 0
        self.magXWindow = deque(maxlen=self.WINDOW_SIZE)
        self.magYWindow = deque(maxlen=self.WINDOW_SIZE)
        self.magZWindow = deque(maxlen=self.WINDOW_SIZE)
        self.accXWindow = deque(maxlen=self.WINDOW_SIZE)
        self.accYWindow = deque(maxlen=self.WINDOW_SIZE)
        self.accZWindow = deque(maxlen=self.WINDOW_SIZE)
        self.calibrator = compassCalibrator.CompassCalibrator()

    def queueMagReadings(self, xReading, yReading, zReading):
        if len(self.magXWindow) == self.WINDOW_SIZE:
            self.magXWindow.popleft()
            self.magYWindow.popleft()
            self.magZWindow.popleft()
        self.magXWindow.append(xReading)
        self.magYWindow.append(yReading)
        self.magZWindow.append(zReading)

    def queueAccReadings(self, xReading, yReading, zReading):
        if len(self.accXWindow) == self.WINDOW_SIZE:
            self.accXWindow.popleft()
            self.accYWindow.popleft()
            self.accZWindow.popleft()
        self.accXWindow.append(xReading)
        self.accYWindow.append(yReading)
        self.accZWindow.append(zReading)

    # Public
    # x points to front
    # y points to left
    # z points to up
    def updateAccReading(self, xReading, yReading, zReading):

        self.queueAccReadings(xReading, yReading, zReading)

        # accX = float(sum(self.accXWindow))/len(self.accXWindow)
        # accY = float(sum(self.accYWindow))/len(self.accYWindow)
        # accZ = float(sum(self.accZWindow))/len(self.accZWindow)

    # Public
    # x points to front
    # y points to left
    # z points to up
    def updateMagReading(self, xReading, yReading, zReading):

        self.queueMagReadings(xReading, yReading, zReading)

        # magX = float(sum(self.magXWindow))/len(self.magXWindow)
        # magY = float(sum(self.magYWindow))/len(self.magYWindow)
        # magZ = float(sum(self.magZWindow))/len(self.magZWindow)

        # # North is 90 deg to the left
        # if magY == 0 and magX < 0:
        #     heading = 3.0 / 2.0 * math.pi
        # # North is 90 deg to the right
        # elif magY == 0 and magX > 0:
        #     heading = math.pi / 2.0
        # else:
        #     theta = math.atan(magX/magY)
        #     # If deviation in 1st quadrant
        #     # theta > 0
        #     if magX > 0 and magY > 0:
        #         heading = theta
        #     # If deviation in 2nd quadrant
        #     # theta < 0
        #     elif magX > 0 and magY < 0:
        #         heading = math.pi + theta
        #     # If deviation in 3rd quadrant
        #     # theta > 0
        #     elif magX < 0 and magY < 0:
        #         heading = math.pi + theta
        #     # If deviation in 4th quadrant
        #     # theta < 0
        #     else:
        #         heading = 2 * math.pi + theta

        # Heading in [0, 2 * pi]
        # heading = self.calibrator.calculateDeviceHeading(magX, magY, magZ)
        #
        # if self.calibrator.NOffsetAngle > heading:
        #     self.currHeading = 2 * math.pi - (self.calibrator.NOffsetAngle - heading)
        # else:
        #     self.currHeading = heading - self.calibrator.NOffsetAngle

    def calculateHeadingInRad(self):

        accX = float(sum(self.accXWindow))/len(self.accXWindow)
        accY = float(sum(self.accYWindow))/len(self.accYWindow)
        accZ = float(sum(self.accZWindow))/len(self.accZWindow)

        magX = float(sum(self.magXWindow))/len(self.magXWindow)
        magY = float(sum(self.magYWindow))/len(self.magYWindow)
        magZ = float(sum(self.magZWindow))/len(self.magZWindow)

        # Heading in [0, 2 * pi]
        devHeading = self.calibrator.calculateDeviceHeading(float(magX), float(magY), float(magZ))

        movingOffset = self.calibrator.calculateMovingOffset(accX, accY, accZ)

        if self.calibrator.NOffsetAngle + movingOffset > devHeading:
            currHeading = 2 * math.pi - (self.calibrator.NOffsetAngle + movingOffset - devHeading)
        else:
            currHeading = devHeading - (self.calibrator.NOffsetAngle + movingOffset)

        return currHeading

    # Public
    # Reading is in radians of [0, 2 * pi] clockwise from North
    def getHeadingInRad(self):
        self.currHeading = self.calculateHeadingInRad()
        return self.currHeading

    # Public
    # Reading is in degrees of [-180, 180] clockwise from North
    def getHeadingInDeg(self):
        self.currHeading = self.calculateHeadingInRad()
        if self.currHeading < math.pi:
            return self.currHeading / (2 * math.pi) * 360
        else:
            return -1 * (2 * math.pi - self.currHeading) / (2 * math.pi) * 360
