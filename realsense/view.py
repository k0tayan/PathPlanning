import cv2
from .config import Config
import numpy as np
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
