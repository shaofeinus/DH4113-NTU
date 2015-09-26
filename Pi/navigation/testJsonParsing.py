import jsonParsing

com1L2 = jsonParsing.mapParser("com1L2")
com2L2 = jsonParsing.mapParser("com2L2")
com2L3 = jsonParsing.mapParser("com2L3")

for i in range(com1L2.numElements):
    print com1L2.getLocationName(i)

for i in range(com2L2.numElements):
    print com2L2.getLocationName(i)

for i in range(com2L3.numElements):
    print com2L3.getLocationName(i)

