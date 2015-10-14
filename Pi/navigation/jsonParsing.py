import json
import urllib2
import distAngleCalc

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
# printMatrix()
# printJSONNodeData()
# index is in the range {0 to n-1}

class mapParser (object) :
        def __init__(self) :
                self.mapName = None
                self.buildingMap = {}
                self.northAt = 0
                self.numElements = 0
                self.matrix = {}
                self.loadedMaps = ["lab2L1.json", "com1L2.json", "com2L2.json", "com2L3.json"]
                
        
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
                mapName = str(buildingName) + "L" + str(levelNumber) + ".json"
                if(self.isMapAlreadyLoaded(mapName) is True) :
                        self.jsonFileInput(mapName)
                else :
                        self.jsonServerInput(buildingName, levelNumber)

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

        def printMatrix(self) :
             print('\n'.join([''.join(['{:5}'.format(item) for item in row[0:15]])
                              for row in self.matrix[0:15]]))
                
        def printJSONNodeData(self) :
                print json.dumps(self.buildingMap.get('map'), indent=3)

        

