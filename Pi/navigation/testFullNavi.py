import fullNavi
import threading
from collections import deque

voiceQueue = deque()
voiceSema = threading.Semaphore(0)
navi = fullNavi.fullNavi(voiceQueue, voiceSema)
navi.generateFullPath("com2", 2, 15, "com2", 3, 8)

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
proceed = raw_input("Press any key to proceed: ")

if navi.hasNextPath() is True :
    navi.switchToPathList2()

while(navi.fullNavigate() is False) :
    x = int(raw_input("Enter x: "))

    y = int(raw_input("Enter y: "))
    heading = int(raw_input("Enter heading: "))
    navi.updateCurLocation(x, y, heading)
