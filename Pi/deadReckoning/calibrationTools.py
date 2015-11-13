from collections import deque
import math

__author__ = 'Shao Fei'


class CalibrationTools:

    G_RAW_RANGE = (-32767, 32767)
    G_ACTUAL_RANGE = (-2.0, 2.0)
    ACC_Z_OFFSET = -1150
    ACC_X_OFFSET = 0
    ACC_Y_OFFSET = -200
    X_ACC_SCALE_FACTOR = 32767.0 / 32000.0
    Y_ACC_SCALE_FACTOR = 32767.0 / 32150.0
    Z_ACC_SCALE_FACTOR = 32767.0 / 32600.0

    # MAG_X_RANGE = (-4068, 4759)
    # MAG_Y_RANGE = (-4365, 4465)
    # MAG_Z_RANGE = (-4363, 3878)
    MAG_X_RANGE = (-4239, 5043)
    MAG_Y_RANGE = (-4571, 4820)
    MAG_Z_RANGE = (-4814, 3937)

    # MAG_X_OFFSET = (MAG_X_RANGE[1] + MAG_X_RANGE[0]) / 2.0
    # MAG_Y_OFFSET = (MAG_Y_RANGE[1] + MAG_Y_RANGE[0]) / 2.0
    # MAG_Z_OFFSET = (MAG_Z_RANGE[1] + MAG_Z_RANGE[0]) / 2.0
    # MAG_X_OFFSET_RANGE = (MAG_X_RANGE[0] - MAG_X_OFFSET, MAG_X_RANGE[1] - MAG_X_OFFSET)
    # MAG_Y_OFFSET_RANGE = (MAG_Y_RANGE[0] - MAG_Y_OFFSET, MAG_Y_RANGE[1] - MAG_Y_OFFSET)
    # MAG_Z_OFFSET_RANGE = (MAG_Z_RANGE[0] - MAG_Z_OFFSET, MAG_Z_RANGE[1] - MAG_Z_OFFSET)

    MAG_X_SCALE_FACTOR = 1.0
    MAG_Y_SCALE_FACTOR = 0.999064084 # 1.000648985
    MAG_Z_SCALE_FACTOR = 0.933922909 # 0.932667875

    MAG_X_OFFSET = 298.7836281 # 308.4580249
    MAG_Y_OFFSET = 121.9181556 # 117.8145883
    MAG_Z_OFFSET = -419.8298189 # -436.2063372

    AV_RAW_RANGE = (-28000, 28000)
    AV_ACTUAL_RANGE = (-245.0 / 180.0 * math.pi, 245.0 / 180.0 * math.pi)
    GY_X_OFFSET = 0.0
    GY_Y_OFFSET = 0.0
    GY_Z_OFFSET = 0.0
    GY_X_SCALE_FACTOR = 1.0
    GY_Y_SCALE_FACTOR = 1.0
    GY_Z_SCALE_FACTOR = 1.0
    GY_OFFSET_MA_WINDOW_SIZE = 500
    GY_RECALIBRATE_THRESHOLD = 10

    def __init__(self):
        self.gyXOffsetWindow = deque(maxlen=self.GY_OFFSET_MA_WINDOW_SIZE)
        self.gyYOffsetWindow = deque(maxlen=self.GY_OFFSET_MA_WINDOW_SIZE)
        self.gyZOffsetWindow = deque(maxlen=self.GY_OFFSET_MA_WINDOW_SIZE)

    # x y z are the actual x y z axis of the the IMU
    # returns in Gs
    def transformACC(self, accX, accY, accZ):

        accX += self.ACC_X_OFFSET
        accY += self.ACC_Y_OFFSET
        accZ += self.ACC_Z_OFFSET

        accX *= self.X_ACC_SCALE_FACTOR
        accY *= self.Y_ACC_SCALE_FACTOR
        accZ *= self.Z_ACC_SCALE_FACTOR

        accX = float(accX) * self.G_ACTUAL_RANGE[1] / self.G_RAW_RANGE[1]
        accY = float(accY) * self.G_ACTUAL_RANGE[1] / self.G_RAW_RANGE[1]
        accZ = float(accZ) * self.G_ACTUAL_RANGE[1] / self.G_RAW_RANGE[1]

        return accX, accY, accZ

    # x y z are the actual x y z axis of the the IMU
    # returns in fraction of max range
    def transformMag(self, magX, magY, magZ):

        # Hard iron correction
        magX -= self.MAG_X_OFFSET
        magY -= self.MAG_Y_OFFSET
        magZ -= self.MAG_Z_OFFSET

        # Soft iron correction
        # magX = float(magX) / self.MAG_X_OFFSET_RANGE[1]
        # magY = float(magY) / self.MAG_Y_OFFSET_RANGE[1]
        # magZ = float(magZ) / self.MAG_Z_OFFSET_RANGE[1]

        magX = float(magX) / self.MAG_X_SCALE_FACTOR
        magY = float(magY) / self.MAG_Y_SCALE_FACTOR
        magZ = float(magZ) / self.MAG_Z_SCALE_FACTOR

        return magX, magY, magZ

    # x y z are axis of rotation of actual x y z axis of the the IMU
    # returns in rad/s
    def transformGyro(self, gyX, gyY, gyZ):

        self.adaptGyroOffset(gyX, gyY, gyZ)

        gyX -= self.GY_X_OFFSET
        gyY -= self.GY_Y_OFFSET
        gyZ -= self.GY_Z_OFFSET

        # gyX *= self.GY_X_SCALE_FACTOR
        # gyY *= self.GY_Y_SCALE_FACTOR
        # gyZ *= self.GY_Z_SCALE_FACTOR

        gyX = float(gyX) * self.AV_ACTUAL_RANGE[1] / self.AV_RAW_RANGE[1]
        gyY = float(gyY) * self.AV_ACTUAL_RANGE[1] / self.AV_RAW_RANGE[1]
        gyZ = float(gyZ) * self.AV_ACTUAL_RANGE[1] / self.AV_RAW_RANGE[1]

        return gyX, gyY, gyZ

    def adaptGyroOffset(self, gyX, gyY, gyZ):
        if math.fabs(gyX - self.GY_X_OFFSET) < self.GY_RECALIBRATE_THRESHOLD:
            # print 'gyro x offset update'
            self.gyXOffsetWindow.append(gyX)
        if math.fabs(gyY - self.GY_Y_OFFSET) < self.GY_RECALIBRATE_THRESHOLD:
            self.gyYOffsetWindow.append(gyY)
            # print 'gyro y offset update'
        if math.fabs(gyZ - self.GY_Z_OFFSET) < self.GY_RECALIBRATE_THRESHOLD:
            self.gyZOffsetWindow.append(gyZ)
            # print 'gyro z offset update'

        self.GY_X_OFFSET = float(sum(self.gyXOffsetWindow)) / float(len(self.gyXOffsetWindow))
        self.GY_Y_OFFSET = float(sum(self.gyYOffsetWindow)) / float(len(self.gyYOffsetWindow))
        self.GY_Z_OFFSET = float(sum(self.gyZOffsetWindow)) / float(len(self.gyZOffsetWindow))

    def initGyroOffset(self, gyX, gyY, gyZ):
        self.GY_X_OFFSET = gyX
        self.GY_Y_OFFSET = gyY
        self.GY_Z_OFFSET = gyZ
        self.gyXOffsetWindow.append(gyX)
        self.gyYOffsetWindow.append(gyY)
        self.gyZOffsetWindow.append(gyZ)
