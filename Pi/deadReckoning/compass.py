from __future__ import division
import math


__author__ = 'Shao Fei'


# Compass assumes that the IMU is places such that
# z-axis is pointing upward
# y-axis is pointing forward
# x-axis is point sidewards TODO: left or right to be calibrated
# Compass reading is in radians
class Compass:

    def __init__(self):
        self.currHeading = 0.0

    # Public
    def updateReading(self, magX, magY):
        # North is 90 deg to the left
        if magY == 0 and magX < 0:
            heading = 3.0 / 2.0 * math.pi
        # North is 90 deg to the right
        elif magY == 0 and magX > 0:
            heading = math.pi / 2.0
        else:
            theta = math.atan(magX/magY)
            # If deviation in 1st quadrant
            if magX > 0 and magY > 0:
                heading = theta
            # If deviation in 2nd quadrant
            elif magX > 0 and magY < 0:
                heading = math.pi + theta
            # If deviation in 3rd quadrant
            elif magX < 0 and magY < 0:
                heading = math.pi + theta
            # If deviation in 4th quadrant
            else:
                heading = 2 * math.pi + theta

        self.currHeading = heading
        return

    # Public
    # Reading is in radians
    def getHeading(self):
        return self.currHeading

    # Public
    # Reading is in radians
    def getHeadingInDeg(self):
        if(self.currHeading < math.pi):
            return self.currHeading / (2 * math.pi) * 360
        else:
            return -1 * (2 * math.pi - self.currHeading) / (2 * math.pi) * 360
