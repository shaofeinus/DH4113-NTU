__author__ = 'Shao Fei'


class CalibrationTools:

    G_RAW_RANGE = (-32768, 32767)
    G_ACTUAL_RANGE = (-2.0, 2.0)
    Z_ACC_OFFSET = -1150
    X_ACC_OFFSET = 0
    Y_ACC_OFFSET = -200
    X_Y_ACC_SCALE_FACTOR = 32767.0 / 32000.0
    Y_ACC_SCALE_FACTOR = 32767.0 / 32150.0
    Z_ACC_SCALE_FACTOR = 32767.0 / 32600

    # MAG_X_RANGE = (-4328, 5605)
    # MAG_Y_RANGE = (-5096, 5002)
    # MAG_Z_RANGE = (-4655, 4618)

    MAG_X_RANGE = (-4068, 4759)
    MAG_Y_RANGE = (-4365, 4465)
    MAG_Z_RANGE = (-4363, 3878)

    def __init__(self):
        pass

    # x y z are the actual x y z axis of the the IMU
    def transformACC(self, accX, accY, accZ):

        accZ += self.Z_ACC_OFFSET
        accX += self.X_ACC_OFFSET
        accY += self.Y_ACC_OFFSET

        accZ *= self.Z_ACC_SCALE_FACTOR
        accX *= self.X_Y_ACC_SCALE_FACTOR
        accY *= self.Y_ACC_SCALE_FACTOR

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

    def transformMag(self, magX, magY, magZ):
        # Hard iron correction
        magX -= (self.MAG_X_RANGE[1] + self.MAG_X_RANGE[0]) / 2.0
        magY -= (self.MAG_Y_RANGE[1] + self.MAG_Y_RANGE[0]) / 2.0
        magZ -= (self.MAG_Z_RANGE[1] + self.MAG_Z_RANGE[0]) / 2.0

        # print 'after hard iron correction:', magX, magY, magZ

        # Soft iron correction
        magX = float(magX - self.MAG_X_RANGE[0]) / float(self.MAG_X_RANGE[1] - self.MAG_X_RANGE[0]) * 2.0 - 1.0
        magY = float(magY - self.MAG_Y_RANGE[0]) / float(self.MAG_Y_RANGE[1] - self.MAG_Y_RANGE[0]) * 2.0 - 1.0
        magZ = float(magZ - self.MAG_Z_RANGE[0]) / float(self.MAG_Z_RANGE[1] - self.MAG_Z_RANGE[0]) * 2.0 - 1.0

        return magX, magY, magZ
