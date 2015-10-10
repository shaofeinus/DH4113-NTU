from collections import deque
import math

__author__ = 'Shao Fei'


class Pedometer2:

    G_RAW_RANGE = (-32768, 32767)
    G_ACTUAL_RANGE = (-2.0, 2.0)
    Z_ACC_OFFSET = 950

    CLOCK_MAX = 4095  # In ms

    ACC_WINDOW_TIME = 1000  # In ms
    ACC_DATA_INTERVAL = 10  # In ms

    ACC_WINDOW_SIZE = ACC_WINDOW_TIME / ACC_DATA_INTERVAL
    SINGLE_DATA_WINDOW_SIZE = 5

    ACC_H_THRESHOLD = 1.25     # In G
    ACC_L_THRESHOLD = 0.85     # In G
    ACC_REST = 0.97

    HIGH_LOW_INTERVAL_MAX = 500  # In ms
    HIGH_LOW_INTERVAL_MIN = 20  # In ms

    # dataUpdateRate in Hz
    def __init__(self):

        self.accWindow = deque(maxlen=self.ACC_WINDOW_SIZE)
        self.singleDataWindow = deque(maxlen=self.SINGLE_DATA_WINDOW_SIZE)
        self.prevUpdateTime = -1
        self.prevHighTimeGlobal = 0
        self.stepsSinceLastQuery = 0
        self.yxAngle = 0.0
        self.xzAngle = 0.0
        self.zyAngle = 0.0

    # Public
    # Angle is in +/- 180 degrees, where 0 degrees is when i-axis points upwards
    def calibrate(self, yxAngle, xzAngle, zyAngle):
        self.yxAngle = yxAngle
        self.xzAngle = xzAngle
        self.zyAngle = zyAngle

    # Public
    def getStepCount(self):
        steps = 0
        while self.stepsSinceLastQuery:
            steps += 1
            self.stepsSinceLastQuery -= 1
        return steps

    # Public
    # Feeds data into Pedometer
    # accX points to left
    # accY points forward
    # accZ points downwards
    def insertData(self, accX, accY, accZ, timeInMillis):

        accX, accY, accZ = self.transformACC(accX, accY, accZ)

        # print str(math.sqrt(accX*accX + accY*accY + accZ*accZ))

        # For debug
        # f = open('pedodata.csv', 'a')
        # # f.write(str(accX) + "," + str(accY) + "," + str(accZ) + "\n")
        # f.write(str(math.sqrt(accX*accX + accY*accY + accZ*accZ)) + "\n")
        # f.close()

        # If not first ever acc data
        if self.prevUpdateTime > -1:

            # If time elapsed too long
            if timeInMillis - self.prevUpdateTime >= 2 * self.ACC_DATA_INTERVAL:
                # print "too long"
                timeElapsed = timeInMillis - self.prevUpdateTime
                self.addMultipleSingleData(accX, accY, accZ, timeElapsed)

            # If time elapsed too short
            elif 0 <= timeInMillis - self.prevUpdateTime <= 0.5 * self.ACC_DATA_INTERVAL:
                # print timeInMillis, "too short"
                return

            # If clock overflowed
            elif timeInMillis - self.prevUpdateTime < 0:

                # print "clock overflow"

                # If If time elapsed too long
                if timeInMillis + (self.CLOCK_MAX - self.prevUpdateTime) >= 2 * self.ACC_DATA_INTERVAL:
                    timeElapsed = timeInMillis + (self.CLOCK_MAX - self.prevUpdateTime)
                    self.addMultipleSingleData(accX, accY, accZ, timeElapsed)

                # If time elapsed too short
                elif timeInMillis + (self.CLOCK_MAX - self.prevUpdateTime) <= 0.5 * self.ACC_DATA_INTERVAL:
                    return

                # If time elapsed in range
                else:
                    newData = (accX, accY, accZ)
                    self.updateSingleDataWindow(newData)

            # If time elapsed in range
            else:
                # print "swee swee"
                newData = (accX, accY, accZ)
                self.updateSingleDataWindow(newData)

        # If first ever acc data
        else:
            newData = (accX, accY, accZ)
            self.updateSingleDataWindow(newData)

        self.prevUpdateTime = timeInMillis

    def transformACC(self, accX, accY, accZ):

        # To account for the offset in z axis
        if accZ - self.Z_ACC_OFFSET < self.G_RAW_RANGE[0]:
            accZ = self.G_RAW_RANGE[0]
        else:
            accZ -= self.Z_ACC_OFFSET

        # print accX, accY, accZ
        accX = (float(accX - self.G_RAW_RANGE[0]) / float(self.G_RAW_RANGE[1] - self.G_RAW_RANGE[0])) * \
               (self.G_ACTUAL_RANGE[1] - self.G_ACTUAL_RANGE[0]) + \
               (self.G_ACTUAL_RANGE[0])
        accY = (float(accY - self.G_RAW_RANGE[0]) / float(self.G_RAW_RANGE[1] - self.G_RAW_RANGE[0])) * \
               (self.G_ACTUAL_RANGE[1] - self.G_ACTUAL_RANGE[0]) + \
               (self.G_ACTUAL_RANGE[0])
        accZ = (float(accZ - self.G_RAW_RANGE[0]) / float(self.G_RAW_RANGE[1] - self.G_RAW_RANGE[0])) * \
               (self.G_ACTUAL_RANGE[1] - self.G_ACTUAL_RANGE[0]) + \
               (self.G_ACTUAL_RANGE[0])
        return accX, accY, accZ

    def addMultipleSingleData(self, accX, accY, accZ, timeElapsed):

        noOfNewDataRequired = round(timeElapsed / self.ACC_DATA_INTERVAL)

        if self.singleDataWindow:
            prevData = self.singleDataWindow[-1]
        else:
            prevData = (self.ACC_REST, self.ACC_REST, self.ACC_REST)

        newDataIncrement = ((accX - prevData[0]) / noOfNewDataRequired,
                            (accY - prevData[1]) / noOfNewDataRequired,
                            (accZ - prevData[2]) / noOfNewDataRequired)

        for i in range(0, int(noOfNewDataRequired)):
            if not self.singleDataWindow and i == 0:
                newData = (self.ACC_REST + newDataIncrement[0],
                           self.ACC_REST + newDataIncrement[1],
                           self.ACC_REST + newDataIncrement[2])
            else:
                newData = (self.singleDataWindow[-1][0] + newDataIncrement[0],
                           self.singleDataWindow[-1][1] + newDataIncrement[1],
                           self.singleDataWindow[-1][2] + newDataIncrement[2])

            self.updateSingleDataWindow(newData)

    # Updates the single data window
    # newData is tuple type
    def updateSingleDataWindow(self, newData):

        newAccG = self.calculateAccG(newData)

        if len(self.singleDataWindow) == self.SINGLE_DATA_WINDOW_SIZE:
            dequeuedAccG = 1.0 / 35 * (
                -3.0 * self.singleDataWindow[0] +
                12.0 * self.singleDataWindow[1] +
                17.0 * self.singleDataWindow[2] +
                12.0 * self.singleDataWindow[3] +
                -3.0 * self.singleDataWindow[4])
            self.singleDataWindow.popleft()
            self.singleDataWindow.append(newAccG)
            self.updateAccWindow(dequeuedAccG)
        else:
            self.singleDataWindow.append(newAccG)

    def calculateAccG(self, newData):
        # xzComp = newData[0] * math.cos(self.xzAngle / 180 * math.pi)
        # xyComp = newData[0] * math.cos((90 - self.yxAngle) / 180 * math.pi)
        # yxComp = newData[1] * math.cos(self.yxAngle / 180 * math.pi)
        # yzComp = newData[1] * math.cos((90 - self.zyAngle) / 180 * math.pi)
        # zyComp = newData[2] * math.cos(self.zyAngle / 180 * math.pi)
        # zxComp = newData[2] * math.cos((90 - self.xzAngle) / 180 * math.pi)
        #
        # # print xzComp, yxComp, zyComp
        # # print xzComp + xyComp + yxComp + yzComp + zyComp + zxComp
        # print xzComp + zxComp + yxComp + xyComp
        # return xzComp + zxComp + yxComp + xyComp
        return newData[0]

    # Updates the acc data window
    def updateAccWindow(self, accG):
        if len(self.accWindow) == self.ACC_WINDOW_SIZE:
            self.countStepsInWindow()
        else:
            self.accWindow.append(accG)

    # Assumes that accWindow is FULL
    def countStepsInWindow(self):

        accTime = 0

        # Account for global prev H time, do not reset global prev H time yet,
        # as if no local H detected in this window, need to reuse it
        prevHighTimeLocal = self.prevHighTimeGlobal

        # Clear the window
        while self.accWindow:

            # Get accG one by one
            accG = self.accWindow.popleft()

            # For data extraction
            # f = open('pedodata.csv', 'a')
            # f.write(str(accG) + "\n")
            # f.close()

            # If current accG exceeds H threshold, update prev H time
            # Prev H time is only reset when a step is recognised
            # Reset global prev H time since a local H is detected
            if accG > self.ACC_H_THRESHOLD:
                prevHighTimeLocal = accTime
                self.prevHighTimeGlobal = self.ACC_WINDOW_TIME  # Reset

            # If current accG goes below L threshold, see the prev H time
            if accG < self.ACC_L_THRESHOLD:

                # If H time is not reset, continue on
                # If H time is reset,
                if prevHighTimeLocal != self.ACC_WINDOW_TIME:
                    HLTime = accTime - prevHighTimeLocal

                    # If L time and nearest H time is in range
                    if self.HIGH_LOW_INTERVAL_MIN < HLTime < self.HIGH_LOW_INTERVAL_MAX:
                        # Add 1 step
                        self.stepsSinceLastQuery += 1

                        # Reset prev H time to max time in window, so that it is never reached
                        prevHighTimeLocal = self.ACC_WINDOW_TIME  # Reset

            accTime += self.ACC_DATA_INTERVAL

        # If global prev H time is not reset, account for the time elapsed with no new H
        if self.prevHighTimeGlobal != self.ACC_WINDOW_TIME:
            self.prevHighTimeGlobal -= self.ACC_WINDOW_TIME

        # If local prev H time is not reset, there exists a unpaired H
        # Need to account for this H time in the next window
        elif prevHighTimeLocal != self.ACC_WINDOW_TIME:
            self.prevHighTimeGlobal = prevHighTimeLocal - self.ACC_WINDOW_TIME

        # If local prev H time is not reset, all H are paired with a L, reset the global prev H time
        else:
            self.prevHighTimeGlobal = self.ACC_WINDOW_TIME

