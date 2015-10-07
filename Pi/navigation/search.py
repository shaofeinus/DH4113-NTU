import jsonParsing

building = jsonParsing.mapParser()
buildingName = raw_input("Enter building name or number: ")
levelNumber = raw_input("Enter level number: ")
isMapSetSuccessfully = building.setMap(buildingName, levelNumber)
while isMapSetSuccessfully is False :
    print "Sorry, the building or level number specified is invalid!"
    buildingName = raw_input("Enter building name: ")
    levelNumber = raw_input("Enter level number: ")
    isMapSetSuccessfully = building.setMap(buildingName, levelNumber)

node = raw_input("Enter starting node: ")
userInputNode = node.split()

possibleNodes = []
for i in xrange(building.numElements) :
    for j in xrange(len(userInputNode)) :
        match = userInputNode[j].lower() in building.getLocationName(i).lower()
        if match is False :
            break
    if match is True :
        possibleNodes.append(i)
        
if len(possibleNodes) > 1 :
    for i in xrange(len(possibleNodes)) :
        print str(i) + ": " + str(building.getLocationName(possibleNodes[i]))
        
    start = int(raw_input("Enter correct node: "))
    while start >= len(possibleNodes) :
        start = int(raw_input("Enter correct node: "))
    start = possibleNodes[start]
else :
    start = possibleNodes[0]


