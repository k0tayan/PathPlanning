import os
import json
import numpy as np
import cv2

try:
    from .Config import Config, Path, Field
except:
    from Config import Config, Path, Field


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
        rtype = 0  # 戻り値に使うやつ　成功したかどうかを入れる
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


class Utils(Config, Field):
    def __init__(self, zone):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.zone = zone
        self.nothing = lambda x: x
        try:
            f = open(self.path + self.setting_path, 'r')
            self.settings = json.load(f)
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10}

    def return_center_x(self, a):
        return a.center[0]

    def return_center_y(self, a):
        return a.center[1]

    def return_radius(self, a):
        return a.radius

    def radius_filter(self, a):
        if self.side:
            return self.radius_filter_side[0] > a.radius > self.radius_filter_side[1]
        else:
            return self.radius_filter_front[0] > a.radius > self.radius_filter_front[1]

    def distance_filter(self, a):
        return 2 < a.dist < 6.5

    def put_text(self, img: object, text: object, pos: object, color: object, size: object = 1, weight: object = 1) -> object:
        return cv2.putText(img, text, tuple(pos), cv2.FONT_HERSHEY_TRIPLEX, size, color, weight, cv2.LINE_AA)

    def rectangle(self, image, center, radius, weight=2):
        if self.zone:
            color = (38, 81, 255)
        else:
            color = (255, 167, 38)
        color_image_copy = cv2.rectangle(image,
                                         (lambda l: (
                                             l[0] - radius, l[1] - radius))(
                                             list(center)),
                                         (lambda l: (
                                             l[0] + radius, l[1] + radius))(
                                             list(center)),
                                         color, weight)
        return color_image_copy

    def put_type_name(self, image, table):
        return self.put_text(image,
                             table.type,
                             (lambda l: (l[0] - 10, l[1] - 50))(list(table.center)),
                             (0, 0, 0), size=1, weight=2)

    def put_dist(self, image, table):
        return self.put_text(image, str(table.dist),
                (lambda l: (l[0], l[1] + 100))(list(table.center)), (0, 0, 0), size=1, weight=2)

    def put_info(self, image, table: Table):
        c_image = self.rectangle(image, table.center,
                       table.radius)
        c_image = self.put_type_name(c_image, table)
        c_image = self.put_dist(c_image, table)
        return c_image

    def make_distance_send(self, tables):
        t = T()
        if self.zone:
            t.under = int(tables.under.dist * 1000)
            t.middle = int(tables.middle.dist * 1000)
            t.up = int(tables.up.dist * 1000)
        else:
            t.under = self.FIELD_WIDTH - (int(tables.under.dist * 1000) + self.TABLE_WIDTH / 2)
            t.middle = self.FIELD_WIDTH - (int(tables.middle.dist * 1000) + self.TABLE_WIDTH / 2)
            t.up = self.FIELD_WIDTH - (int(tables.up.dist * 1000) + self.TABLE_WIDTH / 2)

        if not self.side:
            t.under = self.FIELD_WIDTH - (int(tables.under.dist * 1000) + self.TABLE_WIDTH / 2)
            t.middle = self.FIELD_WIDTH - (int(tables.middle.dist * 1000) + self.TABLE_WIDTH / 2)
            t.up = self.FIELD_WIDTH - (int(tables.up.dist * 1000) + self.TABLE_WIDTH / 2)

        t.validate()
        return t

    def save_param(self, h, s, v, lv, th, kn):
        self.settings['h'] = h
        self.settings['s'] = s
        self.settings['v'] = v
        self.settings['lv'] = lv
        self.settings['th'] = th
        self.settings['k'] = kn
        f = open(self.path + self.setting_path, 'w')
        json.dump(self.settings, f)
