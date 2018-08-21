import pyrealsense2 as rs
import numpy as np
import socket
import struct
import os
import json
import cv2
try:
    from .rsd.Detection import Table, Utils
except:
    from rsd.Detection import Table, Utils

path = os.path.dirname(os.path.abspath(__file__))

width = 640
height = 480
# width = 1280
# height = 720
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
config.enable_stream(rs.stream.color, width, height, rs.format.bgr8,30)
pipeline.start(config)
lower_white = np.array([0, 0, 100])
back_image = cv2.imread(path + '/field_background.png', 0)
util = Utils()
count = 300
nud, nmd, nup = 0, 0, 0
under = np.array([])
middle = np.array([])
up = np.array([])

def putText(img, text, pos, color):
    cv2.putText(img, text, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

cv2.namedWindow('image')
cv2.createTrackbar('H', 'image', 0, 255, util.nothing)
cv2.createTrackbar('S', 'image', 0, 255, util.nothing)
cv2.createTrackbar('V', 'image', 0, 255, util.nothing)
cv2.createTrackbar('threshold', 'image', 0, 255, util.nothing)
cv2.createTrackbar('kernel', 'image', 0, 30,util.nothing)

cv2.setTrackbarPos('H', 'image', util.settings['h'])
cv2.setTrackbarPos('S', 'image', util.settings['s'])
cv2.setTrackbarPos('V', 'image', util.settings['v'])
cv2.setTrackbarPos('threshold', 'image', util.settings['th'])
cv2.setTrackbarPos('kernel', 'image', util.settings['k'])

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
            # color_image = cv2.resize(color_image, (640, 360))
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
            tables = list(filter(util.distance_filter, tables))

            # 半径でフィルタ
            tables = list(filter(util.radius_filter, tables))

            # 半径が大きい順にソート
            tables.sort(key=util.return_radius)

            # 大きい3つだけを抽出
            tables = tables[:3]

            # X座標が小さい順にソート
            tables.sort(key=util.return_center, reverse=True)

            # 画面に描画
            for i, table in enumerate(tables):
                img = cv2.circle(color_image_copy, table.center, table.radius, (0, 255, 0), 2)
                img = cv2.circle(color_image_copy, table.center, 3, (0, 255, 0), 2)
                if table.center[0] < 268:
                    table.type = 'under'
                    under = np.append(under, table.dist)
                    if under.size > count:
                        under = np.delete(under, 0)
                        table.dist = round(under.mean(), 3)
                    else:
                        nud += 1
                        table.dist = 0
                if 268 <= table.center[0] < 360:
                    table.type = 'middle'
                    middle = np.append(middle, table.dist)
                    if middle.size > count:
                        middle = np.delete(middle, 0)
                        table.dist = round(middle.mean(), 3)
                    else:
                        nmd += 1
                        table.dist = 0
                if 360 <= table.center[0]:
                    table.type = 'up'
                    up = np.append(up, table.dist)
                    if up.size > count:
                        up = np.delete(up, 0)
                        table.dist = round(up.mean(), 3)
                    else:
                        nup += 1
                        table.dist = 0
                putText(img, str(table.dist), table.center, (255, 255, 0))
                type_text = list(table.center)
                type_text[0] -= 10
                type_text[1] -= 50
                putText(img, str(table.type), type_text, (255, 51, 255))

            thresh = cv2.applyColorMap(cv2.convertScaleAbs(thresh), cv2.COLORMAP_BONE)
            images = np.hstack((img, thresh))

            putText(images, f"{str(count-nud)}, {str(count-nmd)}, {str(count-nup)}", (10, 40), (255, 255, 255))
            cv2.imshow("image", images)

            k = cv2.waitKey(1)
            if k == ord('q'):
                break
            if k == ord('w'):
                if len(tables) == 3:
                    ret = util.make_coordinate(tables)
                    if ret:
                        x1, x2, x3 = ret
                        util.send_coordinate(x1, x2, x3)
            if k == ord('s'):
                util.settings['h'] = h
                util.settings['s'] = s
                util.settings['v'] = v
                util.settings['th'] = th
                util.settings['k'] = kn
                util.save_file(util.settings)
                cv2.imwrite(path + '/field_background.png', thresh)

        except Exception as error:
            print(error)
except:
    pass
finally:
    pipeline.stop()
