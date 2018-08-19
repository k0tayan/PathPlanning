import pyrealsense2 as rs
import cv2
import numpy as np
import socket
import struct
import os
import json

path = os.path.dirname(os.path.abspath(__file__))

width = 640
height = 480
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
pipeline.start(config)
lower_white = np.array([0, 0, 100])
under = np.array([])
middle = np.array([])
up = np.array([])
back_image = cv2.imread(path + '/field_background.png', 0)

try:
    f = open(path + '/settings.json', 'r')
    settings = json.load(f)
except:
    settings = {'h': 180, 's': 45, 'v': 255, 'th': 210, 'k': 10}

try:
    cl = socket.socket()
    cl.connect(('localhost', 4000))
    is_tcp_available = True
except:
    print('Cant connect to path_planning')
    is_tcp_available = False


class Table:
    def __init__(self, center, radius, dist):
        self.center = center
        self.radius = radius
        self.dist = round(dist, 3)
        self.type = ''


def return_center(a):
    return a.center


def return_radius(a):
    return a.radius


def radius_filter(a):
    return 200 > a.radius > 1


def distance_filter(a):
    return 0.5 < a.dist < 6.5


def nothing(x):
    pass


def make_coordinate(tables):
    _x1, _x2, _x3 = None, None, None
    for table in tables:
        if table.type == 'under':
            _x1 = int(table.dist * 1000)
        if table.type == 'middle':
            _x2 = int(table.dist * 1000)
        if table.type == 'up':
            _x3 = int(table.dist * 1000)
    # _x1 = 2500
    # _x2 = 2500
    # _x3 = 2500
    print(_x1, _x2, _x3)
    if _x1 is None or _x2 is None or _x3 is None:
        return False
    else:
        return _x1, _x2, _x3


def send_coordinate(under, middle, up):
    if is_tcp_available:
        b = struct.pack("iii?", under, middle, up, 0)
        cl.send(b)


def putText(img, text, pos, color):
    cv2.putText(img, text, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)


def save_file(dic):
    f2 = open(path + '/settings.json', 'w')
    json.dump(dic, f2)


cv2.namedWindow('image')
cv2.createTrackbar('H', 'image', 0, 255, nothing)
cv2.createTrackbar('S', 'image', 0, 255, nothing)
cv2.createTrackbar('V', 'image', 0, 255, nothing)
cv2.createTrackbar('threshold', 'image', 0, 255, nothing)
cv2.createTrackbar('kernel', 'image', 0, 30, nothing)

cv2.setTrackbarPos('H', 'image', settings['h'])
cv2.setTrackbarPos('S', 'image', settings['s'])
cv2.setTrackbarPos('V', 'image', settings['v'])
cv2.setTrackbarPos('threshold', 'image', settings['th'])
cv2.setTrackbarPos('kernel', 'image', settings['k'])

try:
    while True:
        try:
            h = cv2.getTrackbarPos('H', 'image')
            s = cv2.getTrackbarPos('S', 'image')
            v = cv2.getTrackbarPos('V', 'image')
            th = cv2.getTrackbarPos('threshold', 'image')
            kn = cv2.getTrackbarPos('kernel', 'image')

            upper_white = np.array([h, s, v])

            frames = pipeline.wait_for_frames()
            depth = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())
            color_image_copy = color_image

            color_image = cv2.medianBlur(color_image, 5)
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            res_white = cv2.bitwise_and(color_image, color_image, mask=mask_white)

            gray = cv2.cvtColor(res_white, cv2.COLOR_RGB2GRAY)
            ret, thresh = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)

            # 背景差分
            """img_diff = cv2.absdiff(thresh, back_image)
            img_diffm = cv2.threshold(img_diff, 20, 255, cv2.THRESH_BINARY)[1]
            operator = np.ones((3, 3), np.uint8)
            img_dilate = cv2.dilate(img_diffm, operator, iterations=4)
            img_mask = cv2.erode(img_dilate, operator, iterations=4)
            thresh = cv2.bitwise_and(thresh, img_mask)"""

            kernel = np.ones((kn, kn), np.uint8)
            erode = cv2.erode(thresh, kernel)
            thresh = cv2.dilate(erode, kernel)

            # 各座標について遠すぎるやつは黒で埋める
            # for y in range(480):
            #    for x in range(640):
            #        dist = depth.get_distance(x, y)
            #        if 6.7 < dist:
            #            thresh[y][x] = 0
            # print(thresh)

            # 輪郭抽出
            imgEdge, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            img = color_image

            # 見つかった輪郭をリストに入れる
            tables = []
            contours.sort(key=cv2.contourArea, reverse=True)
            for cnt in contours:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                dist = depth.get_distance(int(x), int(y))
                table = Table(center, radius, dist)
                tables.append(table)

            # 距離でフィルタ
            tables = list(filter(distance_filter, tables))

            # 半径でフィルタ
            tables = list(filter(radius_filter, tables))

            # 半径が大きい順にソート
            tables.sort(key=return_radius)

            # 大きい3つだけを抽出
            tables = tables[:3]

            # X座標が小さい順にソート
            tables.sort(key=return_center, reverse=True)

            # 画面に描画
            for i, table in enumerate(tables):
                img = cv2.circle(color_image_copy, table.center, table.radius, (0, 255, 0), 2)
                img = cv2.circle(color_image_copy, table.center, 3, (0, 255, 0), 2)
                if table.center[0] < 178:
                    table.type = 'under'
                    # under = np.append(under, table.dist)
                    # table.dist = round(under.mean(), 3)
                if 178 <= table.center[0] < 376:
                    table.type = 'middle'
                    # middle = np.append(middle, table.dist)
                    # table.dist = round(middle.mean(), 3)
                if 376 <= table.center[0]:
                    table.type = 'up'
                    # up = np.append(up, table.dist)
                    # table.dist = round(up.mean(), 3)
                putText(img, str(table.dist), table.center, (255, 255, 0))
                type_text = list(table.center)
                type_text[0] -= 10
                type_text[1] -= 50
                putText(img, str(table.type), type_text, (255, 51, 255))
                # sys.stdout.write(str(table.center) + ':' + str(table.dist) + ' ')
            # sys.stdout.write('\r\n')

            thresh = cv2.applyColorMap(cv2.convertScaleAbs(thresh), cv2.COLORMAP_BONE)
            images = np.hstack((img, thresh))

            cv2.imshow("image", images)

            k = cv2.waitKey(1)
            if k == ord('q'):
                break
            if k == ord('w'):
                if len(tables) == 3:
                    ret = make_coordinate(tables)
                    if ret:
                        x1, x2, x3 = ret
                        send_coordinate(x1, x2, x3)
            if k == ord('s'):
                settings['h'] = h
                settings['s'] = s
                settings['v'] = v
                settings['th'] = th
                settings['k'] = kn
                save_file(settings)
                cv2.imwrite(path + '/field_background.png', thresh)

        except Exception as error:
            print(error)
except:
    pass
finally:
    pipeline.stop()
