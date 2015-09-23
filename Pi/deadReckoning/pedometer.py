import math

__author__ = 'Shao Fei'


class Pedometer:
    # TODO: to be calibrated
    WINDOW_SIZE = 500                                       # window time = WINDOW_SIZE * WINDOW_INTERVAL_TIME
    WINDOW_INTERVAL_TIME = 10                               # in ms
    ACC_REST = 1.0                                          # in Gs
    ACC_THRESHOLD = 2.5                                     # in Gs
    STEP_INTERVAL_TIME_LB = 100 / WINDOW_INTERVAL_TIME      # in ms
    STEP_INTERVAL_TIME_UB = 1000 / WINDOW_INTERVAL_TIME     # in ms

    def __init__(self):
        self.accWindow = []
        self.prevTime = -1
        self.stepCount = 0
        self.isPrevWindowEvenSteps = False
        self.prevLastStepToEndTime = -1

    # Public #
    # To be called when reading corresponds to user at rest
    def calibrate(self, accX_rest, accY_rest, accZ_rest):
        self.ACC_REST = math.sqrt(accX_rest * accX_rest + accY_rest * accY_rest + accZ_rest * accZ_rest)
        return

    # Public #
    # Updates the acc values window
    # To be called at < 100Hz
    def updateWindow(self, accX, accY, accZ, timeInMillis):

        # Update steps if window is full
        if len(self.accWindow) == self.WINDOW_SIZE:
            self.updateSteps()

        # Get resultant acceleration
        accR = math.sqrt(accX * accX + accY * accY + accZ * accZ)

        # Check if time elapsed from last update exceed limit
        if self.prevTime == -1:
            timeElapsed = timeInMillis
        else:
            timeElapsed = timeInMillis - self.prevTime

        if timeElapsed <= self.WINDOW_INTERVAL_TIME:
            self.accWindow.append(accR)

        # If time elapsed exceed limit
        else:
            # Get number of intervals to cover up extra time
            numIntervals = math.ceil(timeElapsed / self.WINDOW_INTERVAL_TIME)
            # Get the change in acc of each interval
            accIntervalChange = (accR - self.accWindow[len(self.accWindow) - 1]) / numIntervals

            while numIntervals > 0:
                # If window has reached its limit size
                if len(self.accWindow) == self.WINDOW_SIZE:
                    # Take note of last reading before clearing window
                    lastReading = self.accWindow[self.WINDOW_SIZE-1]
                    # Update steps and clear window
                    self.updateSteps()
                else:
                    # Last reading is the last element in window
                    lastReading = self.accWindow[len(self.accWindow) - 1]
                self.accWindow.append(lastReading + accIntervalChange)
                numIntervals -= 1

        self.prevTime = timeInMillis
        return

    # Public #
    def getStepCount(self):
        self.updateSteps()
        stepCount = self.stepCount
        # Clear step count to not double count in subsequent calls
        self.stepCount = 0
        return stepCount

    def updateSteps(self):
        if len(self.accWindow) != 0:
            # Count steps based on steps window
            self.stepCount += self.getStepsInWindow()
            # Clear the window after update to avoid double counting in the next update
            del self.accWindow[:]
        return

    def getStepsInWindow(self):
        # Holds the boolean var stating where a value has exceeded threshold
        stepsTime = []
        steps = 0

        maxAcc = self.ACC_REST + self.ACC_THRESHOLD

        # Record a detection on a falling edge from ACC_REST + ACC_THRESHOLD to normal
        for i in range(0, len(self.accWindow) - 1):
            if self.accWindow[i] > maxAcc > self.accWindow[i + 1]:
                stepsTime.append(i)

        # For debug
        # print(stepsTime)

        # If at least 1 detection
        if len(stepsTime) > 1:
            # If there is no previous detection
            if self.prevLastStepToEndTime == -1:
                i = 0           # Start comparing detections at 0 for curr window

            # If time interval between last detection of prev window and first detection of curr window is in range
            elif self.STEP_INTERVAL_TIME_LB <= self.prevLastStepToEndTime + stepsTime[0] <= self.STEP_INTERVAL_TIME_UB:
                steps += 1      # Count step for last detection in prev window
                i = 0           # Start comparing detections at 0 for curr window

            #  If first detection of curr window is too near to last detection of prev window
            elif self.prevLastStepToEndTime + stepsTime[0] < self.STEP_INTERVAL_TIME_LB:
                # Look through curr window and try to find a detection in range
                k = 1
                while k < len(stepsTime):
                    # Next detection in range
                    if self.STEP_INTERVAL_TIME_LB <= self.prevLastStepToEndTime + stepsTime[k] <= self.STEP_INTERVAL_TIME_UB:
                        steps += 1      # Count step
                        break
                    # Next detection too far apart
                    elif self.prevLastStepToEndTime + stepsTime[k] > self.STEP_INTERVAL_TIME_UB:
                        break
                    # Next detection too near
                    else:
                        k += 1

                i = k   # Start comparing detections at k for curr window

            #  If first detection of curr window is too far to last detection of prev window
            else:
                i = 0

            j = 1

            # If start comparing at the last detection, will not go into while loop
            if i + j >= len(stepsTime):
                # Count last step to end time from this time stamp to end of accWindow
                self.prevLastStepToEndTime = len(self.accWindow) - stepsTime[i] - 1

            while i + j < len(stepsTime):
                # If time interval between two detection is between range
                if self.STEP_INTERVAL_TIME_LB <= stepsTime[i + j] - stepsTime[i] <= self.STEP_INTERVAL_TIME_UB:
                    steps += 1  # Record as step
                    i += j  # Set next detection to test to the later detection
                    j = 1
                # If time interval between two interval is too short
                elif stepsTime[i + j] - stepsTime[i] < self.STEP_INTERVAL_TIME_LB:
                    j += 1      # Compare with the next detection
                # If time interval between two interval is too long
                else:
                    i += j  # Skip to the later detection and continue comparing afresh
                    j = 1
                # If detection being compared is the last one, record how many indexes is it to the end of window
                if i == len(stepsTime) - 1 or i + j > len(stepsTime) - 1:
                    self.prevLastStepToEndTime = len(self.accWindow) - stepsTime[i] - 1

        # If only 1 detection
        elif len(stepsTime) == 1:
            # If there is no previous detection
            if self.prevLastStepToEndTime == -1:
                self.prevLastStepToEndTime = len(self.accWindow) - stepsTime[0] - 1

            # If detection is in range
            elif self.STEP_INTERVAL_TIME_LB <= self.prevLastStepToEndTime + stepsTime[0] <= self.STEP_INTERVAL_TIME_UB:
                steps += 1      # Count steps
                self.prevLastStepToEndTime = len(self.accWindow) - stepsTime[0] - 1

            # If detection is too near the previous detection
            elif self.prevLastStepToEndTime + stepsTime[0] < self.STEP_INTERVAL_TIME_LB:
                # Add the whole accWindow side
                self.prevLastStepToEndTime += len(self.accWindow)

            # If detection is too far from the previous detection
            else:
                self.prevLastStepToEndTime = len(self.accWindow) - stepsTime[0] - 1

        # If no detections
        else:
            # Add the whole accWindow side
            self.prevLastStepToEndTime += len(self.accWindow)

        return steps
