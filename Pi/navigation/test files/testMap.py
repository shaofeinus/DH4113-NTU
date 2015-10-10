import os
import json
import pprint


fileLocation = os.getcwd()
print fileLocation
##fileLocation += "com1L2"
json_data = open("com1L2.json").read()
data = json.loads(json_data)
print(json_data)
