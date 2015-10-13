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

    WINDOW_SIZE = 100

    def __init__(self):
        self.currHeading = 0
        self.xWindow = deque(maxlen=self.WINDOW_SIZE)
        self.yWindow = deque(maxlen=self.WINDOW_SIZE)
        self.zWindow = deque(maxlen=self.WINDOW_SIZE)
        self.calibrator = compassCalibrator.CompassCalibrator()

    def queueReadings(self, xReading, yReading, zReading):
        if len(self.xWindow) == self.WINDOW_SIZE:
            self.xWindow.popleft()
            self.yWindow.popleft()
            self.zWindow.popleft()
        self.xWindow.append(xReading)
        self.yWindow.append(yReading)
        self.zWindow.append(zReading)

    # Public
    # x points to front
    # y points to left
    # z points to up
    def updateReading(self, xReading, yReading, zReading):

        self.queueReadings(xReading, yReading, zReading)

        magX = float(sum(self.xWindow)/len(self.xWindow))
        magY = float(sum(self.yWindow)/len(self.yWindow))
        magZ = float(sum(self.zWindow)/len(self.zWindow))

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
        heading = self.calibrator.calculateDeviceHeading(magX, magY, magZ)

        if self.calibrator.NOffsetAngle > heading:
            self.currHeading = 2 * math.pi - (self.calibrator.NOffsetAngle - heading)
        else:
            self.currHeading = heading - self.calibrator.NOffsetAngle

    # Public
    # Reading is in radians of [0, 2 * pi] clockwise from North
    def getHeadingInRad(self):
        return self.currHeading

    # Public
    # Reading is in degrees of [-180, 180] clockwise from North
    def getHeadingInDeg(self):
        heading = self.currHeading
        if heading < math.pi:
            return heading / (2 * math.pi) * 360
        else:
            return -1 * (2 * math.pi - heading) / (2 * math.pi) * 360

