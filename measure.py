import pyrealsense2 as rs
import numpy as np
import os
import cv2
import csv
from datetime import datetime as dt

try:
    from rsd.detection import Table, Utils, Tables, ApproximationFunction
except:
    from .rsd.detection import Table, Utils, Tables
from rsd.config import Config, Color, Path

path = os.path.dirname(os.path.abspath(__file__))

if Config.side:
    width = 640
    height = 480
else:
    width = 1280
    height = 720
only_view = True
mode = Config.mode
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
pipeline.start(config)
util = Utils(zone=Config.zone)
table_set = Tables()
func = ApproximationFunction()
to_csv = []
unders = []
middles = []
ups = []

window_name = 'image'
cv2.namedWindow(window_name)
cv2.moveWindow(window_name, 0, 0)
cv2.createTrackbar('H', window_name, 0, 255, util.nothing)
cv2.createTrackbar('S', window_name, 0, 255, util.nothing)
cv2.createTrackbar('V', window_name, 0, 255, util.nothing)
cv2.createTrackbar('LV', window_name, 0, 255, util.nothing)
cv2.createTrackbar('threshold', window_name, 0, 255, util.nothing)
cv2.createTrackbar('kernel', window_name, 0, 30, util.nothing)

cv2.setTrackbarPos('H', window_name, util.settings['h'])
cv2.setTrackbarPos('S', window_name, util.settings['s'])
cv2.setTrackbarPos('V', window_name, util.settings['v'])
cv2.setTrackbarPos('LV', window_name, util.settings['lv'])
cv2.setTrackbarPos('threshold', window_name, util.settings['th'])
cv2.setTrackbarPos('kernel', window_name, util.settings['k'])

