import jsonParsing

building = raw_input("Enter building name or number: ")
level = raw_input("Enter level: ")

maps = jsonParsing.mapParser()
maps.setMap(building, level)

for i in range(maps.numElements):
    print maps.getLocationName(i)
