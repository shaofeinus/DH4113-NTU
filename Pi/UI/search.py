import jsonParsingLite

# TODO: change all keyboard inputs into keypad input,
#       change all print outputs into voice commands

# API:
# getBuildingName()
# getLevelNumber()
# getLocationPointIndex()

class locationSetting(object) :
    def __init__(self) :
        self.buildingName = None
        self.levelNumber = None
        self.locationPoint = None
        self.possibleNodes = []
        self.building = jsonParsingLite.mapParser()
        self.run()

    def run(self) :
        self.getBuildingFromUser()
        self.getSearchQueryFromUser()
        self.getExactLocationFromUser()
        self.confirmLocationWithUser()

    def restart(self) :
        self.buildingName = None
        self.levelNumber = None
        self.locationPoint = None
        self.possibleNodes = []


    def getBuildingName(self) :
        return self.buildingName

    def getLevelNumber(self) :
        return self.levelNumber

    def getLocationPointIndex(self) :
        return self.locationPoint
        

    def getBuildingFromUser(self) :
        # get building name and level number input from user (keypad code)
        self.buildingName = raw_input("Enter building name or number: ")
        self.levelNumber = raw_input("Enter level number: ")

        isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)
        # if an invalid building or level is given
        while isMapSetSuccessfully is False :
            # get building name and level number input from user (keypad code)
            print "Sorry, the building or level number specified is invalid!"
            self.buildingName = raw_input("Enter building name or number: ")
            self.levelNumber = raw_input("Enter level number: ")
            isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)


    def getSearchQueryFromUser(self) :
        while not self.possibleNodes :
            node = raw_input("Enter location point, or \'all\' for all nodes: ")
            userInputNode = node.split()

            if node == "all" :
                for i in xrange(self.building.numElements) :
                    self.possibleNodes.append(i)
            else :
                for i in xrange(self.building.numElements) :
                    for j in xrange(len(userInputNode)) :
                        match = userInputNode[j].lower() in self.building.getLocationName(i).lower()
                        if match is False :
                            break
                    if match is True :
                        self.possibleNodes.append(i)


    def getExactLocationFromUser(self) :
        if len(self.possibleNodes) > 1 :
            for i in xrange(len(self.possibleNodes)) :
                print str(i) + ": " + str(self.building.getLocationName(self.possibleNodes[i]))

            # get the user to choose the point he wants from the list of suggestions
            isNumberChosen = False
            while isNumberChosen is False :
                try :
                    self.locationPoint = int(raw_input("Enter number of correct location: "))
                except :
                    pass
                if self.locationPoint < len(self.possibleNodes) :
                    isNumberChosen = True
                    break
                print "Please enter a valid number"

            self.locationPoint = self.possibleNodes[self.locationPoint]
            
        else :
            self.locationPoint = self.possibleNodes[0]

    def confirmLocationWithUser(self) :
        print "You have selected building ",
        print str(self.buildingName),
        print ", level " + str(self.levelNumber),
        print ", point \"" + str(self.building.getLocationName(self.locationPoint)) + "\""
        try :
            userInput = int(raw_input("To restart, press 0, else press any other key: "))
        except :
            pass

        if userInput == 0 :
            self.restart()
            self.run()



