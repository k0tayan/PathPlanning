import pyrealsense2 as rs
import coloredlogs, logging
import numpy as np
import os
import cv2
import time
import sys

from realsense import *
from path_planning import PathPlanning

path = os.path.dirname(os.path.abspath(__file__))

send = True
width = Config.width
height = Config.height
mode = Config.mode
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
pipeline.start(config)
util = Utils()
table_set = Tables()
func = ApproximationFunction()
plan = PathPlanning(send=send)
timer = time.time()
detection = True
sc = 1
cd_start = sys.maxsize
view_mode = 0 # 0=thresh 1=path 2=standing_detection
result = [None, None, None]
auto_change = True
result_image = None
standing_detection = True

window_name = 'PathPlanning'
path_window_name = 'Path'
bar_window_name = 'setting'
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.moveWindow(window_name, 450, 0, )
cv2.namedWindow(bar_window_name, cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('H', bar_window_name, 0, 255, util.nothing)
cv2.createTrackbar('S', bar_window_name, 0, 255, util.nothing)
cv2.createTrackbar('V', bar_window_name, 0, 255, util.nothing)
cv2.createTrackbar('LV', bar_window_name, 0, 255, util.nothing)
cv2.createTrackbar('threshold', bar_window_name, 0, 255, util.nothing)
cv2.createTrackbar('kernel', bar_window_name, 0, 100, util.nothing)
cv2.createTrackbar('horizon', bar_window_name, 0, height, util.nothing)
cv2.createTrackbar('vertical', bar_window_name, 0, width, util.nothing)
cv2.createTrackbar('remove_side', bar_window_name, 0, 30, util.nothing)
cv2.createTrackbar('zone', bar_window_name, 0, 1, util.nothing)

cv2.setTrackbarPos('H', bar_window_name, util.settings['h'])
cv2.setTrackbarPos('S', bar_window_name, util.settings['s'])
cv2.setTrackbarPos('V', bar_window_name, util.settings['v'])
cv2.setTrackbarPos('LV', bar_window_name, util.settings['lv'])
cv2.setTrackbarPos('threshold', bar_window_name, util.settings['th'])
cv2.setTrackbarPos('kernel', bar_window_name, util.settings['k'])
cv2.setTrackbarPos('remove_side', bar_window_name, util.settings['rms'])
cv2.setTrackbarPos('zone', bar_window_name, Config.zone)
logging.info('START DETECTION')

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
            h = cv2.getTrackbarPos('H', bar_window_name)
            s = cv2.getTrackbarPos('S', bar_window_name)
            v = cv2.getTrackbarPos('V', bar_window_name)
            lv = cv2.getTrackbarPos('LV', bar_window_name)
            th = cv2.getTrackbarPos('threshold', bar_window_name)
            kn = cv2.getTrackbarPos('kernel', bar_window_name)
            horizon = cv2.getTrackbarPos('horizon', bar_window_name)
            vertical = cv2.getTrackbarPos('vertical', bar_window_name)
            remove_side = cv2.getTrackbarPos('remove_side', bar_window_name)
            Config.zone = cv2.getTrackbarPos('zone', bar_window_name)

            # スライダーの値から白色の上限値、下限値を指定
            upper_white = np.array([h, s, v])
            lower_white = np.array([0, 0, lv])

            # 画面に描画するようにcolor_imageをコピーした変数を作成
            color_image_copy = color_image

            # 画像保存用にcolor_imageをコピーした変数を作成
            color_image_for_save = color_image.copy()

            # チェック用
            for_check = color_image.copy()

            # 横の消すやつ
            if Config.zone:
                pts = np.array([[0, 0], [remove_side * 10, 0], [0, height]])
                color_image = cv2.fillPoly(color_image, pts=[pts], color=Color.red)
            else:
                pts = np.array([[remove_side * 50, 0], [width, 0], [width, height]])
                color_image = cv2.fillPoly(color_image, pts=[pts], color=Color.blue)

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

            # テーブルの検出が終了していたら
            if not detection:
                util.put_info_by_set(color_image_copy, table_set, Color.black)
                result_image = util.put_standing_detection_result(color_image_copy, table_set, result)
                # 画像収集
                if k == ord('r'):
                    logging.info(f'STORED:{sc}')
                    util.save_table_images(color_image_for_save, table_set, 20)
                    sc += 1

                # ペットボトルが立っているかの検出
                if standing_detection:
                    if not util.processing_standing_detection:
                        util.check_standing(for_check, table_set)
                        table_set.under.standing = None
                        table_set.middle.standing = None
                        table_set.up.standing = None

                    if table_set.up.standing is not None:
                        util.processing_standing_detection = False
                        result = [table_set.under.standing, table_set.middle.standing, table_set.up.standing]
                        # util.log_standing(table_set)
                        # 立っていたらTrue、立っていなかったらFalse
                        plan.set_result(table_set.under.standing, table_set.middle.standing,
                                     table_set.up.standing)

                # テーブル検出モード
                if k == ord('b'):
                    detection = True

                # 3秒おきに送信
                if time.time() - timer > 3:
                    ret = util.make_distance_send(table_set)
                    plan.main([ret.under, ret.middle, ret.up, Config.zone])
                    timer = time.time()

                    if auto_change:
                        view_mode += 1
                        if view_mode > 2:
                            view_mode = 0

            # テーブル検出
            if detection:
                util.processing_standing_detection = False
                thresh[:horizon, :] = 0
                # thresh[:, 1165:] = 0
                # thresh[336:, 1000:] = 0

                white_indexes = list(np.where(thresh > 150))

                for white_index in zip(white_indexes[0], white_indexes[1]):
                    dist = np_image[white_index[0]][white_index[1]]
                    if not Config.zone:
                        if (white_index[1], white_index[0]) > (1000, 300) and dist > 2750 + white_index[0]:
                            thresh[white_index[0]][white_index[1]] = 0
                            color_image_copy[white_index[0]][white_index[1]] = [255, 0, 0]
                    else:
                        if (white_index[1] < 300 and white_index[0] > 300)  and dist > 2700 + white_index[0]:
                            thresh[white_index[0]][white_index[1]] = 0
                            color_image_copy[white_index[0]][white_index[1]] = [255, 0, 0]

                # 縮小と膨張
                kernel = np.ones((kn + 2, kn + 2), np.uint8)
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

                # Y座標が小さい順にソート
                tables.sort(key=util.return_center_y)

                if len(tables) == 3:
                    try:
                        rtype = table_set.update(tables[0], tables[1], tables[2])
                        # under tableを描画
                        color_image_copy = util.put_info(color_image_copy, table_set.under)
                        # middle tableを描画
                        color_image_copy = util.put_info(color_image_copy, table_set.middle)
                        # up tableを描画
                        color_image_copy = util.put_info(color_image_copy, table_set.up)

                        if time.time() - timer > 3:
                            ret = util.make_distance_send(table_set)
                            plan.main([ret.under, ret.middle, ret.up, Config.zone])
                            timer = time.time()

                            if auto_change:
                                view_mode += 1
                                if view_mode > 2:
                                    view_mode = 0

                        if k == ord('n'):
                            detection = False
                            logging.info('END DETECTION')

                        if k == 32:  # SPACE
                            cd_start = time.time()

                        if time.time() - cd_start > Config.seconds:
                            detection = False
                            logging.info('END DETECTION')

                    except Exception as error:
                        logging.error(error)

            # 画面枠
            if Config.zone:
                color_image_copy = cv2.rectangle(color_image_copy, (0, 0), (width, height), Color.red, 20)
            else:
                color_image_copy = cv2.rectangle(color_image_copy, (0, 0), (width, height), Color.blue, 20)

            # 二値をカラーに
            thresh = cv2.applyColorMap(cv2.convertScaleAbs(thresh), cv2.COLORMAP_BONE)

            if view_mode == 0:
                # 見せるウインドウには経路を表示
                path_view = cv2.imread("output/tmp.png")
                back = np.full((720, 1280, 3), 255, dtype=np.uint8)
                path_view = cv2.resize(path_view, (1210, 720))
                back[0:720, 70:1280] = path_view
                images = np.hstack((color_image_copy, back))
            elif view_mode == 1:
                path_view = cv2.imread("output/tmp.png")
                back = np.full((720, 1280, 3), 255, dtype=np.uint8)
                path_view = cv2.resize(path_view, (1210, 720))
                back[0:720, 70:1280] = path_view
                images = np.hstack((color_image_copy, back))
            elif view_mode == 2:
                if result_image is not None:
                    images = np.hstack((color_image_copy, result_image))
                else:
                    images = np.hstack((color_image_copy, thresh))
            else:
                images = np.hstack((color_image_copy, thresh))

            # threshウインドウのみthreshを表示
            images_for_thresh = np.hstack((color_image_copy, thresh))
            # ウインドウサイズがでかくなりすぎるので、縮小
            images = cv2.resize(images, (int(1280 * 0.65), int(480 * 0.65)))
            images_for_thresh = cv2.resize(images_for_thresh, (int(1280 * 0.65), int(480 * 0.65)))
            # 表示
            cv2.imshow(window_name, images)
            cv2.imshow(bar_window_name, images_for_thresh)

            # 終了
            if k == ord('q'):
                logging.info('QUIT DETECTION')
                break
            # パラメータの保存
            if k == ord('s'):
                logging.info('SAVED PARAMETER')
                util.save_param(h, s, v, lv, th, kn, remove_side)

            if k == ord('c'):
                view_mode += 1
                if view_mode > 2:
                    view_mode = 0

            if k == ord('o'):
                auto_change = not auto_change

        except Exception as error:
            if str(error) == "wait_for_frames cannot be called before start()":
                pipeline.stop()
                exit()
            elif str(error) == "Frame didn't arrived within 5000":
                pipeline.stop()
                exit()
            else:
                logging.error(error)
except:
    pass
finally:
    pipeline.stop()
