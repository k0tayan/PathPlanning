from operator import attrgetter
import coloredlogs, logging
import numpy as np
import cv2
import time

from realsense import *
import pyrealsense2 as rs
from path_planning import PathPlanning
from yukari.player import Yukari

window_name = 'PathPlanning'
path_window_name = 'Path'
bar_window_name = window_name + '-setting'
field_window_name = 'Field'
timer = 0  # 初期化
sc = 1
coloredlogs.install()


class App(Parameter, Utils, FieldView, Draw, ):
    def __init__(self):
        super(Parameter, self).__init__()
        super(Utils, self).__init__()
        super(FieldView, self).__init__()
        super(Draw, self).__init__()
        if self.use_realsense:
            self.pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, 30)
            config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, 30)
            self.pipeline.start(config)
        else:
            self.capture = cv2.VideoCapture(0)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # カメラ画像の横幅を1280に設定
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # カメラ画像の縦幅を720に設定
        self.table_set = Tables()
        self.planner = PathPlanning(send=self.send)
        self.table_detection = True
        self.detection_success = False
        self.view_mode = 0  # 0=thresh 1=path 2=standing_detection
        self.bottle_result = [None, None, None]
        self.auto_change = True
        self.standing_result_image = None
        self.quit = False
        self.yukari = Yukari()
        self.remove_separator_middle = False
        self.points = None
        self.flip_points = None

        self.set_track_bar_pos(self.settings)
        logging.info('START DETECTION')

    def get_param(self):
        # スライダーの値を取得
        self.h = cv2.getTrackbarPos('H', bar_window_name)
        self.s = cv2.getTrackbarPos('S', bar_window_name)
        self.v = cv2.getTrackbarPos('V', bar_window_name)
        self.lv = cv2.getTrackbarPos('LV', bar_window_name)
        self.th = cv2.getTrackbarPos('threshold', bar_window_name)
        self.kn = cv2.getTrackbarPos('kernel', bar_window_name)
        self.remove_side = cv2.getTrackbarPos('remove_side', bar_window_name)
        self.remove_side_e = cv2.getTrackbarPos('remove_side_e', bar_window_name)
        self.zone = cv2.getTrackbarPos('zone', bar_window_name)

    def get_data_from_realsense(self) -> (np.asanyarray, np.asanyarray):
        # realsenseから深度と画像データを取得
        frames = self.pipeline.wait_for_frames()
        depth = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())

        depth_data = depth.as_frame().get_data()
        np_depth = np.asanyarray(depth_data)
        return color_image, np_depth

    def get_data_from_webcam(self) -> (np.asanyarray, None):
        # ウェブカメラから画像データを取得
        ret, frame = self.capture.read()
        # frame = cv2.flip(frame, -1)
        return frame, None

    def get_data(self):
        if self.use_realsense:
            return self.get_data_from_realsense()
        else:
            return self.get_data_from_webcam()

    def remove_separator(self, color_image):
        # セパレータ消すやつ
        if self.zone:
            if self.remove_separator_middle:
                x = self.height
                y = -(self.remove_side * 20)
                y_x = y / x
                f = lambda a: int(y_x * a - y)

                pts = np.array([[0, 0], [self.remove_side * 20, 0], [f(self.remove_side_e), self.remove_side_e],
                                [0, self.remove_side_e]])
                cv2.fillPoly(color_image, pts=[pts], color=Color.red)

                pts = np.array([[0, self.remove_side_e + 150], [f(self.remove_side_e + 150), self.remove_side_e + 150],
                                [0, self.height]])
                cv2.fillPoly(color_image, pts=[pts], color=Color.red)
            else:
                pts = np.array([[0, 0], [self.remove_side * 20, 0], [0, self.height]])
                cv2.fillPoly(color_image, pts=[pts], color=Color.red)
        else:
            if self.remove_separator_middle:
                x = self.height
                y = -(self.width - self.remove_side * 50)
                y_x = y / x
                f = lambda a: self.width - int(y_x * a - y)

                pts = np.array([[self.remove_side * 50, 0], [f(self.remove_side_e), self.remove_side_e],
                                [self.width, self.remove_side_e], [self.width, 0]])
                cv2.fillPoly(color_image, pts=[pts], color=Color.blue)

                pts = np.array(
                    [[f(self.remove_side_e + 150), self.remove_side_e + 150], [self.width, self.remove_side_e + 150],
                     [self.width, self.height]])
                cv2.fillPoly(color_image, pts=[pts], color=Color.blue)
            else:
                pts = np.array([[self.remove_side * 50, 0], [self.width, 0], [self.width, self.height]])
                cv2.fillPoly(color_image, pts=[pts], color=Color.blue)

    def draw(self, color_image_for_show, thresh):
        # 画面描画
        # 画面枠
        if self.zone:
            cv2.rectangle(color_image_for_show, (0, 0), (self.width, self.height), Color.red, 20)
        else:
            cv2.rectangle(color_image_for_show, (0, 0), (self.width, self.height), Color.blue, 20)

        if self.detection_success:
            # under tableを描画
            color_image_for_show = self.put_info(color_image_for_show, self.table_set.under)
            # middle tableを描画
            color_image_for_show = self.put_info(color_image_for_show, self.table_set.middle)
            # up tableを描画
            color_image_for_show = self.put_info(color_image_for_show, self.table_set.up)

        # 二値をカラーに
        thresh = cv2.applyColorMap(cv2.convertScaleAbs(thresh), cv2.COLORMAP_BONE)
        # threshウインドウのみthreshを表示
        images_for_thresh = np.hstack((color_image_for_show, thresh))

        if self.table_detection:
            color_image_for_show = np.hstack((color_image_for_show, thresh))
        else:
            # 立っているかの判定情報を描画
            self.put_info_by_set(color_image_for_show, self.table_set, Color.black)
            self.standing_result_image = self.put_standing_detection_result(color_image_for_show, self.table_set,
                                                                            self.bottle_result)

            if self.standing_result_image is not None:
                color_image_for_show = np.hstack((color_image_for_show, self.standing_result_image))
            else:
                color_image_for_show = np.hstack((color_image_for_show, thresh))

        # ウインドウサイズがでかくなりすぎるので、縮小
        color_image_for_show = cv2.resize(color_image_for_show, (int(1280 * 0.65), int(480 * 0.65)))
        images_for_thresh = cv2.resize(images_for_thresh, (int(1280 * 0.65), int(480 * 0.65)))

        # 表示
        # cv2.imshow(window_name, color_image_for_show)
        cv2.imshow(bar_window_name, images_for_thresh)

    def analyze(self):
        # スライダーの値を取得
        self.get_param()

        # データを取得
        color_image, np_depth = self.get_data()

        # 画面に描画するようにcolor_imageをコピーした変数を作成
        color_image_for_show = color_image.copy()

        # 画像保存用にcolor_imageをコピーした変数を作成
        self.color_image_for_save = color_image.copy()

        # チェック用
        for_check = color_image.copy()

        # フィールドを分ける白いやつを消す
        self.remove_separator(color_image)
        self.remove_separator(color_image_for_show)

        # ブラーをかける
        color_image = cv2.medianBlur(color_image, 5)
        # hsv空間に変換
        hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

        # スライダーの値から白色の上限値、下限値を指定
        upper_white = np.array([self.h, self.s, self.v])
        lower_white = np.array([0, 0, self.lv])

        # 白色でマスク
        mask_white = cv2.inRange(hsv, lower_white, upper_white)
        # 同じ部分だけ抽出
        res_white = cv2.bitwise_and(color_image, color_image, mask=mask_white)
        # グレースケールに変換
        gray = cv2.cvtColor(res_white, cv2.COLOR_RGB2GRAY)
        # 二値化
        ret, thresh = cv2.threshold(gray, self.th, 255, cv2.THRESH_BINARY)

        # 縮小と膨張
        kernel = np.ones((self.kn, self.kn), np.uint8)
        erode = cv2.erode(thresh, kernel)
        thresh = cv2.dilate(erode, kernel)

        # テーブルの検出処理
        if self.table_detection:
            # ペットボトル判定処理から戻ってきたときのためにFalseにする
            self.processing_standing_detection = False

            self.points, self.flip_points = None, None

            # 輪郭抽出
            imgEdge, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # 見つかった輪郭をリストに入れる
            tables = []  # テーブルの可能性がある輪郭をここに入れる
            contours.sort(key=cv2.contourArea, reverse=True)
            for cnt in contours:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                table = Table(center, radius, 0, (x, y))
                if table.is_table():  # 本当にテーブルかチェック
                    tables.append(table)  # テーブルだったらリストに追加

            # 半径が大きい順にソート
            tables = sorted(tables, reverse=True)

            # 大きい3つだけを抽出
            tables = tables[:3]

            # Y座標が小さい順にソート
            tables = sorted(tables, key=attrgetter('y'))

            # 3つ見つかったら
            self.detection_success = (len(tables) == 3)  # Trueが成功
            if self.detection_success:
                self.table_set.update(tables[0], tables[1], tables[2])

        # 検出処理が終わっていたら
        else:
            # ペットボトルが立っているかの検出
            if self.use_standing_detection:
                self.put_info_by_set(color_image_for_show, self.table_set, Color.black)
                self.put_standing_detection_result(color_image_for_show, self.table_set, self.bottle_result)
                if not self.processing_standing_detection:
                    self.check_standing(for_check, self.table_set)
                    # self.table_set.reset_standing_result()

                if not np.all(self.table_set.result is None):
                    play_result = []
                    if self.bottle_result[0] != self.table_set.result[0]:
                        play_result.append([0, self.table_set.result[0]])
                    if self.bottle_result[1] != self.table_set.result[1]:
                        play_result.append([1, self.table_set.result[1]])
                    if self.bottle_result[2] != self.table_set.result[2]:
                        play_result.append([2, self.table_set.result[2]])
                    if play_result:
                        self.yukari.play_results(play_result)
                    self.bottle_result = self.table_set.result
                    # 立っていたらTrue、立っていなかったらFalse
                    self.planner.set_result_by_list(self.bottle_result)

        if self.detection_success and not self.table_detection:
            global timer
            if time.time() - timer > 3:  # 3秒に1回実行
                # 画面内の座標を送信する座標に変換
                ret = self.make_distance_to_send(self.table_set)
                # 経路計画
                if self.points is None:
                    self.points, self.flip_points = self.planner.main([ret.under, ret.middle, ret.up, self.zone])
                self.planner.send(self.points, self.flip_points)
                # フィールド描画
                field_view = self.draw_field((ret.under, ret.middle, ret.up), self.points)
                cv2.imshow(field_window_name, field_view)
                self.yukari.play_finish_path_planning()
                timer = time.time()

        # 描画
        self.draw(color_image_for_show, thresh)

    def key_check(self):
        # キーの入力
        key = cv2.waitKey(1)

        # ペットボトル判定シーケンスに移行
        if key == ord('n') and self.table_detection and self.detection_success:
            # todo ゆかりさんボイス
            # self.yukari.play_move_to_check_standing_sequence()
            self.table_detection = False
            logging.info('END DETECTION')

        # テーブル検出シーケンスに移行
        if key == ord('b') and not self.table_detection:
            self.yukari.play_detecting_table()
            self.table_detection = True

        # 画像収集
        if key == ord('r') and not self.table_detection:
            global sc
            logging.info(f'STORED:{sc}')
            self.save_table_images(image=self.color_image_for_save, table_set=self.table_set, x_offset=20, y_offset=20)
            sc += 1

        # 終了
        if key == ord('q'):
            logging.info('QUIT DETECTION')
            self.quit = True

        # パラメータの保存
        if key == ord('s'):
            logging.info('SAVED PARAMETER')
            self.save_param(self.h, self.s, self.v, self.lv, self.th, self.kn, self.remove_side)

        # 自動画面切り替えフラグを切り替え
        if key == ord('o'):
            self.auto_change = not self.auto_change

        if key == ord('e'):
            self.remove_separator_middle = not self.remove_separator_middle

    def run(self):
        try:
            while True:
                try:
                    # 画像認識
                    self.analyze()

                    # キーボードの入力
                    self.key_check()

                    if self.quit:
                        break

                except Exception as error:
                    if str(error) == "wait_for_frames cannot be called before start()":
                        if self.use_realsense:
                            self.pipeline.stop()
                            exit()
                    elif str(error) == "Frame didn't arrived within 5000":
                        if self.use_realsense:
                            self.pipeline.stop()
                            exit()
                    else:
                        logging.error(error)
        except:
            pass
        finally:
            if self.use_realsense:
                self.pipeline.stop()


if __name__ == '__main__':
    app = App()
    app.run()
