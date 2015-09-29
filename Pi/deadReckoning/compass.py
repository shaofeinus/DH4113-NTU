from __future__ import division
from collections import deque
import math

__author__ = 'Shao Fei'


# Compass assumes that the IMU is places such that
# z-axis is pointing upward
# y-axis is pointing forward
# x-axis is pointing rightwards TODO: left or right to be calibrated
# Compass reading is in radians
class Compass:

    WINDOW_SIZE = 10

    def __init__(self):
        self.currHeading = 0
        self.xWindow = deque(maxlen=self.WINDOW_SIZE)
        self.yWindow = deque(maxlen=self.WINDOW_SIZE)

    def queueReadings(self, xReading, yReading):
        if len(self.xWindow) == self.WINDOW_SIZE:
            self.xWindow.popleft()
            self.yWindow.popleft()
        self.xWindow.append(xReading)
        self.yWindow.append(yReading)

    # Public
    def updateReading(self, xReading, yReading):

        self.queueReadings(xReading, yReading)

        magX = sum(self.xWindow)/len(self.xWindow)
        magY = sum(self.yWindow)/len(self.yWindow)

        # North is 90 deg to the left
        if magY == 0 and magX < 0:
            heading = 3.0 / 2.0 * math.pi
        # North is 90 deg to the right
        elif magY == 0 and magX > 0:
            heading = math.pi / 2.0
        else:
            theta = math.atan(magX/magY)
            # If deviation in 1st quadrant
            # theta > 0
            if magX > 0 and magY > 0:
                heading = theta
            # If deviation in 2nd quadrant
            # theta < 0
            elif magX > 0 and magY < 0:
                heading = math.pi + theta
            # If deviation in 3rd quadrant
            # theta > 0
            elif magX < 0 and magY < 0:
                heading = math.pi + theta
            # If deviation in 4th quadrant
            # theta < 0
            else:
                heading = 2 * math.pi + theta

        self.currHeading = heading
        return

    # Public
    # Reading is in radians
    def getHeadingInRad(self):
        return self.currHeading

    # Public
    # Reading is in radians
    def getHeadingInDeg(self):
        heading = self.currHeading
        if heading < math.pi:
            return heading / (2 * math.pi) * 360
        else:
            return -1 * (2 * math.pi - heading) / (2 * math.pi) * 360

