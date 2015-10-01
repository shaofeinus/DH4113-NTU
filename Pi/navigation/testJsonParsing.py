import jsonParsing

com1L2 = jsonParsing.mapParser()
com1L2.setMap("com1", 2)

for i in range(com1L2.numElements):
    print com1L2.getLocationName(i)


    

print "first location: " + str(com1L2.getLocationYCoord(0))
