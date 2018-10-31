import os
class Config:
    zone = 0  # zone=1 赤ゾーン zone=0 青ゾーン
    mode = 1  # mode=0: 深度 mode=1 中心座標
    side = 0  # 横からとるか side=1　横から撮る side=0 前から撮る
    use_moving_average = 1  # 中心座標で距離を推定する場合で、移動平均を使うか　使う=1 使わない=0
    setting_path = '/settings.json'
    radius_filter_side = (20, 100)
    radius_filter_front = (22, 110)
    distance_filter_front = (2.4, 5.3)
    custom_vision = True
    width = 1280
    height = 720
    seconds = 10
    send = False
    use_standing_detection = False
    use_realsense = False


class Path:
    dir = os.getcwd()

    under_front = dir + '/measurements/front/under_front.csv'
    middle_front = dir + '/measurements/front/middle_front.csv'
    up_front = dir + '/measurements/front/up_front.csv'

    field_max_right = dir + '/measurements/front/field_max_right.csv'

    keras_green_model = dir + '/realsense/sd/green_model2.h5'

    red_field_image = dir + '/table_images/red.png'
    blue_field_image = dir + '/table_images/blue.png'


class Field:
    FIELD_WIDTH = 5000
    TABLE_WIDTH = 500


class Color:
    blue = (255, 167, 38)
    red = (38, 81, 255)
    purple = (158, 77, 132)
    white = (255, 255, 255)
    error = (255, 75, 0)
    black = (0, 0, 0)
    green = (156, 100, 71)
    light_green = ((0, 252, 124))
