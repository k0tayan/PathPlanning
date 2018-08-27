import pyrealsense2 as rs
import numpy as np
import os
import cv2

try:
    from rsd.Detection import Table, Utils, Tables
except:
    from rsd.Detection import Table, Utils, Tables

path = os.path.dirname(os.path.abspath(__file__))

width = 640
height = 480
zone = 'red'
# width = 1280
# height = 720
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
pipeline.start(config)
lower_white = np.array([0, 0, 100])
util = Utils(zone=zone)
table_set = Tables()


def putText(img, text, pos, color):
    cv2.putText(img, text, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)


window_name = 'image'
cv2.namedWindow(window_name)
cv2.moveWindow(window_name, 0, 0)
cv2.createTrackbar('H', window_name, 0, 255, util.nothing)
cv2.createTrackbar('S', window_name, 0, 255, util.nothing)
cv2.createTrackbar('V', window_name, 0, 255, util.nothing)
cv2.createTrackbar('threshold', window_name, 0, 255, util.nothing)
cv2.createTrackbar('kernel', window_name, 0, 30, util.nothing)

cv2.setTrackbarPos('H', window_name, util.settings['h'])
cv2.setTrackbarPos('S', window_name, util.settings['s'])
cv2.setTrackbarPos('V', window_name, util.settings['v'])
cv2.setTrackbarPos('threshold', window_name, util.settings['th'])
cv2.setTrackbarPos('kernel', window_name, util.settings['k'])

try:
    while True:
        try:
            # 　深度と画像データを取得
            frames = pipeline.wait_for_frames()
            depth = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())

            # キーの入力待ち
            k = cv2.waitKey(1)

            # スライダーの値を取得
            h = cv2.getTrackbarPos('H', window_name)
            s = cv2.getTrackbarPos('S', window_name)
            v = cv2.getTrackbarPos('V', window_name)
            th = cv2.getTrackbarPos('threshold', window_name)
            kn = cv2.getTrackbarPos('kernel', window_name)

            # スライダーの値から白色の上限値を指定
            upper_white = np.array([h, s, v])

            # 画面に描画するようにcolor_imageをコピーした変数を作成
            # color_image = cv2.resize(color_image, (640, 360))
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

            # 各座標について遠すぎるやつは黒で埋める
            # for y in range(480):
            #    for x in range(640):
            #        dist = depth.get_distance(x, y)
            #        if 6.7 < dist:
            #            thresh[y][x] = 0
            # print(thresh)

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
            tables.sort(key=util.return_center)

            if len(tables) == 3:
                try:
                    table_set.update(tables[0], tables[1], tables[2])

                    # under tableを描画
                    color_image_copy = cv2.circle(color_image_copy, table_set.under.center, table_set.under.radius,
                                                  (0, 255, 0), 2)
                    color_image_copy = cv2.circle(color_image_copy, table_set.under.center, 3, (0, 255, 0), 2)
                    putText(color_image_copy, str(table_set.under.dist), table_set.under.center, (255, 255, 0))
                    putText(color_image_copy, str(table_set.under.type),
                            (lambda l: (l[0] - 10, l[1] - 50))(list(table_set.under.center)), (255, 51, 255))

                    # middle tableを描画
                    color_image_copy = cv2.circle(color_image_copy, table_set.middle.center, table_set.middle.radius,
                                                  (0, 255, 0), 2)
                    color_image_copy = cv2.circle(color_image_copy, table_set.middle.center, 3, (0, 255, 0), 2)
                    putText(color_image_copy, str(table_set.middle.dist), table_set.middle.center, (255, 255, 0))
                    putText(color_image_copy, str(table_set.middle.type),
                            (lambda l: (l[0] - 10, l[1] - 50))(list(table_set.middle.center)), (255, 51, 255))

                    # under tableを描画
                    color_image_copy = cv2.circle(color_image_copy, table_set.up.center, table_set.up.radius,
                                                  (0, 255, 0), 2)
                    color_image_copy = cv2.circle(color_image_copy, table_set.up.center, 3, (0, 255, 0), 2)
                    putText(color_image_copy, str(table_set.up.dist), table_set.up.center, (255, 255, 0))
                    putText(color_image_copy, str(table_set.up.type),
                            (lambda l: (l[0] - 10, l[1] - 50))(list(table_set.up.center)), (255, 51, 255))

                    remaining_times = table_set.get_remaining_times()

                    putText(color_image_copy,
                            f"{str(remaining_times[0])}, {str(remaining_times[1])}, {str(remaining_times[2])}",
                            (10, 40), (255, 255, 255))

                    if k == ord('w'):  # パラメータの送信
                        if table_set.is_available():
                            ret = util.make_coordinate(tables)
                            if ret:
                                util.send_coordinate(ret)

                except Exception as error:
                    putText(color_image_copy, str(error), (10, 50), (255, 0, 0))
                    print(error)
            else:
                putText(color_image_copy, 'Could not find 3 tables.', (10, 50), (255, 0, 0))

            thresh = cv2.applyColorMap(cv2.convertScaleAbs(thresh), cv2.COLORMAP_BONE)
            images = np.hstack((color_image_copy, thresh))
            cv2.imshow(window_name, images)

            if k == ord('q'):
                break
            if k == ord('s'):  # パラメータの保存
                util.save_param(h, s, v, th, kn)
            if k == ord('l'):
                os.system(f'./path_planning.sh {3500} {2500} {1500} {0}')
                view_window_name = 'view'
                view = cv2.imread('output/tmp.png')
                cv2.namedWindow(view_window_name)
                cv2.imshow(view_window_name, view)
        except Exception as error:
            print(error)
except:
    pass
finally:
    pipeline.stop()
