import pedometer

__author__ = 'Shao Fei'

FILE_DIR = 'testdata/pedo_testdata.csv'

def main():
    indvSteps = 0
    totalSteps = 0
    pedo = pedometer.Pedometer()

    inputData(pedo)
    indvSteps = pedo.getStepCount()
    totalSteps += indvSteps
    print("Individual window steps:", indvSteps)

    inputData(pedo)
    indvSteps = pedo.getStepCount()
    totalSteps += indvSteps
    print("Individual window steps:", indvSteps)

    inputData(pedo)
    indvSteps = pedo.getStepCount()
    totalSteps += indvSteps
    print("Individual window steps:", indvSteps)

    print("Total steps:", totalSteps)
    return


def inputData(pedo):
    f = open(FILE_DIR, 'r')
    line = f.readline()
    while line:
        values = line.split(',')
        timeInMillis = values[0]
        accX = values[1]
        accY = values[2]
        accZ = values[3]
        pedo.updateWindow(int(accX), int(accY), int(accZ), int(timeInMillis))
        # print(timeInMillis, accX, accY, accZ)
        line = f.readline()
    return


