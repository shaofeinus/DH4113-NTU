import jsonParsingLite
import keypad_polling
import threading
import time
from collections import deque
from voiceCommands import speak

# TODO: change all print outputs into voice commands

# API:
# getBuildingName()
# getLevelNumber()
# getLocationPointIndex()

# escape_flag = True
#
# class escape_thread(threading.Thread):
#     def __init__(self, threadID, threadName):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.threadName = threadName
#         self.numElements = 0
#         self.num = 0
#         self.exit_thread = False
#
#     def set_num_elements(self, numElements):
#         self.numElements = numElements
#
#     def get_num_elements(self):
#         return self.numElements
#
#     def get_num(self):
#         return self.num
#
#     def set_num(self, num):
#         self.num = num
#
#     def kill_thread(self):
#         self.exit_thread = True
#
#     def run(self):
#         global escape_flag
#
#         self.keypad = keypad_polling.keypad()
#         self.keypad.toggle_sound()
#
#         while True:
#             if self.exit_thread:
#                 self.keypad.kill_voice_thread()
#
#                 break
#             if escape_flag:
#                 time.sleep(0)
#             else:
#                 response = self.keypad.get_binary_response()
#                 escape_flag = not response
#                 # self.num = self.keypad.poll_for_ext_num()
#                 # print "IS " + str(self.num) + " < " + str(self.numElements)
#                 # if 0 < self.num < self.numElements:
#                 #     escape_flag = True
#
#
# esc_thread = escape_thread(1, "esc_thread")
# esc_thread.start()

