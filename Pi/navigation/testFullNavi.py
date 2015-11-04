import fullNavi
import threading
from collections import deque

voiceQueue = deque()
voiceSema = threading.Semaphore(0)
navi = fullNavi.fullNavi(voiceQueue, voiceSema)
navi.generateFullPath("com1", 2, 29, "com2", 2, 1)

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

if navi.hasNextPath() is True :
    navi.switchToPathList2()

while(navi.fullNavigate() is False) :
    x = int(raw_input("Enter x: "))

    y = int(raw_input("Enter y: "))
    heading = int(raw_input("Enter heading: "))
    navi.updateCurLocation(x, y, heading)
