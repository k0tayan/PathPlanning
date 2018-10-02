from .config import *
class T:
    def __init__(self):
        self.under = 0
        self.middle = 0
        self.up = 0

    def validate(self):
        if self.under < 1250:
            self.under = 1250
        if self.middle < 1250:
            self.middle = 1250
        if self.up < 1250:
            self.up = 1250
        if self.under > 3750:
            self.under = 3750
        if self.middle > 3750:
            self.middle = 3750
        if self.up > 3750:
            self.up = 3750


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