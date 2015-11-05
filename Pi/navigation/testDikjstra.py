from dijkstra import pathFinder

pathFinder = pathFinder()
pathFinder.setMap(1, 2)
print pathFinder.getPath(0, 14)

pathFinder.setMap(2, 3)
print pathFinder.getPath(0, 9)
