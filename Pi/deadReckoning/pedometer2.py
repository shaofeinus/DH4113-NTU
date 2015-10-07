from collections import deque
import math

__author__ = 'Shao Fei'


class Pedometer2:
    CLOCK_MAX = 4095  # In ms

    ACC_WINDOW_TIME = 1000  # In ms
    ACC_DATA_INTERVAL = 10  # In ms

    ACC_WINDOW_SIZE = ACC_WINDOW_TIME / ACC_DATA_INTERVAL
    SINGLE_DATA_WINDOW_SIZE = 5

    ACC_H_THRESHOLD = 20000
    ACC_L_THRESHOLD = 12500
    HIGH_LOW_INTERVAL_MAX = 500  # In ms
    HIGH_LOW_INTERVAL_MIN = 20  # In ms

    # dataUpdateRate in Hz
    def __init__(self):

        self.accWindow = deque(maxlen=self.ACC_WINDOW_SIZE)
        self.singleDataWindow = deque(maxlen=self.SINGLE_DATA_WINDOW_SIZE)

        self.prevUpdateTime = -1

        self.prevHighTimeGlobal = 0

        self.stepsSinceLastQuery = 0

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
                if timeInMillis + (self.CLOCK_MAX - self.prevUpdateTime) >= 2 * self.ACC_DATA_INTERVAL:
                    timeElapsed = timeInMillis + (self.CLOCK_MAX - self.prevUpdateTime)
                    self.addMultipleSingleData(accX, accY, accZ, timeElapsed)
                elif timeInMillis + (self.CLOCK_MAX - self.prevUpdateTime) <= 0.5 * self.ACC_DATA_INTERVAL:
                    return
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

    def addMultipleSingleData(self, accX, accY, accZ, timeElapsed):
        noOfNewDataRequired = round(timeElapsed / self.ACC_DATA_INTERVAL)
        prevData = self.singleDataWindow[-1]
        newDataIncrement = ((accX - prevData[0]) / noOfNewDataRequired,
                            (accY - prevData[1]) / noOfNewDataRequired,
                            (accZ - prevData[2]) / noOfNewDataRequired)
        for i in range(0, noOfNewDataRequired):
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

