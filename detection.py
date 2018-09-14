import pyrealsense2 as rs
import numpy as np
import os
import cv2

try:
    from rsd.Detection import Table, Utils, Tables, ApproximationFunction
except:
    from .rsd.Detection import Table, Utils, Tables
from rsd.Config import Config, Color

path = os.path.dirname(os.path.abspath(__file__))

if Config.side:
    width = 640
    height = 480
else:
    width = 1280
    height = 720
only_view = False
mode = Config.mode
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
pipeline.start(config)
util = Utils(zone=Config.zone)
table_set = Tables()
func = ApproximationFunction()
t_count = 1
t_list = list(range(1, 30))
t_list += list(range(30, 0, -1))

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

            # blend = np.zeros((480, 640, 3))
            # blend[:, :Config.partition_1, 0] = 90

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


            if Config.side:
                if Config.zone:
                    pass
                else:
                    # 左を捨てる
                    thresh[:, :45] = 0

                    # 下を捨てる
                    thresh[429:, :] = 0

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
                if only_view:
                    color_image_copy = cv2.circle(color_image_copy, center, radius,
                                                  Color.purple, 2)
                dist = depth.get_distance(int(x), int(y))
                table = Table(center, radius, dist, (x, y))
                tables.append(table)

            """# 距離でフィルタ
            tables = list(filter(util.distance_filter, tables))"""

            # 半径でフィルタ
            tables = list(filter(util.radius_filter, tables))

            # 半径が大きい順にソート
            tables.sort(key=util.return_radius, reverse=True)

            # 大きい3つだけを抽出
            tables = tables[:3]

            # X座標が小さい順にソート
            if Config.side:
                tables.sort(key=util.return_center_x)
            else:
                tables.sort(key=util.return_center_y)

            if len(tables) == 3 and not only_view:
                try:
                    rtype = table_set.update(tables[0], tables[1], tables[2])

                    if not rtype & 0x01:
                        # under tableを描画
                        color_image_copy = util.put_info(color_image_copy, table_set.under)

                    if not rtype & 0x02:
                        # middle tableを描画
                        color_image_copy = util.put_info(color_image_copy, table_set.middle)

                    if not rtype & 0x04:
                        # up tableを描画
                        color_image_copy = util.put_info(color_image_copy, table_set.up)

                    if rtype != 0:
                        msg = 'Error:'
                        if rtype & 0x01:
                            msg += ' under'
                        if rtype & 0x02:
                            msg += ' middle'
                        if rtype & 0x04:
                            msg += ' up'
                        util.put_text(color_image_copy, msg, (300, 446), Color.error)
                    else:
                        if k == ord('l'):
                            ret = util.make_distance_send(table_set)
                            os.system(f'./path_planning.sh {ret.under} {ret.middle} {ret.up} {Config.zone}')
                            view_window_name = 'view'
                            view = cv2.imread('output/tmp.png')
                            cv2.namedWindow(view_window_name)
                            cv2.imshow(view_window_name, view)

                    if Config.use_moving_average and Config.side:
                        remaining_times = table_set.get_remaining_times()

                        util.put_text(color_image_copy,
                                f"{str(remaining_times[0])}, {str(remaining_times[1])}, {str(remaining_times[2])}",
                                (10, 40), Color.white)

                except Exception as error:
                    print(error)

            if only_view:
                for i, _table in enumerate(tables):
                    color_image_copy = cv2.circle(color_image_copy, _table.center, _table.radius,
                                                  (0, 255, 0), 2)
                    color_image_copy = util.put_text(color_image_copy, str(_table.center_float), _table.center, Color.red)


            # 画面端で波打つみたいな？
            t_count += 1
            if t_count >= len(t_list)-1:
                t_count = 0
            if Config.zone:
                color_image_copy = cv2.rectangle(color_image_copy, (0, 0), (width, height), Color.red, t_list[t_count])
            else:
                color_image_copy = cv2.rectangle(color_image_copy, (0, 0), (width, height), Color.blue, t_list[t_count])

            if Config.side:
                if Config.zone:
                    pass
                else:
                    # partition_1の描画
                    color_image_copy = cv2.line(color_image_copy, (Config.blue_partition_1, 0),
                                                (Config.blue_partition_1, height), Color.purple, 2)

                    # partition_2の描画
                    color_image_copy = cv2.line(color_image_copy, (Config.blue_partition_2, 0),
                                                (Config.blue_partition_2, height), Color.purple, 2)

            thresh = cv2.applyColorMap(cv2.convertScaleAbs(thresh), cv2.COLORMAP_BONE)
            images = np.hstack((color_image_copy, thresh))
            images = cv2.resize(images, (1280, 480))
            # images = np.hstack((blend, thresh))
            cv2.imshow(window_name, images)

            if k == ord('q'):
                break
            if k == ord('s'):  # パラメータの保存
                util.save_param(h, s, v, lv, th, kn)
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