try:
    while True:
        try:
            # 深度と画像データを取得
            frames = pipeline.wait_for_frames()
            depth = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())
            depth_data = depth.as_frame().get_data()
            np_image = np.asanyarray(depth_data)

            # キーの入力待ち
            k = cv2.waitKey(1)

            # スライダーの値を取得
            h = cv2.getTrackbarPos('H', window_name)
            s = cv2.getTrackbarPos('S', window_name)
            v = cv2.getTrackbarPos('V', window_name)
            lv = cv2.getTrackbarPos('LV', window_name)
            th = cv2.getTrackbarPos('threshold', window_name)
            kn = cv2.getTrackbarPos('kernel', window_name)

            # スライダーの値から白色の上限値、下限値を指定
            upper_white = np.array([h, s, v])
            lower_white = np.array([0, 0, lv])

            # 画面に描画するようにcolor_imageをコピーした変数を作成
            color_image_copy = color_image


            # ブラーをかける
            color_image = cv2.medianBlur(color_image, 5)
            # hsv空間に変換
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
            # 白色でマスク
            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            # 同じ部分だけ抽出
            res_white = cv2.bitwise_and(color_image, color_image, mask=mask_white)
            # グレースケールに変換
            gray = cv2.cvtColor(res_white, cv2.COLOR_RGB2GRAY)
            # 二値化
            ret, thresh = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)

            # 縮小と膨張
            kernel = np.ones((kn, kn), np.uint8)
            erode = cv2.erode(thresh, kernel)
            thresh = cv2.dilate(erode, kernel)

            white_indexes = list(np.where(thresh > 150))

            for white_index in zip(white_indexes[0], white_indexes[1]):
                dist = np_image[white_index[0]][white_index[1]]
                if (white_index[1], white_index[0]) > (1000, 300) and dist > 2800:
                    thresh[white_index[0]][white_index[1]] = 0
                    color_image_copy[white_index[0]][white_index[1]] = [255, 0, 0]

            # 縮小と膨張
            kernel = np.ones((kn, kn), np.uint8)
            erode = cv2.erode(thresh, kernel)
            thresh = cv2.dilate(erode, kernel)

            # 輪郭抽出
            imgEdge, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # 見つかった輪郭をリストに入れる
            tables = []
            contours.sort(key=cv2.contourArea, reverse=True)
            for cnt in contours:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                dist = depth.get_distance(int(x), int(y))

                # color_image_copy = util.put_text(color_image_copy, str(dist)[:5], (int(x), int(y)+50),
                #                                  Color.black)
                table = Table(center, radius, dist, (x, y))
                tables.append(table)

            # 距離でフィルタ
            # tables = list(filter(util.distance_filter, tables))

            # 半径でフィルタ
            tables = list(filter(util.radius_filter, tables))

            # 半径が大きい順にソート
            tables.sort(key=util.return_radius, reverse=True)

            # 大きい3つだけを抽出
            tables = tables[:3]

            if Config.side: # X座標が小さい順にソート
                tables.sort(key=util.return_center_x)
            else: # Y座標が小さい順にそーと
                tables.sort(key=util.return_center_y)

            for i, _table in enumerate(tables):
                if i == 0:
                    color_image_copy = util.put_text(color_image_copy, 'under', (_table.x-120, _table.y-50),
                                                     Color.black)
                if i == 1:
                    color_image_copy = util.put_text(color_image_copy, 'middle', (_table.x-120, _table.y-50),
                                                     Color.black)
                if i == 2:
                    color_image_copy = util.put_text(color_image_copy, 'up', (_table.x-120, _table.y-50),
                                                     Color.black)
                    color_image_copy = util.put_text(color_image_copy, str(_table.dist)[:5], (int(_table.x), int(_table.y) + 50),
                                                                                      Color.black)

                color_image_copy = cv2.circle(color_image_copy, _table.center, _table.radius,
                                              (0, 255, 0), 2)
                color_image_copy = util.put_text(color_image_copy, str(_table.center_float), _table.center, Color.red)

            thresh = cv2.applyColorMap(cv2.convertScaleAbs(thresh), cv2.COLORMAP_BONE)
            images = np.hstack((color_image_copy, thresh))
            images = cv2.resize(images, (1280, 480))
            cv2.imshow(window_name, images)

            if k == ord('q'):
                break
            if k == ord('i'):
                if len(tables) == 3:
                    print('Please input real distance')
                    dists = input().split(' ')
                    unders.append([dists[0], tables[0].x])
                    middles.append([dists[1], tables[1].x])
                    ups.append([dists[2], tables[2].x])
                else:
                    print('too few tables')
            if k == ord('s'):
                tdatetime = dt.now()
                tstr = tdatetime.strftime('%m-%d-%H:%M:%S')
                # underのファイルパス確認
                if os.path.isfile(Path.under_front):
                    os.rename(Path.under_front, Path.under_front+tstr+'.csv')
                # middleのファイルパス確認
                if os.path.isfile(Path.middle_front):
                    os.rename(Path.middle_front, Path.middle_front+tstr+'.csv')
                # upのファイルパス確認
                if os.path.isfile(Path.up_front):
                    os.rename(Path.up_front, Path.up_front+tstr+'.csv')

                # underのcsv書き込み
                f = open(Path.under_front, 'w')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerows(unders)
                f.close()

                # middleのcsv書き込み
                f = open(Path.middle_front, 'w')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerows(middles)
                f.close()

                # upのcsv書き込み
                f = open(Path.up_front, 'w')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerows(ups)
                f.close()
                print('All Stored!')

            if k == ord('1'):
                tdatetime = dt.now()
                tstr = tdatetime.strftime('%m-%d-%H:%M:%S')
                # underのファイルパス確認
                if os.path.isfile(Path.under_front):
                    os.rename(Path.under_front, Path.under_front+tstr+'.csv')
                # underのcsv書き込み
                f = open(Path.under_front, 'w')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerows(unders)
                f.close()
                print('Under Stored!')

            if k == ord('2'):
                tdatetime = dt.now()
                tstr = tdatetime.strftime('%m-%d-%H:%M:%S')
                # middleのファイルパス確認
                if os.path.isfile(Path.middle_front):
                    os.rename(Path.middle_front, Path.middle_front+tstr+'.csv')
                # middleのcsv書き込み
                f = open(Path.middle_front, 'w')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerows(middles)
                f.close()
                print('Middle Stored!')

            if k == ord('3'):
                tdatetime = dt.now()
                tstr = tdatetime.strftime('%m-%d-%H:%M:%S')
                # upのファイルパス確認
                if os.path.isfile(Path.up_front):
                    os.rename(Path.up_front, Path.up_front+tstr+'.csv')
                # upのcsv書き込み
                f = open(Path.up_front, 'w')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerows(ups)
                f.close()
                print('Up Stored!')


        except Exception as error:
            if str(error) == "wait_for_frames cannot be called before start()":
                pipeline.stop()
                exit()
            elif str(error) == "Frame didn't arrived within 5000":
                pipeline.stop()
                exit()
            else:
                print(error)
except:
    pass
finally:
    pipeline.stop()
