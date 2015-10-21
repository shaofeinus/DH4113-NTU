import math

__author__ = 'Shao Fei'


# x points to front
# y points to left
# z points to up
class CompassCalibrator:
    WINDOW_SIZE = 700
    MIN_DATA_NUM = 500
    ACC_TOLERANCE = 0.5         # In G
    MAG_TOLERANCE = 0.5         # In fraction of max
    GYRO_TOLERANCE = 1000.0     # In raw

    DECLINATION_OFFSET = 4.072 / 1000

    def __init__(self):
        self.accXWindow = []
        self.accYWindow = []
        self.accZWindow = []
        self.accCaliFailed = False
        self.magXWindow = []
        self.magYWindow = []
        self.magZWindow = []
        self.magCaliFailed = False
        self.gyXWindow = []
        self.gyYWindow = []
        self.gyZWindow = []
        self.gyCaliFailed = False

        self.NOffsetAngle = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        # self.magXRange = (-2300, 2300)
        # self.magYRange = (-2300, 2300)
        # self.magZRange = (-2300, 2300)

        self.initGYOffset = 0.0
        self.initGXOffset = 0.0
        self.initGZOffset = 0.0

    # Public
    # def inputManualRange(self, xRange, yRange, zRange):
    #     self.magXRange = xRange
    #     self.magYRange = yRange
    #     self.magZRange = zRange

    # Public
    # acc values are in raw values
    # doneFlag passed from main thread
    def calibrateTilt(self, accX, accY, accZ, doneFlag):

        # print 'raw acc', accX, accY, accZ

        # Continue feeding data
        if len(self.accXWindow) < self.WINDOW_SIZE:
            self.accXWindow.append(accX)
            self.accYWindow.append(accY)
            self.accZWindow.append(accZ)
            return

        # Process fully supplied data
        else:
            accX = self.processAccData(self.accXWindow)
            accY = self.processAccData(self.accYWindow)
            accZ = self.processAccData(self.accZWindow)

            if not self.accCaliFailed:

                aR = math.sqrt(accX * accX + accY * accY + accZ * accZ)

                print aR

                # accXNorm points forward
                accXNorm = accX / aR

                # accYNorm points rightward
                accYNorm = accY / aR

                self.pitch = math.asin(accXNorm)
                self.roll = math.asin(accYNorm / math.cos(self.pitch))

                # f = open('calidata.csv', 'a')
                # f.write(str(self.xzAngle) + ',' + str(self.yxAngle) + ',' + str(self.zyAngle) + '\n')
                # f.close()
                print 'Tilt calibration success'
                print 'Pitch:', self.pitch, 'Roll:', self.roll

            doneFlag['tilt'] = True

    # Public
    # doneFlag passed from main thread
    def calibrateNOffset(self, magX, magY, magZ, doneFlag):

        # Continue feeding data
        if len(self.magXWindow) < self.WINDOW_SIZE:
            self.magXWindow.append(magX)
            self.magYWindow.append(magY)
            self.magZWindow.append(magZ)
            return

        # Process fully supplied data
        else:
            magX = self.processMagData(self.magXWindow)
            magY = self.processMagData(self.magYWindow)
            magZ = self.processMagData(self.magZWindow)

            print 'raw mag:', magX, magY, magZ

            if not self.magCaliFailed:
                self.NOffsetAngle = self.calculateDeviceHeading(float(magX), float(magY), float(magZ))
                # f = open('calidata.csv', 'a')
                # f.write(str(self.xzAngle) + ',' + str(self.yxAngle) + ',' + str(self.zyAngle) + '\n')
                # f.close()
                print 'North offset calibration success'

            doneFlag['nOffset'] = True

    # Public
    # doneFlag passed from main thread
    def calibrateGyro(self, gX, gY, gZ, doneFlag):

        # Continue feeding data
        if len(self.gyXWindow) < self.WINDOW_SIZE:
            self.gyXWindow.append(gX)
            self.gyYWindow.append(gY)
            self.gyZWindow.append(gZ)
            return

        # Process fully supplied data
        else:
            gX = self.processGyroData(self.gyXWindow)
            gY = self.processGyroData(self.gyYWindow)
            gZ = self.processGyroData(self.gyZWindow)

            print 'raw gyro:', gX, gY, gZ

            if not self.gyCaliFailed:
                self.initGXOffset = gX
                self.initGYOffset = gY
                self.initGZOffset = gZ
                # f = open('gyrodata.csv', 'a')
                # f.write(str(self.xzAngle) + ',' + str(self.yxAngle) + ',' + str(self.zyAngle) + '\n')
                # f.close()
                print 'Gyro calibration success'

            doneFlag['gyro'] = True

    # Public
    def getNOffsetAngle(self):
        return self.NOffsetAngle

    # Public
    # Returns Heading in [0, 2 * pi]
    # x points front
    # y points left
    # z points up
    def calculateMovingOffset(self, accX, accY, accZ):

        # magX points forward
        # magXComp = magX * math.cos(self.pitch) - magZ * math.sin(self.pitch)
        accXComp = accX*math.cos(self.pitch) - (accZ*math.cos(self.roll) + accY*math.sin(self.roll))*math.sin(self.pitch)

        # magY points left
        # magYComp = magX * math.sin(self.roll) * math.sin(self.pitch) + \
        #     magY * math.cos(self.roll) - \
        #     magZ * math.sin(self.roll) * math.cos(self.pitch)
        accYComp = accY*math.cos(self.roll) - (accZ*math.cos(self.pitch) + accX*math.sin(self.pitch))*math.sin(self.roll)

        heading = math.atan2(accYComp, accXComp)

        if heading < 0:
            heading += 2 * math.pi

        heading = 0

        return heading

    # Public
    # Returns Heading in [0, 2 * pi]
    # x points front
    # y points left
    # z points up
    def calculateDeviceHeading(self, magX, magY, magZ):

        # magX points forward
        # if self.pitch > 0:
        #     magXComp = magX * math.cos(self.pitch) - magZ * math.sin(self.pitch)
        # else:
        #     magXComp = magX * math.cos(self.pitch) + magZ * math.sin(self.pitch)

        # magXComp = magX*math.cos(self.pitch) - (magZ*math.cos(self.roll) + magY*math.sin(self.roll))*math.sin(self.pitch)

        if self.pitch > 0:
            magXComp = magX*math.cos(self.pitch) - magZ*math.sin(self.pitch)
        else:
            magXComp = magX*math.cos(self.pitch) - magZ*math.sin(self.pitch)

        # magY points left
        # if self.roll > 0:
        #     magYComp = magX * math.sin(self.roll) * math.sin(self.pitch) + \
        #         magY * math.cos(self.roll) - \
        #         magZ * math.sin(self.roll) * math.cos(self.pitch)
        # if self.roll < 0:
        #     magYComp = magX * math.sin(self.roll) * math.sin(self.pitch) + \
        #         magY * math.cos(self.roll) - \
        #         magZ * math.sin(self.roll) * math.cos(self.pitch)

        # magYComp = magY*math.cos(self.roll) - (- magZ*math.cos(self.pitch) + magX*math.sin(self.pitch))*math.sin(self.roll)

        if self.roll > 0:
            magYComp = magY*math.cos(self.roll) - magZ*math.sin(self.roll)
        else:
            magYComp = magY*math.cos(self.roll) - magZ*math.sin(self.roll)

        # print 'x comp', magXComp, 'y comp', magYComp

        # print 'after tilt correction:', magX, magY, magZ

        # magYComp = float(magY)
        # magXComp = float(magX)

        heading = math.atan2(magYComp, magXComp)

        heading += self.DECLINATION_OFFSET

        if heading > 2 * math.pi:
            heading -= 2 * math.pi

        if heading < 0:
            heading += 2 * math.pi

        return heading

    def processAccData(self, accWindow):

        if self.accCaliFailed:
            return self.INVALID_G

        accAverage = sum(accWindow) / len(accWindow)

        processedWindow = []

        while accWindow:
            accValue = accWindow.pop()
            if math.fabs(accValue - accAverage) < self.ACC_TOLERANCE:
                processedWindow.append(accValue)

        if len(processedWindow) < self.MIN_DATA_NUM:
            self.accCaliFailed = True
            print "Tilt calibration failed, try again"

        newAccAverage = sum(processedWindow) / len(processedWindow)

        return newAccAverage

    def processMagData(self, magWindow):

        if self.magCaliFailed:
            return 0

        magAverage = sum(magWindow) / len(magWindow)

        processedWindow = []

        while magWindow:
            magValue = magWindow.pop()
            if math.fabs(magValue - magAverage) < self.MAG_TOLERANCE:
                processedWindow.append(magValue)

        if len(processedWindow) < self.MIN_DATA_NUM:
            self.magCaliFailed = True
            print "Compass calibration failed, try again"

        newMagAverage = sum(processedWindow) / len(processedWindow)

        return newMagAverage

    def processGyroData(self, gyWindow):

        if self.gyCaliFailed:
            return 0

        gyAverage = sum(gyWindow) / len(gyWindow)

        processedWindow = []

        while gyWindow:
            gyValue = gyWindow.pop()
            if math.fabs(gyValue - gyAverage) < self.GYRO_TOLERANCE:
                processedWindow.append(gyValue)

        if len(processedWindow) < self.MIN_DATA_NUM:
            self.gyCaliFailed = True
            print "Gyro calibration failed, try again"

        newGAverage = sum(processedWindow) / len(processedWindow)

        return newGAverage
