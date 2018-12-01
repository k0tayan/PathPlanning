from .config import *
from .objects import *
import threading
import coloredlogs, logging
import cv2
import random
import string
import numpy as np
import json
import os
import time
from .predict import initialize, predict_image
from .consts import (STAND, FALLEN_DOWN, FALLEN, FIELD_WIDTH, TABLE_WIDTH)
from .detection import Tables


def randstr(n):
    random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
    return random_str


class Utils(Config, Path):
    def __init__(self):
        self.log = True
        self.processing_standing_detection = False
        self.start_standing_detection_time = 0

        try:
            f = open(self.setting_path, 'r')
            self.settings = json.load(f)
            if self.zone:
                self.settings['rms'] = 19
            else:
                self.settings['rms'] = 20
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10, 'rms': 19}

        # Load and intialize the model
        initialize()

    def get_table_bounding_box(self, image, table: Table, x_offset=20, y_offset=15):
        ys = table.y - table.radius - y_offset
        if ys < 0:
            ys = 0
        yg = table.y + table.radius
        yg = int(yg*0.95)
        if yg > self.height:
            yg = self.height
        xs = table.x - table.radius - x_offset
        if xs < 0:
            xs = 0
        xg = table.x + table.radius + x_offset
        if xg > self.width:
            xg = self.width
        return image[ys:yg, xs:xg]

    def check_by_custom_vision(self, table_set: Tables, image_list):
        results = list(map(predict_image, image_list))
        ret = np.array([])
        for result in results:
            max_pre = 0
            print(result)
            if len(result['predictions']) > 1:
                pre = 0
                for re in result['predictions']:
                    tag = re['tagName']
                    if tag == STAND:
                        pre = re['probability']
                        # print('stand:', pre)
                    elif tag == FALLEN_DOWN:
                        pre = re['probability']
                        # print('fallen_down:', pre)
                    elif tag == FALLEN:
                        pre = re['probability']
                        # print('fallen:', pre)
                    if max_pre < pre:
                        max_pre = pre
                        max_label = tag
            else:
                max_label = result['predictions'][0]['tagName']
                # print(result['predictions'])
            ret = np.append(ret, max_label)
        print(ret)
        logging.info(f'END STANDING DETECTION:{round(time.time() - self.start_standing_detection_time, 3)}[sec]')
        if np.all(ret == FALLEN):
            table_set.reset_standing_result()
        else:
            table_set.under.standing, table_set.middle.standing, table_set.up.standing = (ret == STAND)
        self.processing_standing_detection = False

    def check_standing(self, color_image_for_save, table_set):
        self.log = True
        self.processing_standing_detection = True
        self.start_standing_detection_time = time.time()
        logging.info('START STANDING DETECTION')
        under = self.get_table_bounding_box(color_image_for_save, table_set.under, x_offset=30, y_offset=40)
        middle = self.get_table_bounding_box(color_image_for_save, table_set.middle)
        up = self.get_table_bounding_box(color_image_for_save, table_set.up)
        image_list = [under, middle, up]
        thread = threading.Thread(target=self.check_by_custom_vision, args=(table_set, image_list),
                                  daemon=True, )
        thread.start()

    def make_distance_to_send(self, tables):
        t = T()
        t.under = FIELD_WIDTH - (int(tables.under.dist * 1000) + TABLE_WIDTH / 2)
        t.middle = FIELD_WIDTH - (int(tables.middle.dist * 1000) + TABLE_WIDTH / 2)
        t.up = FIELD_WIDTH - (int(tables.up.dist * 1000) + TABLE_WIDTH / 2)
        t.fix()
        return t

    def calc_circle_level(self, contour, area):
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return 0
        else:
            circle_level = 4.0 * np.pi * area / (perimeter * perimeter) # perimeter = 0 のとき気をつける
            return circle_level

    def save_param(self, h, s, v, lv, th, kn, rms):
        self.settings['h'] = h
        self.settings['s'] = s
        self.settings['v'] = v
        self.settings['lv'] = lv
        self.settings['th'] = th
        self.settings['k'] = kn
        self.settings['rms'] = rms
        f = open(self.setting_path, 'w')
        json.dump(self.settings, f)

    def save_table_images(self, image, table_set, x_offset=20, y_offset=15):
        cv2.imwrite(f'./table_images/new/under_{randstr(10)}.jpg', self.get_table_bounding_box(image, table_set.under, x_offset=30, y_offset=40))
        cv2.imwrite(f'./table_images/new/middle_{randstr(10)}.jpg',
                    self.get_table_bounding_box(image, table_set.middle))
        cv2.imwrite(f'./table_images/new/up_{randstr(10)}.jpg', self.get_table_bounding_box(image, table_set.up))

    def save_table_images_for_check(self, image, table_set, y_offset=15):
        cv2.imwrite('./table_images/tmp/under.jpg', self.get_table_bounding_box(image, table_set.under))
        cv2.imwrite('./table_images/tmp/middle.jpg', self.get_table_bounding_box(image, table_set.middle))
        cv2.imwrite('./table_images/tmp/up.jpg', self.get_table_bounding_box(image, table_set.up))
