import cv2
from .config import Config, Color, Path
from .objects import Table
import numpy as np

window_name = 'PathPlanning'
path_window_name = 'Path'
bar_window_name = window_name + '-setting'
field_window_name = 'Field'

class Draw(Config, Path):
    def __init__(self):
        self.window_name = window_name
        self.path_window_name = path_window_name
        self.bar_window_name = bar_window_name
        self.field_window_name = field_window_name

        cv2.namedWindow(bar_window_name, cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow(field_window_name, cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty(field_window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        kizunaai = cv2.imread('./kizunaai/kizunaai.jpg')
        cv2.imshow(field_window_name, kizunaai)

    def set_track_bar_pos(self, settings: dict):
        cv2.createTrackbar('H', self.bar_window_name, 0, 255, int)
        cv2.createTrackbar('S', self.bar_window_name, 0, 255, int)
        cv2.createTrackbar('V', self.bar_window_name, 0, 255, int)
        cv2.createTrackbar('LV', self.bar_window_name, 0, 255, int)
        cv2.createTrackbar('threshold', self.bar_window_name, 0, 255, int)
        cv2.createTrackbar('kernel', self.bar_window_name, 0, 100, int)
        cv2.createTrackbar('remove_side', self.bar_window_name, 0, 30, int)
        cv2.createTrackbar('remove_side_e', self.bar_window_name, 0, self.height, int)
        cv2.createTrackbar('zone', self.bar_window_name, 0, 1, int)

        cv2.setTrackbarPos('H', self.bar_window_name, settings['h'])
        cv2.setTrackbarPos('S', self.bar_window_name, settings['s'])
        cv2.setTrackbarPos('V', self.bar_window_name, settings['v'])
        cv2.setTrackbarPos('LV', self.bar_window_name, settings['lv'])
        cv2.setTrackbarPos('threshold', self.bar_window_name, settings['th'])
        cv2.setTrackbarPos('kernel', self.bar_window_name, settings['k'])
        cv2.setTrackbarPos('remove_side', self.bar_window_name, settings['rms'])
        cv2.setTrackbarPos('remove_side_e', self.bar_window_name, int(self.height / 3))
        cv2.setTrackbarPos('zone', self.bar_window_name, self.zone)

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
        return self.put_text(image, table.type, (x - 10, y - 50), Color.black, size=1, weight=2)

    def put_dist(self, image, table: Table):
        x, y = table.center
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




class FieldView(Config):
    def __init__(self):
        pass

    def init(self):
        size = self.height, self.width, 3
        img = np.zeros(size, dtype=np.uint8)
        contours = np.array([[0, 0], [0, 720], [1280, 720], [1280, 0]])
        cv2.fillPoly(img, pts=[contours], color=(63, 101, 150))
        self.white_line(img, self.f(3500, 0), self.f(3500, 5000))
        self.white_line(img, self.f(5500, 0), self.f(5500, 5000))
        self.white_line(img, self.f(6500, 0), self.f(6500, 5000))
        self.white_line(img, self.f(7500, 0), self.f(7500, 5000))
        self.white_line(img, self.f(5450, 1000), self.f(5550, 1000))
        self.white_line(img, self.f(5450, 4000), self.f(5550, 4000))
        self.white_line(img, self.f(6450, 1000), self.f(6550, 1000))
        self.white_line(img, self.f(6450, 4000), self.f(6550, 4000))
        self.white_line(img, self.f(7450, 1000), self.f(7550, 1000))
        self.white_line(img, self.f(7450, 4000), self.f(7550, 4000))
        self.img = img

    def f(self, x, y):
        return int(x * (1280 / 8000)), int(y * (720 / 5000))

    def fp(self, tp):
        return int(tp[0] * (1280 / 8000)), int(tp[1] * (720 / 5000))

    def two_stage_table(self, image, pos):
        p1 = self.f(pos[0] + 400, pos[1] - 400)
        p2 = self.f(pos[0] - 400, pos[1] + 400)
        if self.zone:
            cv2.rectangle(image, p1, p2, (0, 0, 255), -1)
        else:
            cv2.rectangle(image, p1, p2, (255, 0, 0), -1)

    def white_line(self, image, pos1, pos2):
        cv2.line(image, pos1, pos2, (255, 255, 255), thickness=5)

    def path_line(self, image, points):
        m = len(points) - 1
        for i, point in enumerate(points):
            y, x = point
            if i == 0:
                if self.zone:
                    cv2.line(image, self.f(1000, 600), self.f(x, y), (0, 128, 0), 3)
                else:
                    cv2.line(image, self.f(1000, 4400), self.f(x, y), (0, 128, 0), 3)
            if i != m:
                y2, x2 = points[i + 1]
                cv2.line(image, self.f(x, y), self.f(x2, y2), (0, 128, 0), 3)
        if self.zone:
            cv2.circle(image, self.f(1000, 600), 10, (128, 0, 128), -1)
        else:
            cv2.circle(image, self.f(1000, 4400), 10, (128, 0, 128), -1)
        for i, point in enumerate(points):
            y, x = point
            cv2.circle(image, self.f(x, y), 10, (128, 0, 128), -1)

    def move_table(self, image, points):
        for i, point in enumerate(points):
            y = point
            if i == 0:
                x = 5500
            elif i == 1:
                x = 6500
            elif i == 2:
                x = 7500
            else:
                x = 0
            cv2.rectangle(image, self.f(x + 250, y - 250), self.f(x - 250, y + 250), (0, 255, 255), -1)

    def draw_field(self, move_table_pos, points):
        self.init()
        if self.zone:
            cv2.rectangle(self.img, self.f(0, 0), self.f(2000, 1200), (55, 54, 149), -1)
            self.two_stage_table(self.img, (3500, 3000))
        else:
            cv2.rectangle(self.img, self.f(2000, 3800), self.f(0, 5000), (165, 78, 62), -1)
            self.two_stage_table(self.img, (3500, 2000))
        self.move_table(self.img, move_table_pos)
        points = [(int(point.x), int(point.y)) for point in points]
        self.path_line(self.img, points)
        return self.img
