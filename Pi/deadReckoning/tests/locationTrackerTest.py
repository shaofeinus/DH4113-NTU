import time

import FindMyWay.Pi.deadReckoning.pedometer
import FindMyWay.Pi.deadReckoning.compass
import FindMyWay.Pi.deadReckoning.locationTracker
import pedoTest
import compassTest

__author__ = 'Shao Fei'

def main():

    pedo = FindMyWay.Pi.deadReckoning.pedometer.Pedometer()
    comp = FindMyWay.Pi.deadReckoning.compass.Compass()
    locT = FindMyWay.Pi.deadReckoning.locationTracker.LocationTracker(pedo, comp, 0, 0)

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