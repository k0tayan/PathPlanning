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
import time
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
        self.log = True
        self.processing_standing_detection = False

        data = np.loadtxt(self.field_max_right, delimiter=',')
        self.field_max_right_res = np.polyfit(data[:, 1], data[:, 0], 1)
        try:
            f = open(self.path + self.setting_path, 'r')
            self.settings = json.load(f)
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10, 'rms': 9}

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

    def put_text(self, img: object, text: object, pos: object, color: object, size: object = 1,
                 weight: object = 1) -> object:
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

    def put_info_by_set(self, c_image, table_set, center_color=(0, 0, 0)):
        # c_image = self.put_center(image, table_set, center_color)
        c_image = self.put_info(c_image, table_set.under)
        c_image = self.put_info(c_image, table_set.middle)
        c_image = self.put_info(c_image, table_set.up)
        c_image = self.put_text(c_image, "Standing Dt", (10, self.height - 20), center_color, size=2, weight=2)
        return c_image

    def get_under_table_boundingbox(self, image, table_set, y_offset=15):
        ys = table_set.under.y - table_set.under.radius - y_offset
        if ys < 0:
            ys = 0
        yg = table_set.under.y + table_set.under.radius
        if yg > self.height:
            yg = self.height
        xs = table_set.under.x - table_set.under.radius - 20
        if xs < 0:
            xs = 0
        xg = table_set.under.x + table_set.under.radius + 20
        if xg > self.width:
            xg = self.width
        return image[ys:yg, xs:xg]

    def get_middle_table_boundingbox(self, image, table_set, y_offset=15):
        ys = table_set.middle.y - table_set.middle.radius - y_offset
        if ys < 0:
            ys = 0
        yg = table_set.middle.y + table_set.middle.radius
        if yg > self.height:
            yg = self.height
        xs = table_set.middle.x - table_set.middle.radius - 20
        if xs < 0:
            xs = 0
        xg = table_set.middle.x + table_set.middle.radius + 20
        if xg > self.width:
            xg = self.width
        return image[ys:yg, xs:xg]

    def get_up_table_boundingbox(self, image, table_set, y_offset=15):
        ys = table_set.up.y - table_set.up.radius - y_offset
        if ys < 0:
            ys = 0
        yg = table_set.up.y + table_set.up.radius + y_offset
        if yg > self.height:
            yg = self.height
        xs = table_set.up.x - table_set.up.radius - 20
        if xs < 0:
            xs = 0
        xg = table_set.up.x + table_set.up.radius + 20
        if xg > self.width:
            xg = self.width
        return image[ys:yg, xs:xg]

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
        self.log = True
        self.processing_standing_detection = True
        logging.info('START STANDING DETECTION')
        under = self.get_under_table_boundingbox(color_image_for_save, table_set, 15)
        middle = self.get_middle_table_boundingbox(color_image_for_save, table_set, 15)
        up = self.get_up_table_boundingbox(color_image_for_save, table_set, 15)
        if self.tensorflow:
            image_list = [[under, 0], [middle, 1], [up, 2]]
            thread = threading.Thread(target=self.check_by_tensorflow, args=(table_set, image_list), daemon=True, )
            thread.start()
        else:
            image_list = [under, middle, up]
            self.check_by_keras(table_set, image_list)

    def check_led(self, for_check):
        image = for_check[300:, :]
        image = cv2.medianBlur(image, 5)
        # スライダーの値から緑色の上限値、下限値を指定
        lower_green = np.array([64, 0, 251])
        upper_green = np.array([94, 63, 255])
        # hsv空間に変換
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # 緑色でマスク
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        # 同じ部分だけ抽出
        res_green = cv2.bitwise_and(image, image, mask=mask_green)
        # グレースケールに変換
        gray = cv2.cvtColor(res_green, cv2.COLOR_RGB2GRAY)
        # 二値化
        ret, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # 縮小と膨張
        kernel = np.ones((12, 12), np.uint8)
        erode = cv2.erode(thresh, kernel)
        thresh = cv2.dilate(erode, kernel)

        imgEdge, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        sum = np.sum(thresh == 255)
        return sum

    def log_standing(self, table_set):
        if self.log:
            logging.info('Bottle status')
            if table_set.under.standing:
                print('under:standing')
            elif table_set.under.standing is None:
                logging.error('Not detected')
            else:
                print('under:falling down')
            if table_set.middle.standing:
                print('middle:standing')
            elif table_set.middle.standing is None:
                logging.error('Not detected')
            else:
                print('middle:falling down')
            if table_set.up.standing:
                print('up:standing')
            elif table_set.up.standing is None:
                logging.error('Not detected')
            else:
                print('up:falling down')
            self.log = False

    def put_standing_detection_result(self, image, table_set, result):
        under, middle, up = result
        if self.zone:
            sim = cv2.imread(self.red_field_image)
        else:
            sim = cv2.imread(self.blue_field_image)
        if under:
            cv2.circle(image, table_set.under.center, table_set.under.radius + 10, Color.light_green, 3)
            cv2.circle(sim, (275, 220), 80, Color.red, 4)
        elif under is not None:
            cv2.line(sim, (205, 205), (348, 348), Color.blue, 6)
            cv2.line(sim, (205, 348), (348, 205), Color.blue, 6)
        if middle:
            cv2.circle(image, table_set.middle.center, table_set.middle.radius + 10, Color.light_green, 3)
            cv2.circle(sim, (620, 175), 80, Color.red, 4)
        elif middle is not None:
            cv2.line(sim, (546, 146), (699, 280), Color.blue, 6)
            cv2.line(sim, (546, 280), (699, 146), Color.blue, 6)
        if up:
            cv2.circle(image, table_set.up.center, table_set.up.radius + 10, Color.light_green, 3)
            cv2.circle(sim, (1025, 110), 80, Color.red, 4)
        elif up is not None:
            cv2.line(sim, (953, 25), (1100, 180), Color.blue, 6)
            cv2.line(sim, (953, 180), (1100, 25), Color.blue, 6)
        return sim

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
        cv2.imwrite(f'./table_images/new/under_{randstr(10)}.jpg',
                      self.get_under_table_boundingbox(image, table_set, y_offset))
        cv2.imwrite(f'./table_images/new/middle_{randstr(10)}.jpg',
                    self.get_middle_table_boundingbox(image, table_set, y_offset))
        cv2.imwrite(f'./table_images/new/up_{randstr(10)}.jpg',
                    self.get_up_table_boundingbox(image, table_set, y_offset))
