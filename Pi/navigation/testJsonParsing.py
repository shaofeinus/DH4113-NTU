from jsonParsing import mapParser

com1L2 = mapParser("com1L2")
com2L2 = mapParser("com2L2")
com2L3 = mapParser("com2L3")

for i in range(com1L2.numElements):
    print com1L2.getLocationName(i)

for i in range(com2L2.numElements):
    print com2L2.getLocationName(i)

for i in range(com2L3.numElements):
    print com2L3.getLocationName(i)

