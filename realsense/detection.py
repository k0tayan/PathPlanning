import numpy as np
from .config import *
from .objects import *


class ApproximationFunction(Path):
    def __init__(self):
        # フロント下
        data = np.loadtxt(self.under_front, delimiter=',')
        self.under_front_res = np.polyfit(data[:, 1], data[:, 0], 3)

        # フロント中央
        data = np.loadtxt(self.middle_front, delimiter=',')
        self.middle_front_res = np.polyfit(data[:, 1], data[:, 0], 3)

        # フロント上
        data = np.loadtxt(self.up_front, delimiter=',')
        self.up_front_res = np.polyfit(data[:, 1], data[:, 0], 3)

    def make_distance_under_front_by_center(self, x):
        return np.poly1d(self.under_front_res)(x)

    def make_distance_middle_front_by_center(self, x):
        return np.poly1d(self.middle_front_res)(x)

    def make_distance_up_front_by_center(self, x):
        return np.poly1d(self.up_front_res)(x)


class Tables(Config, ApproximationFunction):
    def __init__(self):
        super().__init__()

    def __round(self, n):
        return round(n, 3)

    def update(self, under: Table, middle: Table, up: Table):
        return self.update_for_front(under, middle, up)

    def update_for_front(self, under: Table, middle: Table, up: Table):
        self.under = under
        self.under.type = 'under'
        self.under.dist = self.__round(self.make_distance_under_front_by_center(under.x))

        self.middle = middle
        self.middle.type = 'middle'
        self.middle.dist = self.__round(self.make_distance_middle_front_by_center(middle.x))

        self.up = up
        self.up.type = 'up'
        self.up.dist = self.__round(self.make_distance_up_front_by_center(up.x))

        return 0
