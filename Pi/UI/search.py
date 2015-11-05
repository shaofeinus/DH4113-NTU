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
        self.FINAL_CONFIRMATION = "To confirm, press start. To restart, press back"
        #self.run()

    def run(self) :
        self.getBuildingFromUser()
        self.getSearchQueryFromUser()
        self.getExactLocationFromUser()
        # self.confirmLocationWithUser()

    def setBuildingAndLevel(self, building, level):
        self.buildingName = building
        self.levelNumber = level

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

    def getLocationXCoord(self) :
        return self.building.getLocationXCoord(self.locationPoint)

    def getLocationYCoord(self) :
        return self.building.getLocationYCoord(self.locationPoint)

    def getBuildingFromUser(self) :
        # get building name and level number input from user (keypad code)
        continueLoop = True
        # while continueLoop:
        if self.isEndLocation:
            print ("Is destination in the same building as the starting location? If \"YES\", press start. If \"NO\", press back.")
            self.speaker.speak ("Is destination in the same building as the starting location? If \"YES\", press start. If \"NO\", press back.")

            if self.keypad.get_binary_response():
                while True:
                    print self.BUILDING_PROMPT
                    self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

                    print "Building is " + self.buildingName + ". Press start to confirm. Back to cancel"
                    self.speaker.speak("Building is " + self.buildingName + ". Press start to confirm. Back to cancel")

                    if not self.keypad.get_binary_response():
                        break
        else:
            while True:
                print self.BUILDING_PROMPT
                self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

                print "Building is " + self.buildingName + ". Press start to confirm. Back to cancel"
                self.speaker.speak("Building is " + self.buildingName + ". Press start to confirm. Back to cancel")

                if not self.keypad.get_binary_response():
                    break

        if self.isEndLocation:
            print ("Is destination on the same level as the starting location?. If \"YES\", press start. If \"NO\", press back.")
            self.speaker.speak ("Is destination on the same level as the starting location?. If \"YES\", press start. If \"NO\", press back.")

            if self.keypad.get_binary_response():
                while True:
                    print self.LEVEL_PROMPT
                    self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)
                    print "Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel"
                    self.speaker.speak("Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel")

                    if not self.keypad.get_binary_response():
                        break
        else:
            while True:
                print self.LEVEL_PROMPT
                self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)
                print "Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel"
                self.speaker.speak("Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel")

                if not self.keypad.get_binary_response():
                    break

            # print "Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel"
            # self.speaker.speak("Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel")
            #
            # continueLoop = self.keypad.get_binary_response()

        isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)
        # if an invalid building or level is given
        while isMapSetSuccessfully is False :
            # get building name and level number input from user (keypad code)
            print self.INVALID_BUILDING_LEVEL
            self.speaker.speak(self.INVALID_BUILDING_LEVEL)

            if self.isEndLocation:
                print "Is destination in the same building as the starting location?. If \"YES\", press start. If \"NO\", press back."
                self.speaker.speak ("Is destination in the same building as the starting location?. If \"YES\", press start. If \"NO\", press back.")

                if self.keypad.get_binary_response():
                    while True:
                        print self.BUILDING_PROMPT
                        self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

                        print "Building is " + self.buildingName + ". Press start to confirm. Back to cancel"
                        self.speaker.speak("Building is " + self.buildingName + ". Press start to confirm. Back to cancel")

                        if not self.keypad.get_binary_response():
                            break
            else:
                while True:
                    print self.BUILDING_PROMPT
                    self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

                    print "Building is " + self.buildingName + ". Press start to confirm. Back to cancel"
                    self.speaker.speak("Building is " + self.buildingName + ". Press start to confirm. Back to cancel")

                    if not self.keypad.get_binary_response():
                        break

            if self.isEndLocation:
                print ("Is destination on the same level as the starting location?. If \"YES\", press start. If \"NO\", press back.")
                self.speaker.speak ("Is destination on the same level as the starting location?. If \"YES\", press start. If \"NO\", press back.")

                if self.keypad.get_binary_response():
                    while True:
                        print self.LEVEL_PROMPT
                        self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)
                        print "Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel"
                        self.speaker.speak("Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel")

                        if not self.keypad.get_binary_response():
                            break
            else:
                while True:
                    print self.LEVEL_PROMPT
                    self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)
                    print "Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel"
                    self.speaker.speak("Level number is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel")

                    if not self.keypad.get_binary_response():
                        break

            isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)


                # print "Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel"
                # self.speaker.speak("Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". Press start to confirm. Back to cancel")
                #
                # continueLoop = self.keypad.get_binary_response()

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
                # print "All nodes will be listed. When you are ready to make your selection, press start."
                # self.speaker.speak("All nodes will be listed. When you are ready to make your selection, press start.")
            elif node == "help":
                print self.SEARCH_HELP1, self.SEARCH_HELP2, self.SEARCH_HELP3
                self.speaker.speak(str(self.SEARCH_HELP1 + self.SEARCH_HELP2 + self.SEARCH_HELP3))
                disable = True
                # self.speaker.speak(str(self.SEARCH_HELP2))
                # self.speaker.speak(str(self.SEARCH_HELP3))
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
                        # self.speaker.speak("All search results will be listed.")
                        # self.speaker.wait()
                    else:
                        print "No results found"
                        self.speaker.speak("No results found")
                        self.speaker.wait()

    def getExactLocationFromUser(self) :
        continueLoop = True
        while continueLoop:
            if len(self.possibleNodes) > 1 : #all is entered, or search query
                isNumberChosen = False

                self.keypad.chr_queue.clear()
                for i in xrange(len(self.possibleNodes)) :
                    print str(i) + ": " + str(self.building.getLocationName(self.possibleNodes[i]))
                    self.keypad.chr_queue.append("for " + str(self.building.getLocationName(self.possibleNodes[i])) + ", press"  + str(i), time.time())
                    self.voiceSema.release()
                    # self.speaker.speak("for " + str(self.building.getLocationName(self.possibleNodes[i])) + ", press"  + str(i))

                while isNumberChosen is False:
                    self.locationPoint = int(self.keypad.poll_for_ext_num(True))
                    if self.locationPoint < len(self.possibleNodes):
                        isNumberChosen = True
                        break
                    print self.INVALID_NUMBER
                    self.speaker.speak(self.INVALID_NUMBER)
                self.locationPoint = self.possibleNodes[self.locationPoint]
                # while True:
                #     num = self.keypad.poll_for_num_cond()
                #     if num == 9 or num == -1:
                #         self.keypad.chr_queue.clear()
                #         break

                # get the user to choose the point he wants from the list of suggestions
                # while isNumberChosen is False :
                #     # self.keypad.chr_queue.append("")
                #     # self.voiceSema.release()
                #     while not self.keypad.chr_queue.empty():
                #         pass
                #     self.locationPoint = int(self.keypad.get_input_ext_num("Enter number of correct location: "))# int(raw_input("Enter number of correct location: "))
                #
                #     if self.locationPoint < len(self.possibleNodes):
                #         isNumberChosen = True
                #         break
                #     print self.INVALID_NUMBER
                #     self.speaker.speak(self.INVALID_NUMBER)
                # self.locationPoint = self.possibleNodes[self.locationPoint]

            else :
                self.locationPoint = self.possibleNodes[0]
            print "Location selected is " + self.building.getLocationName(self.locationPoint) + ". Press start to confirm. Back to cancel"#self.SELECTION_LOCATION
            if self.isEndLocation:
                self.speaker.speak ("Destination selected is " + self.building.getLocationName(self.locationPoint) + ". Press start to confirm. Back to cancel")
            else:
                self.speaker.speak ("Start location selected is " + self.building.getLocationName(self.locationPoint) + ". Press start to confirm. Back to cancel")

            continueLoop = self.keypad.get_binary_response()
            if continueLoop:
                self.possibleNodes = []
                self.getSearchQueryFromUser()

    def confirmLocationWithUser(self) :
        print "You have selected building " + str(self.buildingName) + ", level " + str(self.levelNumber) + ", at \"" + str(self.building.getLocationName(self.locationPoint)) + "\""
        self.speaker.speak("You have selected building " + str(self.buildingName) + ", level " + str(self.levelNumber) + ", at " + str(self.building.getLocationName(self.locationPoint)))

        print self.FINAL_CONFIRMATION
        self.speaker.speak(self.FINAL_CONFIRMATION)

        if self.keypad.get_binary_response():
            self.restart()
            self.run()
