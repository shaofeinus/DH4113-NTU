import json
import urllib2
import distAngleCalc
import os

# This module retrieves the map of the building (com1L2, com2L2, com2L3) in json format
# It then stores the in an adjacency matrix the following info:
# in top right half, distance in cm between nodes in adjacency matrix
# in bottom left half, angle between nodes
# angle always is calculated from the smaller index to the larger index
# negative angle means turn left, positive means right
# Adjacency matrix name is matrix

# API:
# mapParser()
# setMap(buildingName, levelNumber)
# getLocationName(index)
# getNorthAt()
# getLocationXCoord(index)
# getLocationYCoord(index)
# getAngle(point1, point2)
# getDistance(point1, point2)
# getNodeID()
# printMatrix()
# printJSONNodeData()
# index is in the range {0 to n-1}

class mapParser (object) :
        def __init__(self) :
                self.mapName = None
                self.buildingMap = {}
                self.northAt = 0
                self.numElements = 0
                self.matrix = []
                self.loadedMaps = ["com1L2.json", "com2L2.json", "com2L3.json",
                                   "1L2.json", "2L2.json", "2L3.json"]
                # list of coordinates where the map merges with another map
                # (startMap, endMap, x, y, differentLevel)
                # 0 = com1L2, 1 = com2L2, 2 = com2L3
                self.conList = [(0, 1, 11815, 406, 0), (1, 0, 61, 4024, 0),
                                (1, 2, 4329, 2317, 1), (2, 1, 4207, 2134, 1)]

        def clear(self) :
                self.buildingMap = {}
                self.northAt = 0
                self.numElements = 0
                self.matrix = []
                
        # returns the URL of the map
        def mapUrl(self, buildingName, levelNumber) :
                mapName = "http://ShowMyWay.comp.nus.edu.sg/getMapInfo.php?Building=" + str(buildingName) + "&Level=" + str(levelNumber)
                return mapName

        def isMapAlreadyLoaded(self, newMapName) :
                for i in self.loadedMaps :
                        if newMapName == i :
                                return True
                return False

        # load from text file
        def jsonFileInput(self, mapName) :        
                with open(mapName) as jsonMap:
                        self.buildingMap = json.load(jsonMap)
                        
        # load from server
        def jsonServerInput(self, buildingName, levelNumber) :
                # json server input
                jsonMap = urllib2.urlopen(self.mapUrl(buildingName, levelNumber))
                self.buildingMap = json.load(jsonMap)
        
        # return True if successful, False if unsuccessful
        def setMap(self, buildingName, levelNumber) :
                self.clear()
                mapName = str(buildingName) + "L" + str(levelNumber) + ".json"
                if(self.isMapAlreadyLoaded(mapName) is True) :
                        self.jsonFileInput(mapName)
                else :
                        try :
                                os.system("sudo ifmetric wlan0 100")
                                self.jsonServerInput(buildingName, levelNumber)
                        except :
                                return False

                if self.buildingMap['info'] is None :
                        return False
                      
                self.northAt = int(self.buildingMap['info']['northAt'])
                self.numElements = len(self.buildingMap.get('map'))
                self.matrix = [[0]*self.numElements for i in range(self.numElements)]
                self.fillAMatrix()
                return True

        
        def fillAMatrix(self) :
        # angle always is calculated from the smaller index to the larger index
        # negative angle means turn left, positive means right
                for i in range(self.numElements) :
                        self.linkString = self.buildingMap['map'][i]['linkTo']
                        self.linkArray = [int(s) for s in self.linkString.split(',')]
                        x1 = int(self.buildingMap['map'][i]['x'])
                        y1 = int(self.buildingMap['map'][i]['y'])
                        for j in self.linkArray :
                                x2 = int(self.buildingMap['map'][j-1]['x'])
                                y2 = int(self.buildingMap['map'][j-1]['y'])
                                if self.matrix[j-1][i] == 0 :
                                        self.matrix[i][j-1] = distAngleCalc.distance(
                                            x1, y1, x2, y2)
                                else :
                                        self.matrix[i][j-1] = distAngleCalc.calcAngle(
                                            x2, y2, x1, y1, self.northAt)

        # returns the location of North
        def getNorthAt(self) :
                return int(self.northAt)

        # returns the name of the location at the index
        def getLocationName(self, index) : 
               return self.buildingMap['map'][index]['nodeName']

        # returns the x-coordinate of the location at the index
        def getLocationXCoord(self, index) :
               return int(self.buildingMap['map'][index]['x'])

        # returns the y-coordinate of the location at the index
        def getLocationYCoord(self, index) :
               return int(self.buildingMap['map'][index]['y'])

        # returns the angle between 2 points wrt North
        def getAngle(self, point1, point2) :
               if point1 < point2 :
                       return self.matrix[point2][point1]
               else :
                       return (self.matrix[point1][point2] + 180)

        # returns the distance between 2 locations
        def getDistance(self, point1, point2) :
                if point1 < point2 :
                       return self.matrix[point1][point2]
                else :
                       return self.matrix[point2][point1]
                
        # returns a list of tuples(startMap, endMap, id, hasStairs) of a building connection
        def getNodeID(self) :
                connectionList = []              
                for i in xrange(len(self.conList)) :
                        tempX = int(self.conList[i][2])
                        tempY = int(self.conList[i][3])

                        for j in xrange(self.numElements) :
                                nodeX = int(self.buildingMap['map'][j]['x'])
                                nodeY = int(self.buildingMap['map'][j]['y'])
                                if ((nodeX == tempX) and (nodeY == tempY)) :
                                        connectionList.append(
                                                (self.conList[i][0], self.conList[i][1], j, self.conList[i][4]))
                return connectionList
                                
                
        def printMatrix(self) :
             print('\n'.join([''.join(['{:5}'.format(item) for item in row[0:15]])
                              for row in self.matrix[0:15]]))
                
        def printJSONNodeData(self) :
                print json.dumps(self.buildingMap.get('map'), indent=3)

        

