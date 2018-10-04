from .sd.label_image import StandingDetection
from .config import *
from .objects import *
import functools
import threading
import coloredlogs, logging
import cv2
from pool.mypool import MyPool
import random
import string
import numpy as np
import json
import os
from keras.models import load_model

def randstr(n):
    random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
    return random_str

class Utils(Config, Field, Path):
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.nothing = lambda x: x
        self.pool = MyPool(3)
        self.model = load_model(self.keras_green_model)

        data = np.loadtxt(self.field_max_right, delimiter=',')
        self.field_max_right_res = np.polyfit(data[:, 1], data[:, 0], 1)
        try:
            f = open(self.path + self.setting_path, 'r')
            self.settings = json.load(f)
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10, 'rms':9}

    def is_over_field_max_right(self, table):
        x = np.poly1d(self.field_max_right_res)(table.y)
        if table.x - x > 10:
            return True
        else:
            return False

    def is_table(self, table):
        return not self.is_over_field_max_right(table)

    def return_center_x(self, a):
        return a.center[0]

    def return_center_y(self, a):
        return a.center[1]

    def return_radius(self, a):
        return a.radius

    def radius_filter(self, a):
        return self.radius_filter_front[0] > a.radius > self.radius_filter_front[1]

    def distance_filter(self, a):
        return self.distance_filter_front[0] < a.dist < self.distance_filter_front[1]

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

    def put_center(self, image, table_set, color):
        c_image = self.put_text(image, str(table_set.under.center_float), table_set.under.center,
                                         color)
        c_image = self.put_text(c_image, str(table_set.middle.center_float), table_set.middle.center,
                                         color)
        c_image = self.put_text(c_image, str(table_set.up.center_float), table_set.up.center,
                                         color)
        return c_image

    def put_info_by_set(self, image, table_set, center_color=(0, 0, 0)):
        c_image = self.put_center(image, table_set, center_color)
        c_image = self.put_info(c_image, table_set.under)
        c_image = self.put_info(c_image, table_set.middle)
        c_image = self.put_info(c_image, table_set.up)
        return c_image

    def get_under_table_boundingbox(self, image, table_set, y_offset=15):
        return image[table_set.under.y - table_set.under.radius - y_offset:table_set.under.y + table_set.under.radius + y_offset,
        table_set.under.x - table_set.under.radius - 20:table_set.under.x + table_set.under.radius + 20]

    def get_middle_table_boundingbox(self, image, table_set, y_offset=15):
        return image[table_set.middle.y - table_set.middle.radius - y_offset:table_set.middle.y + table_set.middle.radius + y_offset,
        table_set.middle.x - table_set.middle.radius - 20:table_set.middle.x + table_set.middle.radius + 20]

    def get_up_table_boundingbox(self, image, table_set, y_offset=15):
        return image[table_set.up.y - table_set.up.radius - y_offset:table_set.up.y + table_set.up.radius + y_offset,
        table_set.up.x - table_set.up.radius - 20:table_set.up.x + table_set.up.radius + 20]

    def check_by_keras(self, table_set, image_list):
        # keras
        def resize(im):
            im = cv2.resize(im, (50, 50))
            return im
        image_list = list(map(resize, image_list))

        table_set.under.standing = self.model.predict_classes(np.array([image_list[0] / 255.]), 100)[0]
        table_set.middle.standing = self.model.predict_classes(np.array([image_list[1] / 255.]), 100)[0]
        table_set.up.standing = self.model.predict_classes(np.array([image_list[2] / 255.]), 100)[0]

    def check_by_tensorflow(self, table_set, image_list):
        # tensorflow
        sd = StandingDetection()
        ret = np.array(list(map(sd.detect, image_list)))
        ret = ret == 'stand'
        table_set.under.standing = ret[0]
        table_set.middle.standing = ret[1]
        table_set.up.standing = ret[2]

    def check_standing(self, color_image_for_save, table_set):
        under = self.get_under_table_boundingbox(color_image_for_save, table_set, 10)
        middle = self.get_middle_table_boundingbox(color_image_for_save, table_set, 10)
        up = self.get_up_table_boundingbox(color_image_for_save, table_set, 10)
        image_list = [under, middle, up]
        if  self.tensorflow:
            self.check_by_tensorflow(table_set, image_list)
        else:
            self.check_by_keras(table_set, image_list)

    def check_led(self, color_image):
        # スライダーの値から緑色の上限値、下限値を指定
        upper_green = np.array([64, 0, 251])
        lower_green = np.array([94, 63, 255])
        # hsv空間に変換
        hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        # 緑色でマスク
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        # 同じ部分だけ抽出
        res_green = cv2.bitwise_and(color_image, color_image, mask=mask_green)
        # グレースケールに変換
        gray = cv2.cvtColor(res_green, cv2.COLOR_RGB2GRAY)
        # 二値化
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # print(np.sum(thresh == 255))

    def log_standing(self, table_set):
        if table_set.under.standing:
            logging.info('under:standing')
        elif table_set.under.standing is None:
            logging.error('Not detected')
        else:
            logging.info('under:falling down')
        if table_set.middle.standing:
            logging.info('middle:standing')
        elif table_set.middle.standing is None:
            logging.error('Not detected')
        else:
            print('middle:falling down')
        if table_set.up.standing:
            logging.info('up:standing')
        elif table_set.up.standing is None:
            logging.error('Not detected')
        else:
            logging.info('up:falling down')

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

    def save_param(self, h, s, v, lv, th, kn, rms):
        self.settings['h'] = h
        self.settings['s'] = s
        self.settings['v'] = v
        self.settings['lv'] = lv
        self.settings['th'] = th
        self.settings['k'] = kn
        self.settings['rms'] = rms
        f = open(self.path + self.setting_path, 'w')
        json.dump(self.settings, f)

    def save_table_images(self, image, table_set, y_offset=15):
        cv2.imwrite(f'./table_images/new/{randstr(10)}_under.jpg',
                      self.get_under_table_boundingbox(image, table_set, y_offset))
        # cv2.imwrite(f'./table_images/new/{randstr(10)}_middle.jpg',
        #            self.get_middle_table_boundingbox(image, table_set, y_offset))
        #cv2.imwrite(f'./table_images/new/{randstr(10)}_up.jpg',
        #            self.get_up_table_boundingbox(image, table_set, y_offset))