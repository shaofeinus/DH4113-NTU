import p2pNavi

voiceQueue = None
voiceSema = None
p2p = p2pNavi.navigation(voiceQueue, voiceSema)

p2p.setNorthAt(0)
p2p.setPrevCoordinates(0, 0)
p2p.setNexCoordinates(1500, 1500)
p2p.setNextNodeName("random node")

isDone = 0
while(isDone == 0) :
    x = int(raw_input("x: "))
    y = int(raw_input("y: "))
    p2p.updateHeading(0)
    p2p.updateCurCoord(x, y)
    print "alrdy alerted: " + str(p2p.alreadyAlerted)
    isDone = p2p.navigate()

p2p.setNexCoordinates(2500, 2500)
isDone = 0
while(isDone == 0) :
    x = int(raw_input("x: "))
    y = int(raw_input("y: "))
    p2p.updateHeading(0)
    p2p.updateCurCoord(x, y)
    print "alrdy alerted: " + str(p2p.alreadyAlerted)
    isDone = p2p.navigate()
