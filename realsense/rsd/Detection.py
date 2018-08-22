import socket
import struct
import os
import json
import numpy as np

try:
    from .Config import Config
except:
    from Config import Config


class Table(Config):
    def __init__(self, center, radius, dist):
        self.center = center
        self.radius = radius
        self.dist = round(dist, 3)
        self.type = ''


class Tables(Config):
    def __init__(self):
        self.under_dist = np.array([])
        self.middle_dist = np.array([])
        self.up_dist = np.array([])

    def update(self, under: Table, middle: Table, up: Table):
        if under.center[0] < self.partition_1:
            self.under = under
            self.under.type = 'under'
            self.under_dist = np.append(self.under_dist, self.under.dist)
            if self.under_dist.size > self.count:
                self.under_dist = np.delete(self.under_dist, 0)
                self.under.dist = round(self.under_dist.mean(), 3)
            else:
                self.nud += 1
                self.under.dist = 0
        else:
            raise Exception('Under table was found, but the coordinates are inappropriate.')
        if self.partition_1 <= middle.center[0] <= self.partition_2:
            self.middle = middle
            self.middle.type = 'middle'
            self.middle_dist = np.append(self.middle_dist, self.middle.dist)
            if self.middle_dist.size > self.count:
                self.middle_dist = np.delete(self.middle_dist, 0)
                self.middle.dist = round(self.middle_dist.mean(), 3)
            else:
                self.nmd += 1
                self.middle.dist = 0
        else:
            raise Exception('Middle table was found, but the coordinates are inappropriate.')
        if self.partition_2 < up.center[0]:
            self.up = up
            self.up.type = 'up'
            self.up_dist = np.append(self.up_dist, self.up.dist)
            if self.up_dist.size > self.count:
                self.up_dist = np.delete(self.up_dist, 0)
                self.up.dist = round(self.up_dist.mean(), 3)
            else:
                self.nup += 1
                self.under.dist = 0
        else:
            raise Exception('Up table was found, but the coordinates are inappropriate.')

    def get_remaining_times(self):
        return self.count-self.nud, self.count-self.nmd, self.count-self.nup

    def is_available(self):
        return (self.count - self.nud + self.count - self.nmd + self.count - self.nup) == 0


class Utils:
    def __init__(self, zone):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.zone = zone
        self.nothing = lambda x: x
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
        return a.center[0]

    def return_radius(self, a):
        return a.radius

    def radius_filter(self, a):
        return 200 > a.radius > 1

    def distance_filter(self, a):
        return 0.5 < a.dist < 6.5

    def make_coordinate(self, tables):
        _x1 = int(tables.under.dist * 1000)
        _x2 = int(tables.middle.dist * 1000)
        _x3 = int(tables.up.dist * 1000)
        return _x1, _x2, _x3

    def send_coordinate(self, dists):
        if self.is_tcp_available:
            packet = dists
            if self.zone == 'red':
                packet.append(1)
            else:
                packet.append(0)
            b = struct.pack("iii?", *packet)
            self.cl.send(b)

    def save_param(self, h, s, v, th, kn):
        self.settings['h'] = h
        self.settings['s'] = s
        self.settings['v'] = v
        self.settings['th'] = th
        self.settings['k'] = kn
        f = open(self.path + '/../settings.json', 'w')
        json.dump(self.settings, f)
