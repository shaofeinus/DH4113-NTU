import jsonParsingLite

building = jsonParsingLite.mapParser()

# get building name and level number input from user (keypad code)
buildingName = raw_input("Enter building name or number: ")
levelNumber = raw_input("Enter level number: ")

isMapSetSuccessfully = building.setMap(buildingName, levelNumber)
# if an invalid building or level is given
while isMapSetSuccessfully is False :
    # get building name and level number input from user (keypad code)
    print "Sorry, the building or level number specified is invalid!"
    buildingName = raw_input("Enter building name: ")
    levelNumber = raw_input("Enter level number: ")
    isMapSetSuccessfully = building.setMap(buildingName, levelNumber)

node = raw_input("Enter location point: ")
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

    # get the user to choose the point he wants from the list of suggestions
    isNumberChosen = False
    while isNumberChosen is False :
        try :
            start = int(raw_input("Enter number of correct location: "))
        except :
            pass
        if start < len(possibleNodes) :
            isNumberChosen = True
            break
        print "Please enter a valid number"

    start = possibleNodes[start]
    
else :
    start = possibleNodes[0]


