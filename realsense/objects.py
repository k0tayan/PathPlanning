from .config import *
class T:
    def __init__(self):
        self.under = 0
        self.middle = 0
        self.up = 0

    def __fix(self, coord):
        if coord < 1250:
            return 1250
        elif coord > 3750:
            return 3750
        else:
            return coord

    def fix(self):
        self.under = self.__fix(self.under)
        self.middle = self.__fix(self.middle)
        self.up = self.__fix(self.up)


class Table(Config):
    def __init__(self, center, radius, dist, center_float):
        self.center = center
        self.radius = radius
        self.dist = round(dist, 3)
        self.type = ''
        x = round(center_float[0], 1)
        y = round(center_float[1], 1)
        self.center_float = (x, y)
        self.x = center[0]
        self.y = center[1]
        self.standing = None

    def is_table(self):
        # 半径でフィルタ
        return self.radius_filter_front[0] < self.radius < self.radius_filter_front[1]

    def __lt__(self, other):
        return self.radius < other.radius

class Parameter:
    def __init__(self):
        self.h = None
        self.s = None
        self.v = None
        self.lv = None
        self.th = None
        self.kn = None
        self.horizon = None
        self.vertical = None
        self.remove_side = None
        self.zone = None
