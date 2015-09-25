import FindMyWay.Pi.deadReckoning.compass
import random

__author__ = 'Shao Fei'

FILE_DIR = 'testdata/comp_testdata.csv'


def main():
    comp = FindMyWay.Pi.deadReckoning.compass.Compass()
    inputData(comp)
    return


def inputData(comp, shouldPrint):
    f = open(FILE_DIR, 'r')
    line = f.readline()

    while line:
        values = line.split(',')
        magX = int(values[0])
        magY = int(values[1])
        comp.updateReading(magX, magY)
        line = f.readline()
        if shouldPrint:
            print("Degrees from N:", comp.getHeadingInRad())

    f.close()
    return


def inputRandData(comp):
    magX = random.randint(-1000, 1000)
    magY = random.randint(-1000, 1000)
    comp.updateReading(magX, magY)
    return

