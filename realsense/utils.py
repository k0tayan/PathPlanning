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
from .types import Types
from .detection import Tables


def randstr(n):
    random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
    return random_str


class Utils(Config, Field, Path, Types):
    def __init__(self):
        self.log = True
        self.processing_standing_detection = False
        self.start_standing_detection_time = 0

        try:
            f = open(self.setting_path, 'r')
            self.settings = json.load(f)
            if self.zone:
                self.settings['rms'] = 9
            else:
                self.settings['rms'] = 18
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10, 'rms': 9}

        # Load and intialize the model
        initialize()

    def get_table_bounding_box(self, image, table: Table, x_offset=20, y_offset=15):
        ys = table.y - table.radius - y_offset
        if ys < 0:
            ys = 0
        yg = table.y + table.radius + y_offset
        if yg > self.height:
            yg = self.height
        xs = table.x - table.radius - x_offset
        if xs < 0:
            xs = 0
        xg = table.x + table.radius + y_offset
        if xg > self.width:
            xg = self.width
        return image[ys:yg, xs:xg]

    # def check_by_keras(self, table_set, image_list):
    #    # keras
    #    def resize(im):
    #        im = cv2.resize(im, (50, 50))
    #        return im

    #   image_list = list(map(resize, image_list))

    #    table_set.under.standing = self.model.predict_classes(np.array([image_list[0] / 255.]), 100)[0]
    #    table_set.middle.standing = self.model.predict_classes(np.array([image_list[1] / 255.]), 100)[0]
    #    table_set.up.standing = self.model.predict_classes(np.array([image_list[2] / 255.]), 100)[0]

    def check_by_custom_vision(self, table_set: Tables, image_list):
        # self.save_table_images_for_check(image, table_set, 20)
        # image_list = [cv2.imread('./table_images/tmp/under.jpg'),
        #               cv2.imread('./table_images/tmp/middle.jpg'),
        #               cv2.imread('./table_images/tmp/up.jpg')]
        results = list(map(predict_image, image_list))

        # results = []
        # results.append(predict_image(image_list[0]))
        # results.append(predict_image(image_list[1]))
        # results.append(predict_image(image_list[2]))

        ret = np.array([])
        for result in results:
            max_pre = 0
            if len(result['predictions']) > 1:
                pre = 0
                for re in result['predictions']:
                    tag = re['tagName']
                    if tag == self.stand:
                        pre = re['probability']
                        print('stand:', pre)
                    elif tag == self.fallendown:
                        pre = re['probability']
                        print('fallen_down:', pre)
                    elif tag == self.fallen:
                        pre = re['probability']
                        print('fallen:', pre)
                    if max_pre < pre:
                        max_pre = pre
                        max_label = tag
            else:
                max_label = result['predictions'][0]['tagName']
                print(result['predictions'])
            ret = np.append(ret, max_label)
        print(ret)
        logging.info(f'END STANDING DETECTION:{round(time.time() - self.start_standing_detection_time, 3)}[sec]')
        if np.all(ret == self.fallen):
            table_set.reset_standing_result()
        else:
            table_set.under.standing, table_set.middle.standing, table_set.up.standing = (ret == self.stand)
        self.processing_standing_detection = False

    def check_standing(self, color_image_for_save, table_set):
        self.log = True
        self.processing_standing_detection = True
        self.start_standing_detection_time = time.time()
        logging.info('START STANDING DETECTION')
        under = self.get_table_bounding_box(color_image_for_save, table_set.under)
        middle = self.get_table_bounding_box(color_image_for_save, table_set.middle)
        up = self.get_table_bounding_box(color_image_for_save, table_set.up)
        if self.custom_vision:
            image_list = [under, middle, up]
            thread = threading.Thread(target=self.check_by_custom_vision, args=(table_set, image_list),
                                      daemon=True, )
            thread.start()

    def make_distance_to_send(self, tables):
        t = T()
        t.under = self.FIELD_WIDTH - (int(tables.under.dist * 1000) + self.TABLE_WIDTH / 2)
        t.middle = self.FIELD_WIDTH - (int(tables.middle.dist * 1000) + self.TABLE_WIDTH / 2)
        t.up = self.FIELD_WIDTH - (int(tables.up.dist * 1000) + self.TABLE_WIDTH / 2)
        t.fix()
        return t

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
        cv2.imwrite(f'./table_images/new/under_{randstr(10)}.jpg', self.get_table_bounding_box(image, table_set.under))
        cv2.imwrite(f'./table_images/new/middle_{randstr(10)}.jpg',
                    self.get_table_bounding_box(image, table_set.middle))
        cv2.imwrite(f'./table_images/new/up_{randstr(10)}.jpg', self.get_table_bounding_box(image, table_set.up))

    def save_table_images_for_check(self, image, table_set, y_offset=15):
        cv2.imwrite('./table_images/tmp/under.jpg', self.get_table_bounding_box(image, table_set.under))
        cv2.imwrite('./table_images/tmp/middle.jpg', self.get_table_bounding_box(image, table_set.middle))
        cv2.imwrite('./table_images/tmp/up.jpg', self.get_table_bounding_box(image, table_set.up))