class locationSetting(object) :
    def __init__(self, isEndLocation, keypad, voiceSema) :
        self.buildingName = None
        self.levelNumber = None
        self.locationPoint = None
        self.possibleNodes = []
        self.building = jsonParsingLite.mapParser()
        self.keypad = keypad
        self.isEndLocation = isEndLocation
        self.voiceSema = voiceSema

        self.BUILDING_PROMPT = "Enter building name or number: "
        self.LEVEL_PROMPT = "Enter level number: "
        self.INVALID_BUILDING_LEVEL = "Sorry, the building or level number specified is invalid!"
        self.SEARCH_PROMPT = "Enter search query for location. For help, enter: \"help\""
        self.SEARCH_HELP = "To retrieve all nodes, enter ,\"all\". To select a node ID, enter \".\", followed by the node ID"
        self.INVALID_NUMBER = "Please enter a valid number"
        self.INVALID_ID = "Please enter a valid ID"
        self.FINAL_CONFIRMATION = "To confirm, press start. To restart, press back"
        #self.run()

    def run(self) :
        self.getBuildingFromUser()
        self.getSearchQueryFromUser()
        self.getExactLocationFromUser()
        self.confirmLocationWithUser()

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
        

    def getBuildingFromUser(self) :
        # get building name and level number input from user (keypad code)
        continueLoop = True
        while continueLoop:
            if self.isEndLocation:
                print ("Is destination in the same building as the starting location? If \"YES\", press start. If \"NO\", press back.")
                speak ("Is destination in the same building as the starting location? If \"YES\", press start. If \"NO\", press back.")

                if self.keypad.get_binary_response():
                    self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")
            else:
                self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

            if self.isEndLocation:
                print ("Is destination on the same level as the starting location? If \"YES\", press start. If \"NO\", press back.")
                speak ("Is destination on the same level as the starting location? If \"YES\", press start. If \"NO\", press back.")

                if self.keypad.get_binary_response():
                    self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)# raw_input("Enter level number: ")
            else:
                self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)# raw_input("Enter level number: ")

            print "Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". To confirm, press start. To cancel, press back"
            speak("Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". To confirm, press start. To cancel, press back")

            continueLoop = self.keypad.get_binary_response()

        isMapSetSuccessfully = self.building.setMap(self.buildingName, self.levelNumber)
        # if an invalid building or level is given
        while isMapSetSuccessfully is False :
            # get building name and level number input from user (keypad code)
            print self.INVALID_BUILDING_LEVEL
            speak(self.INVALID_BUILDING_LEVEL)
            while continueLoop:
                if self.isEndLocation:
                    print ("Is destination in the same building as the starting location? If \"YES\", press start. If \"NO\", press back.")
                    speak ("Is destination in the same building as the starting location? If \"YES\", press start. If \"NO\", press back.")

                    if self.keypad.get_binary_response():
                        self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")
                else:
                    self.buildingName = self.keypad.get_input_str(self.BUILDING_PROMPT)# raw_input("Enter building name or number: ")

                if self.isEndLocation:
                    print ("Is destination on the same level as the starting location? If \"YES\", press start. If \"NO\", press back.")
                    speak ("Is destination on the same level as the starting location? If \"YES\", press start. If \"NO\", press back.")

                    if self.keypad.get_binary_response():
                        self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)# raw_input("Enter level number: ")
                else:
                    self.levelNumber = self.keypad.get_input_ext_num(self.LEVEL_PROMPT)# raw_input("Enter level number: ")

                print "Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". To confirm, press start. To cancel, press back"
                speak("Building is " + self.buildingName + ", level is " + str(self.levelNumber) + ". To confirm, press start. To cancel, press back")

                continueLoop = self.keypad.get_binary_response()

    def getSearchQueryFromUser(self) :
        while not self.possibleNodes :
            node = self.keypad.get_input_str(self.SEARCH_PROMPT)# raw_input("Enter location point, or \'all\' for all nodes: ")
            userInputNode = node.split()

            if node == "all" :
                self.possibleNodes = []
                for i in xrange(self.building.numElements) :
                    self.possibleNodes.append(i)
                print "All nodes will be listed. When you are ready to make your selection, press start."
                speak("All nodes will be listed. When you are ready to make your selection, press start.")
            elif node == "help":
                print self.SEARCH_HELP
                speak(str(self.SEARCH_HELP))
            else :
                temp_node = node.strip()
                if temp_node[0] == '.':
                    try:
                        node_num = int(temp_node[1:len(temp_node)])
                        if 0 < node_num <= self.building.numElements:
                            self.possibleNodes.append(node_num - 1)
                        else:
                            print self.INVALID_NUMBER
                            speak(self.INVALID_NUMBER)
                    except:
                        print self.INVALID_NUMBER
                        speak(self.INVALID_NUMBER)

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
                        print "All search results will be listed. When you are ready to make your selection, press start."
                        speak("All search results will be listed. When you are ready to make your selection, press start.")
                    else:
                        print "No results found"
                        speak("No results found")


    def getExactLocationFromUser(self) :
        # global esc_thread
        # global escape_flag

        continueLoop = True
        while continueLoop:
            if len(self.possibleNodes) > 1 : #all is entered, or search query
                # esc_thread.set_num_elements(len(self.possibleNodes))
                # esc_thread.set_num(0)
                # escape_flag = False
                isNumberChosen = False

                self.keypad.chr_queue.clear()
                for i in xrange(len(self.possibleNodes)) :
                    print str(i) + ": " + str(self.building.getLocationName(self.possibleNodes[i]))
                    self.keypad.chr_queue.append("for " + str(self.building.getLocationName(self.possibleNodes[i])) + ", press"  + str(i))
                    self.voiceSema.release()
                    # if escape_flag:
                    #     # self.locationPoint = self.keypad.get_input_ext_num()#esc_thread.get_num()
                    #     # if 0 < self.locationPoint < len(self.possibleNodes):
                    #     #     isNumberChosen = True
                    #     # else:
                    #     #     print self.INVALID_NUMBER
                    #     #     speak(self.INVALID_NUMBER)
                    #     break
                while True:
                    num = self.keypad.poll_for_num_cond()
                    print num
                    if num == 9 or num == -1:
                        self.keypad.chr_queue.clear()
                        break

                # get the user to choose the point he wants from the list of suggestions
                while isNumberChosen is False :
                    self.keypad.chr_queue.append("")
                    self.voiceSema.release()
                    while len(self.keypad.chr_queue) > 0:
                        pass
                    self.locationPoint = int(self.keypad.get_input_ext_num("Enter number of correct location: "))# int(raw_input("Enter number of correct location: "))

                    if self.locationPoint < len(self.possibleNodes):
                        isNumberChosen = True
                        break
                    print self.INVALID_NUMBER
                    speak(self.INVALID_NUMBER)
                self.locationPoint = self.possibleNodes[self.locationPoint]

            else :
                self.locationPoint = self.possibleNodes[0]
            print "Location selected is " + self.building.getLocationName(self.locationPoint) + ". To confirm, press start. To cancel, press back"#self.SELECTION_LOCATION
            speak ("Location selected is " + self.building.getLocationName(self.locationPoint) + ". To confirm, press start. To cancel, press back")

            continueLoop = self.keypad.get_binary_response()
            if continueLoop:
                self.possibleNodes = []
                self.getSearchQueryFromUser()

    def confirmLocationWithUser(self) :
        print "You have selected building " + str(self.buildingName) + ", level " + str(self.levelNumber) + ", at \"" + str(self.building.getLocationName(self.locationPoint)) + "\""
        speak("You have selected building " + str(self.buildingName) + ", level " + str(self.levelNumber) + ", at " + str(self.building.getLocationName(self.locationPoint)))

        print self.FINAL_CONFIRMATION
        speak(self.FINAL_CONFIRMATION)

        if self.keypad.get_binary_response():
            self.restart()
            self.run()
        # self.keypad.kill_voice_thread()
        # global esc_thread
        # esc_thread.kill_thread()
        # esc_thread.join(3)
        # print "escape thread successfully stopped", (not esc_thread.isAlive())



