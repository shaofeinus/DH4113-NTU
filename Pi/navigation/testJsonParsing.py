import jsonParsing

building = raw_input("Enter building name or number: ")
level = raw_input("Enter level: ")

maps = jsonParsing.mapParser()
maps.setMap(building, level)
print "distance is: " + str(maps.getDistance(0, 15))
maps.printMatrix()

print "********************************************************************"
maps.setMap(2, 3)
maps.printMatrix()
print "distance is: " + str(maps.getDistance(0, 15))
##for i in range(maps.numElements):
##    print maps.getLocationName(i)

##x = raw_input("Enter x: ");
##y = raw_input("Enter y: ");
##
##conList = maps.getNodeID()
##
##print conList


