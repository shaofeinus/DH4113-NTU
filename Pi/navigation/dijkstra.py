import sys
import Queue
from jsonParsing import mapParser    

#USAGE:
#1) Create an instance of pathFinder object
#2) Call setMap(mapNo) to set the map
#       0: COM1L2
#       1: COM2L2
#       2: COM3L3
#3) Call getPath(). Function returns path in a node sequence stored in list
#4) PROFIT $$$

class pathFinder (object) :
    def __init__(self):
        self.currMap = None
        self.mapNo = None
        self.redNodes = []
        self.nodes = []
        self.tree = []

    def init(self):
        for x in range(self.NUM_NODES):
            self.redNodes = [0 for x in range(self.NUM_NODES)]
            self.nodes = [sys.maxint for x in range(self.NUM_NODES)]
        
    def isAllRed(self):
        for x in self.redNodes:
             if x == 0:
                return 0
        return 1
             
    def getMinDistNode(self):
        minDist = sys.maxint
        minIndex = -1

        for x in range(self.NUM_NODES):
             if self.redNodes[x] == 0 and self.nodes[x] < minDist:
                 minIndex = x
                 minDist = self.nodes[x]
        return minIndex

    def relax(self, v, w):
        d = self.nodes[v] + self.currMap.getDistance(v, w)#adj[v][w]
        if self.nodes[w] > d:
             self.nodes[w] = d
             isFound = 0
             for x in self.tree:
                 if x[1] == w:
                     x[0] = v
                     isFound = 1
             if isFound == 0:
                 newEdge = [v,w]
                 self.tree.append(newEdge)
             
    def dijkstra (self, start):
        self.init()
        self.nodes[start] = 0
        
        while (self.isAllRed() == 0):
            v = self.getMinDistNode()
            self.redNodes[v] = 1
            
            for w in range(self.NUM_NODES):
                if w != v and self.currMap.getDistance(v, w) > 0:
                    self.relax(v, w)
                
    def isInTree(self, start, end):
        for x in self.tree:
            if x[0] == start and x[1] == end:
                return True
        return False

    def getPath(self, start, end):
        start = start - 1
        end = end - 1
        rev = False

        if (start > end):
            start, end = end, start
            rev = True

        self.dijkstra(start)
        self.init()
        path = [start]

        while path[len(path) - 1] != end:
            isFound = False
            for x in self.tree:
                if x[0] == path[len(path) - 1] and self.redNodes[x[1]] == 0:
                    path.append(x[1])
                    isFound = True
                    break
            if not isFound:
                self.redNodes[path.pop()] = 1

        if rev == True:
            path.reverse()
        return path
    
    def setMap(self, mapNo):
        self.mapNo = mapNo
        
        if self.mapNo == 0:
            self.currMap = mapParser("com1L2")
        elif self.mapNo == 1:
            self.currMap = mapParser("com2L2")
        elif self.mapNo == 2:
            self.currMap = mapParser("com2L3")
            
        self.NUM_NODES = self.currMap.numElements
    
