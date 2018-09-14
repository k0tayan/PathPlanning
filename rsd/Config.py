class Config:
    zone = 0 # zone=1 赤ゾーン zone=0 青ゾーン
    mode = 1 # mode=0: 深度 mode=1 中心座標
    side = 0 # 横からとるか side=1　横から撮る side=0 前から撮る
    use_moving_average = 1 # 中心座標で距離を推定する場合で、移動平均を使うか　使う=1 使わない=0
    red_partition_1 = 0
    red_partition_2 = 0
    blue_partition_1 = 0
    blue_partition_2 = 0
    count = 200 # 移動平均の取る個数
    nud, nmd, nup = 0, 0, 0 # 表示用
    setting_path = '/settings.json'
    radius_filter_side = (100, 20)
    radius_filter_front = (110, 22)


class Path:
    blue_under = '/Users/sho/PycharmProjects/PathPlanning/measurements/blue/under.csv'
    blue_middle = '/Users/sho/PycharmProjects/PathPlanning/measurements/blue/middle.csv'
    blue_up = '/Users/sho/PycharmProjects/PathPlanning/measurements/blue/up.csv'

    red_under = None
    red_middle = None
    red_up = None

    under_front = '/Users/sho/PycharmProjects/PathPlanning/measurements/front/under_front.csv'
    middle_front = '/Users/sho/PycharmProjects/PathPlanning/measurements/front/middle_front.csv'
    up_front = '/Users/sho/PycharmProjects/PathPlanning/measurements/front/up_front.csv'

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
