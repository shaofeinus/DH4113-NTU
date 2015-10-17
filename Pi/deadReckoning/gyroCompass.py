from collections import deque
import math

__author__ = 'Shao Fei'


class GyroCompass:

    WINDOW_SIZE = 10
    TIME_INTERVAL = 10.0 / 1000     # In sec

    def __init__(self):
        self.angleFromMapN = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.XMAWindow = deque(maxlen=self.WINDOW_SIZE)
        self.YMAWindow = deque(maxlen=self.WINDOW_SIZE)
        self.ZMAWindow = deque(maxlen=self.WINDOW_SIZE)

    def calibrate(self, pitch, roll):
        self.pitch = pitch
        self.roll = roll

    def queueGyroReadings(self, xReading, yReading, zReading):

        # Only appending is needed as deque object automatically releases oldest element if maxlen is reached
        self.XMAWindow.append(xReading)
        self.YMAWindow.append(yReading)
        self.ZMAWindow.append(zReading)

        x = sum(self.XMAWindow) / len(self.XMAWindow)
        y = sum(self.YMAWindow) / len(self.YMAWindow)
        z = sum(self.ZMAWindow) / len(self.ZMAWindow)

        self.updateHeading(x, y, z)

    def updateHeading(self, xReading, yReading, zReading):

        resolvedAV = self.resolveGyro(xReading, yReading, zReading)

        self.angleFromMapN -= resolvedAV * self.TIME_INTERVAL

        if self.angleFromMapN > 2 * math.pi:
            self.angleFromMapN -= 2 * math.pi
        if self.angleFromMapN < 0:
            self.angleFromMapN += 2 * math.pi

    def resolveGyro(self, xReading, yReading, zReading):
        return zReading * math.cos(self.pitch) * math.cos(self.roll) + \
               xReading * math.sin(self.pitch) + \
               yReading * math.sin(self.roll)
