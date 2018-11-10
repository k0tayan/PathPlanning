import numpy as np
import cv2


class PointList:
    def __init__(self, npoints):
        self.npoints = npoints
        self.ptlist = []
        self.pos = 0

    def add(self, x, y):
        if self.pos < self.npoints:
            self.ptlist.append((x, y))
            self.pos += 1
            return True
        return False

    def get_points(self):
        return self.ptlist

    def reset_points(self):
        self.pos = 0
        self.ptlist = []

    def is_full(self):
        return self.pos == self.npoints


class Event:
    def onMouse(self, event, x, y, flag, params):
        wname, img, ptlist = params
        if event == cv2.EVENT_LBUTTONDOWN:  # レフトボタンをクリックしたとき、ptlist配列にx,y座標を格納する
            if ptlist.add(x, y):
                print('[%d] ( %d, %d )' % (ptlist.pos - 1, x, y))
            else:
                print('All points have selected.')
