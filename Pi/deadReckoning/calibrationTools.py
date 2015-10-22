from collections import deque
import math

__author__ = 'Shao Fei'


class CalibrationTools:

    G_RAW_RANGE = (-32768, 32767)
    G_ACTUAL_RANGE = (-2.0, 2.0)
    ACC_Z_OFFSET = -1150
    ACC_X_OFFSET = 0
    ACC_Y_OFFSET = -200
    X_ACC_SCALE_FACTOR = 32767.0 / 32000.0
    Y_ACC_SCALE_FACTOR = 32767.0 / 32150.0
    Z_ACC_SCALE_FACTOR = 32767.0 / 32600

    MAG_X_RANGE = (-4068, 4759)
    MAG_Y_RANGE = (-4365, 4465)
    MAG_Z_RANGE = (-4363, 3878)

    AV_RAW_RANGE = (-28000, 28000)
    AV_ACTUAL_RANGE = (-245.0 / 180.0 * math.pi, 245.0 / 180.0 * math.pi)
    GY_X_OFFSET = -76.38
    GY_Y_OFFSET = -553.19
    GY_Z_OFFSET = 57.45
    GY_X_SCALE_FACTOR = 1.0
    GY_Y_SCALE_FACTOR = 1.0
    GY_Z_SCALE_FACTOR = 1.0
    GY_OFFSET_MA_WINDOW_SIZE = 100
    GY_RECALIBRATE_THRESHOLD = 10

    def __init__(self):
        self.gyroXOffsetWindow = deque(maxlen=self.GY_OFFSET_MA_WINDOW_SIZE)
        self.gyroYOffsetWindow = deque(maxlen=self.GY_OFFSET_MA_WINDOW_SIZE)
        self.gyroZOffsetWindow = deque(maxlen=self.GY_OFFSET_MA_WINDOW_SIZE)

    # x y z are the actual x y z axis of the the IMU
    # returns in Gs
    def transformACC(self, accX, accY, accZ):

        accX += self.ACC_X_OFFSET
        accY += self.ACC_Y_OFFSET
        accZ += self.ACC_Z_OFFSET

        accX *= self.X_ACC_SCALE_FACTOR
        accY *= self.Y_ACC_SCALE_FACTOR
        accZ *= self.Z_ACC_SCALE_FACTOR

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

    # x y z are the actual x y z axis of the the IMU
    # returns in fraction of max range
    def transformMag(self, magX, magY, magZ):

        # Hard iron correction
        magX -= (self.MAG_X_RANGE[1] + self.MAG_X_RANGE[0]) / 2.0
        magY -= (self.MAG_Y_RANGE[1] + self.MAG_Y_RANGE[0]) / 2.0
        magZ -= (self.MAG_Z_RANGE[1] + self.MAG_Z_RANGE[0]) / 2.0

        # Soft iron correction
        magX = float(magX - self.MAG_X_RANGE[0]) / float(self.MAG_X_RANGE[1] - self.MAG_X_RANGE[0]) * 2.0 - 1.0
        magY = float(magY - self.MAG_Y_RANGE[0]) / float(self.MAG_Y_RANGE[1] - self.MAG_Y_RANGE[0]) * 2.0 - 1.0
        magZ = float(magZ - self.MAG_Z_RANGE[0]) / float(self.MAG_Z_RANGE[1] - self.MAG_Z_RANGE[0]) * 2.0 - 1.0

        return magX, magY, magZ

    # x y z are axis of rotation of actual x y z axis of the the IMU
    # returns in rad/s
    def transformGyro(self, gyX, gyY, gyZ):

        # self.adaptGyroOffset(self, gyX, gyY, gyZ)

        gyX += self.GY_X_OFFSET
        gyY += self.GY_Y_OFFSET
        gyZ += self.GY_Z_OFFSET

        gyX *= self.GY_X_SCALE_FACTOR
        gyY *= self.GY_Y_SCALE_FACTOR
        gyZ *= self.GY_Z_SCALE_FACTOR

        gyX = (float(gyX - self.AV_RAW_RANGE[0]) / float(self.AV_RAW_RANGE[1] - self.AV_RAW_RANGE[0])) * \
              (self.AV_ACTUAL_RANGE[1] - self.AV_ACTUAL_RANGE[0]) + \
              (self.AV_ACTUAL_RANGE[0])
        gyY = (float(gyY - self.AV_RAW_RANGE[0]) / float(self.AV_RAW_RANGE[1] - self.AV_RAW_RANGE[0])) * \
              (self.AV_ACTUAL_RANGE[1] - self.AV_ACTUAL_RANGE[0]) + \
              (self.AV_ACTUAL_RANGE[0])
        gyZ = (float(gyZ - self.AV_RAW_RANGE[0]) / float(self.AV_RAW_RANGE[1] - self.AV_RAW_RANGE[0])) * \
              (self.AV_ACTUAL_RANGE[1] - self.AV_ACTUAL_RANGE[0]) + \
              (self.AV_ACTUAL_RANGE[0])

        # TODO: convert to rad/s

        return gyX, gyY, gyZ

    def adaptGyroOffset(self, gyX, gyY, gyZ):

        self.gyroXOffsetWindow.append(gyX)
        self.gyroYOffsetWindow.append(gyY)
        self.gyroZOffsetWindow.append(gyZ)

        if len(self.gyroXOffsetWindow) < self.GY_OFFSET_MA_WINDOW_SIZE:
            return
        else:
            newX = float(sum(self.gyroXOffsetWindow)) / len(self.gyroXOffsetWindow)
            newY = float(sum(self.gyroYOffsetWindow)) / len(self.gyroYOffsetWindow)
            newZ = float(sum(self.gyroZOffsetWindow)) / len(self.gyroZOffsetWindow)

            if math.fabs(newX - self.GY_X_OFFSET) < self.GY_RECALIBRATE_THRESHOLD:
                self.GY_X_OFFSET = -newX

            if math.fabs(newY - self.GY_Y_OFFSET) < self.GY_RECALIBRATE_THRESHOLD:
                self.GY_Y_OFFSET = -newY

            if math.fabs(newZ - self.GY_Z_OFFSET) < self.GY_RECALIBRATE_THRESHOLD:
                self.GY_Z_OFFSET = -newZ

    def initGyroOffset(self, gyX, gyY, gyZ):
        self.GY_X_OFFSET = gyX
        self.GY_Y_OFFSET = gyY
        self.GY_Z_OFFSET = gyZ
