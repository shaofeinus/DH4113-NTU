import json
import urllib2

# API:
# mapParser()
# setMap(buildingName, levelNumber)
# getLocationName(index)
# printJSONNodeData()
# index is in the range {0 to n-1}

class mapParser (object) :
        def __init__(self) :
                self.mapName = None
                self.buildingMap = {}
                self.numElements = 0
                self.loadedMaps = ["com1L2.json", "com2L2.json", "com2L3.json"]
                
        
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
                        try :               
                                self.jsonServerInput(buildingName, levelNumber)
                        except :
                                return False

                if self.buildingMap['info'] is None :
                        return False
                        
                self.numElements = len(self.buildingMap.get('map'))
                return True

        # returns the name of the location at the index
        def getLocationName(self, index) : 
               return self.buildingMap['map'][index]['nodeName']

        def printJSONNodeData(self) :
                print json.dumps(self.buildingMap.get('map'), indent=3)

        

