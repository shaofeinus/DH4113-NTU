import jsonParsingLite
import keypad_polling

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
        self.keypad = keypad_polling.keypad()
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
        while True:
            self.buildingName = self.keypad.get_input_str("Enter building name or number: ")# raw_input("Enter building name or number: ")
            self.levelNumber = self.keypad.get_input_ext_num("Enter level number: ")# raw_input("Enter level number: ")
            if self.levelNumber != -1:
                break
            print "Input Cancelled"

        isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)
        # if an invalid building or level is given
        while isMapSetSuccessfully is False :
            # get building name and level number input from user (keypad code)
            print "Sorry, the building or level number specified is invalid!"
            while True:
                self.buildingName = self.keypad.get_input_str("Enter building name or number: ")# raw_input("Enter building name or number: ")
                self.levelNumber = self.keypad.get_input_ext_num("Enter level number: ")# raw_input("Enter level number: ")
                if self.levelNumber != -1:
                    break
                print "Input Cancelled"
            isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)



    def getSearchQueryFromUser(self) :
        while not self.possibleNodes :
            node = self.keypad.get_input_str("Enter location point, or \'all\' for all nodes: ")# raw_input("Enter location point, or \'all\' for all nodes: ")
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
        continueLoop = True
        while continueLoop:
            if len(self.possibleNodes) > 1 :
                for i in xrange(len(self.possibleNodes)) :
                    print str(i) + ": " + str(self.building.getLocationName(self.possibleNodes[i]))

                # get the user to choose the point he wants from the list of suggestions
                isNumberChosen = False
                while isNumberChosen is False :
                    try :
                        self.locationPoint = int(self.keypad.get_input_ext_num("Enter number of correct location: "))# int(raw_input("Enter number of correct location: "))
                    except :
                        pass
                    if self.locationPoint < len(self.possibleNodes) :
                        isNumberChosen = True
                        continueLoop = False
                        break
                    print "Please enter a valid number"

                self.locationPoint = self.possibleNodes[self.locationPoint]

            else :
                self.locationPoint = self.possibleNodes[0]
                print "Is \"", self.building.getLocationName(self.locationPoint), "\" correct? start = YES, # = NO"
                num = 0
                while True:
                    num = self.keypad.poll_for_num()
                    if num == 11:
                        self.possibleNodes = []
                        self.getSearchQueryFromUser()
                        print "Input Cancelled"
                        break
                    elif num == 9:
                        continueLoop = False
                        break



    def confirmLocationWithUser(self) :
        print "You have selected building ",
        print str(self.buildingName),
        print ", level " + str(self.levelNumber),
        print ", point \"" + str(self.building.getLocationName(self.locationPoint)) + "\""
        try :
            print "To restart, press 0, else press any other key: "
            userInput = int(self.keypad.poll_for_num())# int(raw_input("To restart, press 0, else press any other key: "))
        except :
            pass

        if userInput == 10 : #10 is keypad number 0
            self.restart()
            self.run()



