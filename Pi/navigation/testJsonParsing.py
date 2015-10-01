import jsonParsing

com1L2 = jsonParsing.mapParser()
com1L2.setMap("com2", 3)

for i in range(com1L2.numElements):
    print com1L2.getLocationName(i)

watever = jsonParsing.mapParser()
watever.setMap("watever", 99)

for i in range(watever.numElements):
    print watever.getLocationName(i)
    

print "first location: " + str(com1L2.getLocationYCoord(0))
