import pyrealsense2 as rs
import numpy as np
import os
import cv2
import time

try:
    from rsd.detection import Table, Utils, Tables, ApproximationFunction
except:
    from .rsd.detection import Table, Utils, Tables
from rsd.config import Config, Color
from path_planning import PathPlanning

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
plan = PathPlanning(True)
t_count = 1
t_list = list(range(1, 30))
t_list += list(range(30, 0, -1))
timer = time.time()
save = True
detection = True
sc = 1

window_name = 'image'
cv2.namedWindow(window_name)
cv2.moveWindow(window_name, 450, 0, )
cv2.createTrackbar('H', window_name, 0, 255, util.nothing)
cv2.createTrackbar('S', window_name, 0, 255, util.nothing)
cv2.createTrackbar('V', window_name, 0, 255, util.nothing)
cv2.createTrackbar('LV', window_name, 0, 255, util.nothing)
cv2.createTrackbar('threshold', window_name, 0, 255, util.nothing)
cv2.createTrackbar('kernel', window_name, 0, 100, util.nothing)
cv2.createTrackbar('horizon', window_name, 0, height, util.nothing)
cv2.createTrackbar('vertical', window_name, 0, width, util.nothing)
cv2.createTrackbar('remove_side', window_name, 0, 30, util.nothing)
cv2.createTrackbar('zone', window_name, 0, 1, util.nothing)

cv2.setTrackbarPos('H', window_name, util.settings['h'])
cv2.setTrackbarPos('S', window_name, util.settings['s'])
cv2.setTrackbarPos('V', window_name, util.settings['v'])
cv2.setTrackbarPos('LV', window_name, util.settings['lv'])
cv2.setTrackbarPos('threshold', window_name, util.settings['th'])
cv2.setTrackbarPos('kernel', window_name, util.settings['k'])
cv2.setTrackbarPos('remove_side', window_name, util.settings['rms'])
cv2.setTrackbarPos('zone', window_name, Config.zone)
print('---------------START DETECTION---------------')

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
            horizon = cv2.getTrackbarPos('horizon', window_name)
            vertical = cv2.getTrackbarPos('vertical', window_name)
            remove_side = cv2.getTrackbarPos('remove_side', window_name)
            Config.zone = cv2.getTrackbarPos('zone', window_name)

            # スライダーの値から白色の上限値、下限値を指定
            upper_white = np.array([h, s, v])
            lower_white = np.array([0, 0, lv])

            # 画面に描画するようにcolor_imageをコピーした変数を作成
            color_image_copy = color_image

            # 画像保存用にcolor_imageをコピーした変数を作成
            color_image_for_save = color_image.copy()

            pts = np.array([[remove_side * 50, 0], [width, 0], [width, height]])
            if Config.zone:
                color_image_copy = cv2.fillPoly(color_image_copy, pts=[pts], color=Color.red)
            else:
                color_image_copy = cv2.fillPoly(color_image_copy, pts=[pts], color=Color.blue)

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

            if not detection:
                util.put_info_by_set(color_image_copy, table_set, Color.black)
                if k == ord('r'):
                    print(f'---------------STORED:{sc}---------------')
                    util.save_table_images(color_image_for_save, table_set, 20)
                    sc += 1
                """if time.time() - timer > 3:
                    ret = util.make_distance_send(table_set)
                    plan.main([ret.under, ret.middle, ret.up, Config.zone])
                    os.system("imgcat output/tmp.png")
                    timer = time.time()"""
                if k == ord('d'):
                    start = time.time()
                    print('--------START STANDING DETECTION---------')
                    ret = util.is_table_standing(color_image_for_save, table_set)
                    if ret[0]:
                        print('under:standing')
                    else:
                        print('under:falling down')
                    if ret[1]:
                        print('middle:standing')
                    else:
                        print('middle:falling down')
                    if ret[2]:
                        print('up:standing')
                    else:
                        print('up:falling down')
                    print(f'--------END[{time.time()-start}]-----------')
                    plan.set_fail(not ret[0], not ret[1], not ret[2])

                if k == ord('b'):
                    detection = True

            if detection:
                if Config.side:
                    if Config.zone:
                        pass
                    else:
                        # 左を捨てる
                        thresh[:, :45] = 0

                        # 下を捨てる
                        thresh[429:, :] = 0
                else:
                    thresh[:horizon, :] = 0
                    # thresh[:, 1165:] = 0
                    # thresh[336:, 1000:] = 0

                white_indexes = list(np.where(thresh > 150))

                for white_index in zip(white_indexes[0], white_indexes[1]):
                    dist = np_image[white_index[0]][white_index[1]]
                    if (white_index[1], white_index[0]) > (1000, 300) and dist > 2800 + white_index[0]:
                        thresh[white_index[0]][white_index[1]] = 0
                        color_image_copy[white_index[0]][white_index[1]] = [255, 0, 0]

                # 縮小と膨張
                kernel = np.ones((kn+2, kn+2), np.uint8)
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
                    if only_view:
                        color_image_copy = cv2.circle(color_image_copy, center, radius,
                                                      Color.purple, 2)
                    dist = depth.get_distance(int(x), int(y))
                    table = Table(center, radius, dist, (x, y))
                    tables.append(table)


                # 距離でフィルタ
                # tables = list(filter(util.distance_filter, tables))

                # tables = list(filter(util.is_table, tables))

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
                            if time.time() - timer > 3:
                                ret = util.make_distance_send(table_set)
                                plan.main([ret.under, ret.middle, ret.up, Config.zone])
                                os.system("imgcat output/tmp.png")
                                timer = time.time()

                        if Config.use_moving_average and Config.side:
                            remaining_times = table_set.get_remaining_times()

                            util.put_text(color_image_copy,
                                    f"{str(remaining_times[0])}, {str(remaining_times[1])}, {str(remaining_times[2])}",
                                    (10, 40), Color.white)

                        if not Config.side:
                            if k == ord('n'):
                                detection = False
                                print('---------------END DETECTION---------------')

                    except Exception as error:
                        print(error)

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
            if not Config.side:
                images = cv2.resize(images, (int(1280*0.65), int(480*0.65)))
            cv2.imshow(window_name, images)

            if k == ord('q'):
                break
            if k == ord('s'):  # パラメータの保存
                util.save_param(h, s, v, lv, th, kn, remove_side)
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
