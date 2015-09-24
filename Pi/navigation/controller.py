from p2pNavi import navigation
from jsonParsing import mapParser
#import dijkstra

com1L2 = mapParser("com1L2")
com2L2 = mapParser("com2L2")
com2L3 = mapParser("com2L3")

dummyDijkstraList = [1, 2, 4, 8]
numNodes = len(dummyDijkstraList)

for i in range(numNodes - 1) :
    northAt = com1L2.getNorthAt()
    prevX = com1L2.getLocationXCoord(i-1)
    prevY = com1L2.getLocationYCoord(i-1)
    nexX = com1L2.getLocationXCoord(i)
    nexY = com1L2.getLocationYCoord(i)
    
    path = navigation(prevX, prevY, nexX, nexY, northAt)
    path.startNavi()
    
