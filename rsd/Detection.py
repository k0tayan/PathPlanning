import os
import json
import numpy as np

try:
    from .Config import Config, Path
except:
    from Config import Config, Path


class ApproximationFunction(Path):
    def __init__(self):
        # 青ゾーン中央
        data = np.loadtxt(self.blue_middle, delimiter=',')
        self.blue_middle_res = np.polyfit(data[:, 1], data[:, 0], 4)

        # 青ゾーン上
        data = np.loadtxt(self.blue_up, delimiter=',')
        self.blue_up_res = np.polyfit(data[:, 1], data[:, 0], 3)

    def make_distance_middle_blue_zone_by_center(self, x):
        return np.poly1d(self.blue_middle_res)(x)

    def make_distance_up_blue_zone_by_center(self, x):
        return np.poly1d(self.blue_up_res)(x)


class Table(Config):
    def __init__(self, center, radius, dist):
        self.center = center
        self.radius = radius
        self.dist = round(dist, 3)
        self.type = ''


class Tables(Config, ApproximationFunction):
    def __init__(self):
        super().__init__()
        # 深度用
        self.under_dist = []
        self.middle_dist = []
        self.up_dist = []

        # 中心座標用
        self.under_center = []
        self.middle_center = []
        self.up_center = []

    def __round(self, n):
        return round(n, 3)

    def update(self, under: Table, middle: Table, up: Table):
        # mode=0: 深度
        # mode=1: 中心座標
        rtype = 0 # 戻り値に使うやつ　成功したかどうかを入れる
        if under.center[0] < self.partition_1: # 一番下のテーブル
            self.under = under
            self.under.type = 'under'
            if self.mode: # 中心座標
                if self.use_moving_average:
                    self.under_center.append(self.under.center)
                    if len(self.under_center) > self.count:
                        self.under_center.pop(0)
                        center = np.mean(self.under_center, axis=0)
                        self.under.dist = self.__round(self.make_distance_under(center))
                    else:
                        self.nud += 1
                        self.under.dist = 0
                else:
                    self.under.dist = self.__round(self.make_distance_under(self.under.center))
            else: # 深度
                self.under_dist.append(self.__round(self.under.dist))
                if len(self.under_dist) > self.count:
                    self.under_dist.pop(0)
                    self.under.dist = self.__round(np.mean(self.under_dist))
                    # self.under.dist = self.make_distance_under(self.__round(self.under_dist.mean()))
                else:
                    self.nud += 1
                    self.under.dist = 0
        else:
            rtype += 0x01

        if self.partition_1 <= middle.center[0] <= self.partition_2: # 真ん中のテーブル
            self.middle = middle
            self.middle.type = 'middle'
            if self.mode: # 中心座標
                if self.use_moving_average:
                    self.middle_center.append(self.middle.center)
                    if len(self.middle_center) > self.count:
                        self.middle_center.pop(0)
                        center = np.mean(self.middle_center, axis=0)
                        self.middle.dist = self.__round(self.make_distance_middle(center))
                    else:
                        self.nmd += 1
                        self.middle.dist = 0
                else:
                    self.middle.dist = self.__round(self.make_distance_middle(self.middle.center))

            else: # 深度
                self.middle_dist.append(self.__round(self.middle.dist))
                if len(self.middle_dist) > self.count:
                    self.middle_dist.pop(0)
                    self.middle.dist = self.__round(np.mean(self.middle_dist))
                    # self.middle.dist = self.make_distance_middle(self.__round(self.middle_dist.mean()))
                else:
                    self.nmd += 1
                    self.middle.dist = 0
        else:
            rtype += 0x02

        if self.partition_2 < up.center[0]: # 一番上のテーブル
            self.up = up
            self.up.type = 'up'
            if self.mode: # 中心座標
                if self.use_moving_average:
                    self.up_center.append(self.up.center)
                    if len(self.up_center) > self.count:
                        self.up_center.pop(0)
                        center = np.mean(self.up_center, axis=0)
                        self.up.dist = self.__round(self.make_distance_up(center))
                    else:
                        self.nup += 1
                        self.up.dist = 0
                else:
                    self.up.dist = self.__round(self.make_distance_up(self.up.center))
            else:
                self.up_dist.append(self.__round(self.up.dist))
                if len(self.up_dist) > self.count:
                    self.up_dist.pop(0)
                    self.up.dist = self.__round(np.mean(self.up_dist))
                    # self.up.dist = self.make_distance_up(self.__round(self.up_dist.mean()))
                else:
                    self.nup += 1
                    self.up.dist = 0
        else:
            rtype += 0x04
        return rtype

    def get_remaining_times(self):
        return self.count-self.nud, self.count-self.nmd, self.count-self.nup

    def is_available(self):
        return (self.count - self.nud + self.count - self.nmd + self.count - self.nup) == 0

    def make_distance_under(self, distanceOrCenter):
        if self.mode:
            return 0
        else:
            return 0

    def make_distance_middle(self, distanceOrCenter):
        if self.mode:
            y = distanceOrCenter[1]
            if self.zone: # 赤ゾーン
                return 0
            else: #青ゾーン
                return self.make_distance_middle_blue_zone_by_center(y)
        else:
            return 0

    def make_distance_up(self, distanceOrCenter):
        if self.mode:
            y = distanceOrCenter[1]
            if self.zone:
                return 0
            else:
                return self.make_distance_up_blue_zone_by_center(y)
        else:
            return 0



class Utils(Config):
    def __init__(self, zone):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.zone = zone
        self.nothing = lambda x: x
        try:
            f = open(self.path + self.setting_path, 'r')
            self.settings = json.load(f)
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10}

    def return_center(self, a):
        return a.center[0]

    def return_radius(self, a):
        return a.radius

    def radius_filter(self, a):
        return 100 > a.radius > 20

    def distance_filter(self, a):
        return 2 < a.dist < 6.5

    def make_distance_send(self, tables):
        _x1 = int(tables.under.dist * 1000)
        _x2 = int(tables.middle.dist * 1000)
        _x3 = int(tables.up.dist * 1000)
        return _x1, _x2, _x3

    def save_param(self, h, s, v, lv, th, kn):
        self.settings['h'] = h
        self.settings['s'] = s
        self.settings['v'] = v
        self.settings['lv'] = lv
        self.settings['th'] = th
        self.settings['k'] = kn
        f = open(self.path + self.setting_path, 'w')
        json.dump(self.settings, f)
