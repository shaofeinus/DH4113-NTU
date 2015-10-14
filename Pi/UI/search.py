import jsonParsingLite
import keypad_polling
from voiceCommands import speak

# TODO: change all print outputs into voice commands

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

        self.BUILDING_PROMPT = "Enter building name or number: "
        self.LEVEL_PROMPT = "Enter level number: "
        self.INVALID_BUILDING_LEVEL = "Sorry, the building or level number specified is invalid!"
        self.SEARCH_PROMPT = "Enter location point, /'id/' to enter a node id, or \'all\' for all nodes: "
        self.INVALID_NUMBER = "Please enter a valid number"
        self.FINAL_CONFIRMATION = "To confirm, press start. To restart, press hash"
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
        continueLoop = True
        while continueLoop:
            self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")
            self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)# raw_input("Enter level number: ")

            print "Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". To confirm, press start. To cancel, press hash"
            #speak("Building is " + self.buildingName + ", level is " + self.levelNumber + ". To confirm, press start. To cancel, press hash")

            continueLoop = self.keypad.get_binary_response()

        isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)
        # if an invalid building or level is given
        while isMapSetSuccessfully is False :
            # get building name and level number input from user (keypad code)
            print self.INVALID_BUILDING_LEVEL
            #speak(self.INVALID_BUILDING_LEVEL)
            while True:
                self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")
                self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)# raw_input("Enter level number: ")
                if self.levelNumber != -1:
                    break

            isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)

    def getSearchQueryFromUser(self) :
        while not self.possibleNodes :
            node = self.keypad.get_input_str(self.SEARCH_PROMPT)# raw_input("Enter location point, or \'all\' for all nodes: ")
            userInputNode = node.split()

            if node == "all" :
                for i in xrange(self.building.numElements) :
                    self.possibleNodes.append(i)
            elif node == "id":
                id_no = self.keypad.get_input_ext_num("Enter node ID: ")
                if 0 < id_no <= self.building.numElements:
                    self.possibleNodes.append(id_no - 1)
                else:
                    print self.INVALID_NUMBER
                    #speak(self.INVALID_NUMBER)
            else :
                for i in xrange(self.building.numElements) :
                    match = False
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
                    #speak("for " + str(self.building.getLocationName(self.possibleNodes[i])) + ", press"  + str(i))
                # get the user to choose the point he wants from the list of suggestions
                isNumberChosen = False
                while isNumberChosen is False :
                    self.locationPoint = int(self.keypad.get_input_ext_num("Enter number of correct location: "))# int(raw_input("Enter number of correct location: "))

                    if self.locationPoint < len(self.possibleNodes):
                        isNumberChosen = True
                        break
                    print self.INVALID_NUMBER
                    #speak(self.INVALID_NUMBER)
                self.locationPoint = self.possibleNodes[self.locationPoint]

            else :
                self.locationPoint = self.possibleNodes[0]
            print "Location selected is " + self.building.getLocationName(self.locationPoint) + " To confirm, press start. To cancel, press hash"#self.SELECTION_LOCATION
            #speak ("Location selected is " + self.building.getLocationName(self.locationPoint) + " To confirm, press start. To cancel, press hash")

            continueLoop = self.keypad.get_binary_response()
            if continueLoop:
                self.possibleNodes = []
                self.getSearchQueryFromUser()

    def confirmLocationWithUser(self) :
        print "You have selected building " + str(self.buildingName) + ", level " + str(self.levelNumber) + ", point \"" + str(self.building.getLocationName(self.locationPoint)) + "\""
        #speak("You have selected building " + str(self.buildingName) + ", level " + str(self.levelNumber) + ", point \"" + str(self.building.getLocationName(self.locationPoint)) + "\"")

        userInput = -123
        print self.FINAL_CONFIRMATION
        #speak(self.FINAL_CONFIRMATION)
        userInput = int(self.keypad.poll_for_num())# int(raw_input("To restart, press 0, else press any other key: "))

        print "TEST:", userInput
        if userInput == 10 : #10 is keypad number 0
            self.restart()
            self.run()



