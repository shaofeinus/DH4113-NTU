from __future__ import division
from collections import deque
import math

__author__ = 'Shao Fei'


# Compass assumes that the IMU is places such that
# z-axis is pointing upward
# y-axis is pointing forward
# x-axis is point sidewards TODO: left or right to be calibrated
# Barometer reading is in cm
class Barometer:

    WINDOW_SIZE = 10
    HEIGHT_PER_FLOOR = 300          # in cm

    def __init__(self):
        self.height = 0
        self.window = deque(maxlen=self.WINDOW_SIZE)

    def queueReadings(self, reading):

        height = self.transformReading(reading)

        if len(self.window) == self.WINDOW_SIZE:
            self.window.popleft()
        self.window.append(height)

    def transformReading(self, rawReading):

        pressure = rawReading / 4096
        height = (1 - math.pow(pressure / 1013.25, 0.190263)) * 4433080
        return height

    # Public
    def updateReading(self, reading):

        self.queueReadings(reading)

        self.height = sum(self.window)/len(self.window)

        return

    # Public
    # Reading is in cm
    def getHeight(self):
        return self.height

    # Public
    def getFloor(self):
        return math.ceil(self.height / self.HEIGHT_PER_FLOOR)
