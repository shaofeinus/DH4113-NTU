from dijkstra import pathFinder

myPathFinder = pathFinder()
myPathFinder.setMap(input("MapNo: "))
while True:
    print myPathFinder.getPath(input("Start: "), input("End: "))
    myPathFinder.setMap(input("MapNo: "))
