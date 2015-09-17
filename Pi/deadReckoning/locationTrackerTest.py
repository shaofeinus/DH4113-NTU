import pedometer
import compass
import locationTracker
import pedoTest
import compassTest
import time

__author__ = 'Shao Fei'

def main():

    pedo = pedometer.Pedometer()
    comp = compass.Compass()
    locT = locationTracker.LocationTracker(pedo, comp, 0, 0)

    while 1:
        pedoTest.inputData(pedo)
        pedoTest.inputData(pedo)
        # pedoTest.inputData(pedo)
        # pedoTest.inputData(pedo)
        compassTest.inputRandData(comp)

        locT.updateLocation()
        print("Total Steps:", locT.getTotalSteps())
        print("Deviation from N:", comp.getHeadingInDeg())
        print(locT.getLocation())

        time.sleep(1)
    return

main()