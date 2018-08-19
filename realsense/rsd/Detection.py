import socket
import struct
import os
import json
import cv2

class Table:
    def __init__(self, center, radius, dist):
        self.center = center
        self.radius = radius
        self.dist = round(dist, 3)
        self.type = ''


class Utils:
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        try:
            f = open(self.path + '/../settings.json', 'r')
            self.settings = json.load(f)
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10}
        try:
            self.cl = socket.socket()
            self.cl.connect(('localhost', 4000))
            self.is_tcp_available = True
        except:
            print('Cant connect to path_planning')
            self.is_tcp_available = False

    def return_center(self, a):
        return a.center

    def return_radius(self, a):
        return a.radius

    def radius_filter(self, a):
        return 200 > a.radius > 1

    def distance_filter(self, a):
        return 0.5 < a.dist < 6.5

    def nothing(self, x):
        pass

    def make_coordinate(self, tables):
        _x1, _x2, _x3 = None, None, None
        for table in tables:
            if table.type == 'under':
                _x1 = int(table.dist * 1000)
            if table.type == 'middle':
                _x2 = int(table.dist * 1000)
            if table.type == 'up':
                _x3 = int(table.dist * 1000)
        # _x1 = 2500
        # _x2 = 2500
        # _x3 = 2500
        print(_x1, _x2, _x3)
        if _x1 is None or _x2 is None or _x3 is None:
            return False
        else:
            return _x1, _x2, _x3

    def send_coordinate(self, under, middle, up):
        if self.is_tcp_available:
            b = struct.pack("iii?", under, middle, up, 0)
            self.cl.send(b)

    def save_file(self, dic):
        f2 = open(self.path + '/../settings.json', 'w')
        json.dump(dic, f2)


