import json

import requests

__author__ = 'Shao Fei'


# 'request' is external library, need to install
# sudo apt-get python3-requests

class MapGetter:
    def __init__(self, url, buildingname, level):
        params = {'Building': buildingname, 'Level': level}
        resp = requests.get(url=url, params=params)

        # Map data - data is of Dict type
        self.data = json.loads(resp.text)

    def getNorth(self):
        if self.data is not None:
            degree = self.data['info']['northAt']
            print("North at: ", degree)
            return degree
        else:
            return None

    def getMap(self):
        if self.data is not None:
            map = self.data['map']
            for node in map:
                print("ID: ", node['nodeId'])
                print("Name: ", node['nodeName'])
                print("x: ", node['x'])
                print("y: ", node['y'])
                print("linkTo: ", node['linkTo'])
            return map
        else:
            return None

    def getWifi(self):
        if self.data is not None:
            wifi = self.data['wifi']
            for node in wifi:
                print("ID: ", node['nodeId'])
                print("Name: ", node['nodeName'])
                print("x: ", node['x'])
                print("y: ", node['y'])
                print("MAC: ", node['macAddr'])
            return wifi
        else:
            return None
