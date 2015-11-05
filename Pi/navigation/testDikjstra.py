from dijkstra import pathFinder

pathFinder = pathFinder()
pathFinder.setMap(2, 2)
print pathFinder.getPath(0, 15)

pathFinder.setMap(2, 3)
print pathFinder.getPath(0, 15)
