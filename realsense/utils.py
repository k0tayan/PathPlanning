from .sd.label_image import StandingDetection
from .config import *
from .objects import *
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
from .predict import initialize, predict_image
from .types import Types


def randstr(n):
    random_str = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])
    return random_str


class Utils(Config, Field, Path, Types):
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.nothing = lambda x: x
        self.model = load_model(self.keras_green_model)
        self.log = True
        self.processing_standing_detection = False
        self.start_standing_detection_time = 0

        try:
            f = open(self.path + self.setting_path, 'r')
            self.settings = json.load(f)
            if self.zone:
                self.settings['rms'] = 9
            else:
                self.settings['rms'] = 18
        except:
            self.settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10, 'rms': 9}

        # Load and intialize the model
        initialize()

    def put_text(self, img, text, pos, color, size=1, weight=1):
        return cv2.putText(img, text, tuple(pos), cv2.FONT_HERSHEY_TRIPLEX, size, color, weight, cv2.LINE_AA)

    def rectangle(self, image, center, radius, weight=2):
        if self.zone:
            color = Color.red
        else:
            color = Color.blue
        x, y = center
        color_image_copy = cv2.rectangle(image, (x - radius, y - radius), (x + radius, y + radius), color, weight)
        return color_image_copy

    def put_type_name(self, image, table: Table):
        x, y = table.center
        return self.put_text(image, table.type, (x - 10, y -50), Color.black, size=1, weight=2)

    def put_dist(self, image, table: Table):
        x, y =  table.center
        return self.put_text(image, str(table.dist), (x, y + 100), Color.black, size=1, weight=2)

    def put_info(self, image, table: Table):
        c_image = self.rectangle(image, table.center, table.radius)
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

    def check_by_custom_vision(self, table_set, image):
        self.save_table_images_for_check(image, table_set, 20)
        image_list = [cv2.imread('./table_images/tmp/under.jpg'),
                      cv2.imread('./table_images/tmp/middle.jpg'),
                      cv2.imread('./table_images/tmp/up.jpg')]
        # results = list(map(predict_image, image_list))

        results = []
        results.append(predict_image(image_list[0]))
        results.append(predict_image(image_list[1]))
        results.append(predict_image(image_list[2]))

        ret = np.array([])
        for result in results:
            if len(result['predictions']) > 1:
                stand_pre = 0
                fallen_down_pre = 0
                fallen_pre = 0
                for re in result['predictions']:
                    tag = re['tagName']
                    if tag == self.stand:
                        stand_pre = re['probability']
                        print('stand:', stand_pre)
                    elif tag == self.fallendown:
                        fallen_down_pre = re['probability']
                        print('fallen_down:', fallen_down_pre)
                    elif tag == self.fallen:
                        fallen_pre = re['probability']
                        print('fallen:', fallen_pre)
                    fallen_down_pre = max(fallen_down_pre, fallen_pre)
                if stand_pre > fallen_down_pre:
                    r = self.stand
                else:
                    r = self.fallendown
            else:
                r = result['predictions'][0]['tagName']
                print(result['predictions'])
                if r == self.fallen:
                    r = self.fallendown
            ret = np.append(ret, r)
        print(ret)
        logging.info(f'END STANDING DETECTION:{round(time.time() - self.start_standing_detection_time, 3)}[sec]')
        ret = ret == self.stand
        table_set.under.standing, table_set.middle.standing, table_set.up.standing = ret

    def check_standing(self, color_image_for_save, table_set):
        self.log = True
        self.processing_standing_detection = True
        self.start_standing_detection_time = time.time()
        logging.info('START STANDING DETECTION')
        under = self.get_under_table_boundingbox(color_image_for_save, table_set, 20)
        middle = self.get_middle_table_boundingbox(color_image_for_save, table_set, 20)
        up = self.get_up_table_boundingbox(color_image_for_save, table_set, 20)
        if self.custom_vision:
            image_list = [under, middle, up]
            # self.check_by_custom_vision(table_set, image_list)
            thread = threading.Thread(target=self.check_by_custom_vision, args=(table_set, color_image_for_save),
                                      daemon=True, )
            thread.start()
        else:
            image_list = [under, middle, up]
            self.check_by_keras(table_set, image_list)

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
        f = open(self.path + self.setting_path, 'w')
        json.dump(self.settings, f)

    def save_table_images(self, image, table_set, y_offset=15):
        cv2.imwrite(f'./table_images/new/under_{randstr(10)}.jpg',
                    self.get_under_table_boundingbox(image, table_set, y_offset))
        cv2.imwrite(f'./table_images/new/middle_{randstr(10)}.jpg',
                    self.get_middle_table_boundingbox(image, table_set, y_offset))
        cv2.imwrite(f'./table_images/new/up_{randstr(10)}.jpg',
                    self.get_up_table_boundingbox(image, table_set, y_offset))

    def save_table_images_for_check(self, image, table_set, y_offset=15):
        cv2.imwrite('./table_images/tmp/under.jpg',
                    self.get_under_table_boundingbox(image, table_set, y_offset))
        cv2.imwrite('./table_images/tmp/middle.jpg',
                    self.get_middle_table_boundingbox(image, table_set, y_offset))
        cv2.imwrite('./table_images/tmp/up.jpg',
                    self.get_up_table_boundingbox(image, table_set, y_offset))
