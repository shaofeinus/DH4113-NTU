import math
import pedometer2

__author__ = 'Shao Fei'


class AngleCalibrator:

    WINDOW_SIZE = 500
    MIN_DATA_NUM = 350
    ACC_TOLERANCE = 0.5     # In G
    INVALID_G = 999.0
    INVALID_ANGLE = 361.0

    def __init__(self):
        self.accXWindow = []
        self.accYWindow = []
        self.accZWindow = []
        self.failed = False
        self.yxAngle = self.INVALID_ANGLE
        self.xzAngle = self.INVALID_ANGLE
        self.zyAngle = self.INVALID_ANGLE
        self.pedometerTool = pedometer2.Pedometer2()

    # Public
    # acc values are in raw values
    # doneFlag passed from main thread
    def feedData(self, accX, accY, accZ, doneFlag):

        # Transform acc values to Gs
        accX, accY, accZ = self.pedometerTool.transformACC(accX, accY, accZ)

        # print accX, accY, accZ

        # print accX, accY, accZ

        # Continue feeding data
        if len(self.accXWindow) <= self.WINDOW_SIZE:
            self.accXWindow.append(accX)
            self.accYWindow.append(accY)
            self.accZWindow.append(accZ)
            return

        # Process fully supplied data
        else:
            calibratedX = self.processData(self.accXWindow)
            calibratedY = self.processData(self.accYWindow)
            calibratedZ = self.processData(self.accZWindow)

            if self.failed:
                doneFlag[0] = True
                # pass
            else:
                self.xzAngle = self.calculateAngle(calibratedX, calibratedZ)
                self.yxAngle = self.calculateAngle(calibratedY, calibratedX)
                self.zyAngle = self.calculateAngle(calibratedZ, calibratedY)
                # f = open('calidata.csv', 'a')
                # f.write(str(self.xzAngle) + ',' + str(self.yxAngle) + ',' + str(self.zyAngle) + '\n')
                # f.close()
                doneFlag[0] = True
                print 'Calibration success'

    # Public
    def getAngles(self):
        result = (self.yxAngle, self.xzAngle, self.zyAngle)
        return result

    # Angle calculated is w.r.t deviation from i-axis
    # Angle is in +/- 180 degrees, where 0 degrees is when i-axis points upwards
    @staticmethod
    def calculateAngle(i, j):
        if i > 0 and j > 0:
            return - math.atan(j/i) * (180 / math.pi)
        elif i > 0 and j < 0:
            return math.atan(math.fabs(j/i)) * (180 / math.pi)
        elif i < 0 and j > 0:
            return - (math.pi - math.atan(math.fabs(j/i))) * (180 / math.pi)
        else:
            return (math.pi - math.atan(j/i)) * (180 / math.pi)

    def processData(self, accWindow):

        if self.failed:
            return self.INVALID_G

        accAverage = sum(accWindow) / len(accWindow)

        processedWindow = []

        while accWindow:
            accValue = accWindow.pop()
            if math.fabs(accValue - accAverage) < self.ACC_TOLERANCE:
                processedWindow.append(accValue)

        if len(processedWindow) < self.MIN_DATA_NUM:
            self.failed = True
            print "Calibration failed, try again"

        newAccAverage = sum(processedWindow) / len(processedWindow)

        print newAccAverage
        return newAccAverage




