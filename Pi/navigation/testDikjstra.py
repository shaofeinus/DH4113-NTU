from dijkstra import pathFinder

pathFinder = pathFinder()
pathFinder.setMap(1, 2)
print pathFinder.getPath(0, 16)

pathFinder.setMap(2, 3)
print pathFinder.getPath(0, 16)
