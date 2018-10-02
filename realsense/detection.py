import numpy as np
from .config import *
from .objects import *


class ApproximationFunction(Path):
    def __init__(self):
        # 青ゾーン下
        data = np.loadtxt(self.blue_under, delimiter=',')
        self.blue_under_res = np.polyfit(data[:, 1], data[:, 0], 5)

        # 青ゾーン中央
        data = np.loadtxt(self.blue_middle, delimiter=',')
        self.blue_middle_res = np.polyfit(data[:, 1], data[:, 0], 4)

        # 青ゾーン上
        data = np.loadtxt(self.blue_up, delimiter=',')
        self.blue_up_res = np.polyfit(data[:, 1], data[:, 0], 3)

        # フロント下
        data = np.loadtxt(self.under_front, delimiter=',')
        self.under_front_res = np.polyfit(data[:, 1], data[:, 0], 3)

        # フロント中央
        data = np.loadtxt(self.middle_front, delimiter=',')
        self.middle_front_res = np.polyfit(data[:, 1], data[:, 0], 3)

        # フロント上
        data = np.loadtxt(self.up_front, delimiter=',')
        self.up_front_res = np.polyfit(data[:, 1], data[:, 0], 3)

    def make_distance_under_blue_zone_by_center(self, x):
        return np.poly1d(self.blue_under_res)(x)

    def make_distance_middle_blue_zone_by_center(self, x):
        return np.poly1d(self.blue_middle_res)(x)

    def make_distance_up_blue_zone_by_center(self, x):
        return np.poly1d(self.blue_up_res)(x)

    def make_distance_under_front_by_center(self, x):
        return np.poly1d(self.under_front_res)(x)

    def make_distance_middle_front_by_center(self, x):
        return np.poly1d(self.middle_front_res)(x)

    def make_distance_up_front_by_center(self, x):
        return np.poly1d(self.up_front_res)(x)


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

    def __side_partition_validate_under(self, table: Table):
        if self.side:
            return ((not self.zone) and table.center[0] < self.blue_partition_1) or \
                   (self.zone and table.center[0] < self.red_partition_1)

    def __side_partition_validate_middle(self, table: Table):
        if self.side:
            return (not self.zone and (self.blue_partition_1 <= table.center[0] <= self.blue_partition_2)) or \
                   (self.zone and (self.red_partition_1 <= table.center[0] <= self.red_partition_2))

    def __side_partition_validate_up(self, table: Table):
        if self.side:
            return (not self.zone and (self.blue_partition_2 < table.center[0])) or \
                   (self.zone and (self.red_partition_1 < table.center[0]))

    def update(self, under: Table, middle: Table, up: Table):
        if not self.side:
            return self.update_for_front(under, middle, up)
        # mode=0: 深度
        # mode=1: 中心座標
        rtype = 0  # 戻り値に使うやつ 成功したかどうかを入れる
        if self.__side_partition_validate_under(under):  # 一番下のテーブル
            self.under = under
            self.under.type = 'under'
            if self.mode:  # 中心座標
                if self.use_moving_average:
                    self.under_center.append(self.under.center)
                    if len(self.under_center) > self.count:
                        self.under_center.pop(0)
                        center = np.mean(self.under_center, axis=0)
                        self.under.dist = self.__round(self.make_distance_under(center))
                    else:
                        self.nud += 1
                        self.under.dist = -1
                else:
                    self.under.dist = self.__round(self.make_distance_under(self.under.center))
            else:  # 深度
                self.under_dist.append(self.__round(self.under.dist))
                if len(self.under_dist) > self.count:
                    self.under_dist.pop(0)
                    self.under.dist = self.__round(np.mean(self.under_dist))
                    # self.under.dist = self.make_distance_under(self.__round(self.under_dist.mean()))
                else:
                    self.nud += 1
                    self.under.dist = -1
        else:
            rtype += 0x01

        if self.__side_partition_validate_middle(middle):  # 中央のテーブル
            self.middle = middle
            self.middle.type = 'middle'
            if self.mode:  # 中心座標
                if self.use_moving_average:
                    self.middle_center.append(self.middle.center)
                    if len(self.middle_center) > self.count:
                        self.middle_center.pop(0)
                        center = np.mean(self.middle_center, axis=0)
                        self.middle.dist = self.__round(self.make_distance_middle(center))
                    else:
                        self.nmd += 1
                        self.middle.dist = -1
                else:
                    self.middle.dist = self.__round(self.make_distance_middle(self.middle.center))

            else:  # 深度
                self.middle_dist.append(self.__round(self.middle.dist))
                if len(self.middle_dist) > self.count:
                    self.middle_dist.pop(0)
                    self.middle.dist = self.__round(np.mean(self.middle_dist))
                    # self.middle.dist = self.make_distance_middle(self.__round(self.middle_dist.mean()))
                else:
                    self.nmd += 1
                    self.middle.dist = -1
        else:
            rtype += 0x02

        if self.__side_partition_validate_up(up):  # 一番上のテーブル
            self.up = up
            self.up.type = 'up'
            if self.mode:  # 中心座標
                if self.use_moving_average:
                    self.up_center.append(self.up.center)
                    if len(self.up_center) > self.count:
                        self.up_center.pop(0)
                        center = np.mean(self.up_center, axis=0)
                        self.up.dist = self.__round(self.make_distance_up(center))
                    else:
                        self.nup += 1
                        self.up.dist = -1
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
                    self.up.dist = -1
        else:
            rtype += 0x04
        return rtype

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

    def get_remaining_times(self):
        return self.count - self.nud, self.count - self.nmd, self.count - self.nup

    def is_available(self):
        return (self.count - self.nud + self.count - self.nmd + self.count - self.nup) == 0

    def make_distance_under(self, distanceOrCenter):
        if self.mode:
            y = distanceOrCenter[1]
            if self.zone:
                return 0
            else:
                return self.make_distance_under_blue_zone_by_center(y)
        else:
            return 0

    def make_distance_middle(self, distanceOrCenter):
        if self.mode:
            y = distanceOrCenter[1]
            if self.zone:  # 赤ゾーン
                return 0
            else:  # 青ゾーン
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
