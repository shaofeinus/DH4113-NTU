import fullNavi
import threading
from collections import deque

voiceQueue = deque()
voiceSema = threading.Semaphore(0)
navi = fullNavi.fullNavi(voiceQueue, voiceSema)
navi.generateFullPath("com1", 2, 29, "com2", 3, 9)

x = int(raw_input("Enter x: "))
y = int(raw_input("Enter y: "))
heading = int(raw_input("Enter heading: "))
navi.updateCurLocation(x, y, heading)

count = 0
while(navi.fullNavigate() is False) :
    x = int(raw_input("Enter x: "))

    y = int(raw_input("Enter y: "))
    heading = int(raw_input("Enter heading: "))
    navi.updateCurLocation(x, y, heading)

print "You are now at the building connection."
proceed = raw_input("Enter any key to proceed: ")

if navi.hasNextPath() is True :
    navi.switchToNextPathList()
    print "Different level? " + str(navi.isDifferentLevel())
    print "North difference: " + str(navi.getNorthDifference())
    print "Initial coordinates: " + str(navi.getFirstCoordinates())

while(navi.fullNavigate() is False) :
    x = int(raw_input("Enter x: "))

    y = int(raw_input("Enter y: "))
    heading = int(raw_input("Enter heading: "))
    navi.updateCurLocation(x, y, heading)


print "You are now at the building connection."
proceed = raw_input("Enter any key to proceed: ")
if navi.hasNextPath() is True :
##        navi.switchToPathList3()
    navi.switchToNextPathList()
    print "Different level? " + str(navi.isDifferentLevel())
    print "North difference: " + str(navi.getNorthDifference())
    print "Initial coordinates: " + str(navi.getFirstCoordinates())

while(navi.fullNavigate() is False) :
    x = int(raw_input("Enter x: "))

    y = int(raw_input("Enter y: "))
    heading = int(raw_input("Enter heading: "))
    navi.updateCurLocation(x, y, heading)

while(navi.fullNavigate() is False) :
    print "HEY"

