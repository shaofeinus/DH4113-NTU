import search

##startPoint = search.locationSetting(False)


##print "Start building is: " + str(startPoint.getBuildingName())
##print "Start level number is: " + str(startPoint.getLevelNumber())
##print "Start point is: " + str(startPoint.getLocationPointIndex())

##endPoint = search.locationSetting(True)
##print "End building is: " + str(endPoint.getBuildingName())
##print "End level number is: " + str(endPoint.getLevelNumber())
##print "End point is: " + str(endPoint.getLocationPointIndex())

startLocation = search.locationSetting(False)
startLocation.run()

endLocation = search.locationSetting(True)
endLocation.setBuildingAndLevel(startLocation.buildingName, startLocation.levelNumber)
endLocation.run()

print startLocation.buildingName, startLocation.levelNumber, startLocation.getLocationPointIndex()
print endLocation.buildingName, endLocation.levelNumber, endLocation.getLocationPointIndex()