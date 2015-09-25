import FindMyWay.Pi.deadReckoning.mapGetter

__author__ = 'Shao Fei'

test = FindMyWay.Pi.deadReckoning.mapGetter.MapGetter("http://showmyway.comp.nus.edu.sg/getMapInfo.php", "COM1", 2)
test.getMap()
test.getWifi()
test.getNorth()



