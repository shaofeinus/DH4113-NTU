from collections import deque
import math

__author__ = 'Shao Fei'


class GyroCompass:

    WINDOW_SIZE = 10
    TIME_INTERVAL = 20.0 / 1000     # In sec
    RATE_OF_DRIFT = -9.0E-10    #0.0
    INITIAL_DRIFT = -6.0E-7     #-1.0E-5

    def __init__(self):
        self.angleDeviation = 0.0      # [0, 2 pi]
        self.pitch = 0.0
        self.roll = 0.0
        self.XMAWindow = deque(maxlen=self.WINDOW_SIZE)
        self.YMAWindow = deque(maxlen=self.WINDOW_SIZE)
        self.ZMAWindow = deque(maxlen=self.WINDOW_SIZE)
        self.currDriftOffset = self.INITIAL_DRIFT

    def calibrate(self, pitch, roll):
        self.pitch = pitch
        self.roll = roll

    def queueGyroReadings(self, xReading, yReading, zReading):

        # Only appending is needed as deque object automatically releases oldest element if maxlen is reached
        self.XMAWindow.append(xReading)
        self.YMAWindow.append(yReading)
        self.ZMAWindow.append(zReading)

        if len(self.XMAWindow) == self.WINDOW_SIZE:
            xReading = sum(self.XMAWindow) / len(self.XMAWindow)
            yReading = sum(self.YMAWindow) / len(self.YMAWindow)
            zReading = sum(self.ZMAWindow) / len(self.ZMAWindow)
            self.updateHeading(xReading, yReading, zReading)
        # self.updateHeading(xReading, yReading, zReading)

    # Updates angle dev in range [0, 2 pi]
    def updateHeading(self, xReading, yReading, zReading):

        resolvedAV = self.resolveGyro(xReading, yReading, zReading)

        self.angleDeviation -= resolvedAV * self.TIME_INTERVAL
        self.angleDeviation -= self.currDriftOffset

        # Converts angle deviation to [0, 2 * pi]
        if self.angleDeviation > 2 * math.pi:
            self.angleDeviation -= 2 * math.pi
        if self.angleDeviation < 0:
            self.angleDeviation += 2 * math.pi

        # print self.getAngleDevInDeg()

    def resolveGyro(self, xReading, yReading, zReading):
        ans = zReading * math.cos(self.pitch) * math.cos(self.roll) + \
               xReading * math.sin(self.pitch) + \
               yReading * math.sin(self.roll)

        # rollComp = zReading * math.cos(self.pitch) * math.cos(self.roll) + \
        #            yReading * math.sin(self.roll)

        # f = open('resolvedGyro.csv', 'a')
        # f.write(str(xReading) + ',' + str(yReading) + ',' + str(zReading) + '\n')
        # f.close()
        # ans = zReading
        return ans

    def getAngleDevInDeg(self):
        if self.angleDeviation < math.pi:
            ans = self.angleDeviation / math.pi * 180.0
        else:
            ans = self.angleDeviation / math.pi * 180.0
            ans -= 360.0
        return ans

    def getAngleDevInRad(self):
        ans = self.angleDeviation
        self.angleDeviation = 0.0
        return ans

    def updateOffset(self):
        self.currDriftOffset += self.RATE_OF_DRIFT
