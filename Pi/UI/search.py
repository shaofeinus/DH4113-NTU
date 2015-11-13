import jsonParsingLite
import keypad_polling
import threading
import time
from collections import deque
# from voiceCommands import speak

# TODO: change all print outputs into voice commands

class locationSetting(object) :
    def __init__(self, isEndLocation, keypad, voiceSema, speaker) :
        self.buildingName = None
        self.levelNumber = None
        self.locationPoint = None
        self.possibleNodes = []
        self.building = jsonParsingLite.mapParser()
        self.keypad = keypad
        self.isEndLocation = isEndLocation
        self.voiceSema = voiceSema
        self.speaker = speaker

        self.BUILDING_PROMPT = "Enter building name or number: "
        self.LEVEL_PROMPT = "Enter level number: "
        self.INVALID_BUILDING_LEVEL = "Sorry, the building or level number specified is invalid!"
        self.SEARCH_PROMPT = "Enter search query for location. For help, enter: \"help\"."
        self.SEARCH_HELP1 = "To retrieve all nodes, enter, all. "
        self.SEARCH_HELP2 = "To select a node ID, enter, dot. "
        self.SEARCH_HELP3 = "Followed by the node ID. "
        self.INVALID_NUMBER = "Please enter a valid number"
        self.INVALID_ID = "Please enter a valid ID"

    def run(self) :
        self.getBuildingFromUser()
        self.getSearchQueryFromUser()
        self.getExactLocationFromUser()

    def setBuildingAndLevel(self, building, level):
        self.buildingName = building
        self.levelNumber = level

    def getBuildingName(self) :
        return self.buildingName

    def getLevelNumber(self) :
        return self.levelNumber

    def getLocationPointIndex(self) :
        return self.locationPoint

    def getLocationXCoord(self) :
        return self.building.getLocationXCoord(self.locationPoint - 1)

    def getLocationYCoord(self) :
        return self.building.getLocationYCoord(self.locationPoint - 1)

    def getBuildingFromUser(self) :
        # get building name and level number input from user (keypad code)

        while True: #isMapSetSuccessfully is False :
            # get building name and level number input from user (keypad code)
            if self.isEndLocation: #set building at destination
                self.speaker.wait()
                print "Is destination in the same building as the starting location?. If \"YES\", press start. If \"NO\", press back."
                self.speaker.speak ("Is destination in the same building as the starting location?. If \"YES\", press start. If \"NO\", press back.")

                if self.keypad.get_binary_response():
                    while True:
                        print self.BUILDING_PROMPT
                        self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

                        print "Building is " + self.buildingName + ". Press start to confirm. Back to cancel"
                        self.speaker.wait()
                        self.speaker.speak("Building is " + self.buildingName + ". Press start to confirm. Back to cancel")

                        if not self.keypad.get_binary_response():
                            break
            else: #set building at origin
                while True:
                    print self.BUILDING_PROMPT
                    self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

                    print "Building is " + self.buildingName + ". Press start to confirm. Back to cancel"
                    self.speaker.wait()
                    self.speaker.speak("Building is " + self.buildingName + ". Press start to confirm. Back to cancel")

                    if not self.keypad.get_binary_response():
                        break

            while True: #set level
                self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)
                print "Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel"
                self.speaker.wait()
                self.speaker.speak("Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel")

                if not self.keypad.get_binary_response():
                    break

            if self.building.setMap(self.buildingName, self.levelNumber):
                break

            # if an invalid building or level is given
            print self.INVALID_BUILDING_LEVEL
            self.speaker.wait()
            self.speaker.speak(self.INVALID_BUILDING_LEVEL)


    def getSearchQueryFromUser(self) :
        disable = False
        while not self.possibleNodes :
            if disable:
                node = self.keypad.poll_for_str()# raw_input("Enter location point, or \'all\' for all nodes: ")
                disable = False
            else:
                node = self.keypad.get_input_str(self.SEARCH_PROMPT)# raw_input("Enter location point, or \'all\' for all nodes: ")
            userInputNode = node.split()

            if node == "all" :
                self.possibleNodes = []
                for i in xrange(self.building.numElements) :
                    self.possibleNodes.append(i)
            elif node == "help":
                print self.SEARCH_HELP1, self.SEARCH_HELP2, self.SEARCH_HELP3
                self.speaker.speak(str(self.SEARCH_HELP1 + self.SEARCH_HELP2 + self.SEARCH_HELP3))
                disable = True
            else :
                temp_node = node.strip()
                if temp_node[0] == '.':
                    try:
                        node_num = int(temp_node[1:len(temp_node)])
                        if 0 < node_num <= self.building.numElements:
                            self.possibleNodes.append(node_num - 1)
                        else:
                            print self.INVALID_NUMBER
                            self.speaker.speak(self.INVALID_NUMBER)
                    except:
                        print self.INVALID_NUMBER
                        self.speaker.speak(self.INVALID_NUMBER)

                else:
                    for i in xrange(self.building.numElements) :
                        match = False
                        for j in xrange(len(userInputNode)) :
                            match = userInputNode[j].lower() in self.building.getLocationName(i).lower()
                            if match is False :
                                break
                        if match is True :
                            self.possibleNodes.append(i)
                    if len(self.possibleNodes) > 0:
                        print "All search results will be listed."
                    else:
                        print "No results found"
                        self.speaker.speak("No results found")
                        self.speaker.wait()

    def getExactLocationFromUser(self) :
        # continueLoop = True
        while True: #continueLoop:
            if len(self.possibleNodes) > 1 : #all is entered, or search query
                isNumberChosen = False

                self.keypad.chr_queue.clear()
                for i in xrange(len(self.possibleNodes)) :
                    print str(i) + ": " + str(self.building.getLocationName(self.possibleNodes[i]))
                    self.keypad.chr_queue.append("for " + str(self.building.getLocationName(self.possibleNodes[i])) + ", press"  + str(i), time.time())
                    self.voiceSema.release()

                while isNumberChosen is False:
                    self.locationPoint = int(self.keypad.poll_for_ext_num(True))
                    if self.locationPoint < len(self.possibleNodes):
                        isNumberChosen = True
                        break
                    print self.INVALID_NUMBER
                    self.speaker.speak(self.INVALID_NUMBER)
                self.locationPoint = self.possibleNodes[self.locationPoint]
            else :
                self.locationPoint = self.possibleNodes[0]
            print "Location selected is " + self.building.getLocationName(self.locationPoint) + ". Press start to confirm. Back to cancel"#self.SELECTION_LOCATION
            if self.isEndLocation:
                self.speaker.speak ("Destination selected is " + self.building.getLocationName(self.locationPoint) + ". Press start to confirm. Back to cancel")
            else:
                self.speaker.speak ("Start location selected is " + self.building.getLocationName(self.locationPoint) + ". Press start to confirm. Back to cancel")

            if not self.keypad.get_binary_response():
                self.locationPoint += 1
                break
            self.possibleNodes = []
            self.getSearchQueryFromUser()