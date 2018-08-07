import pyrealsense2 as rs
import cv2
import numpy as np
import socket, struct

w = 640
h = 480

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, w, h, rs.format.z16, 30)
config.enable_stream(rs.stream.color, w, h, rs.format.bgr8, 30)

pipeline.start(config)
lower_white = np.array([0, 0, 100])
upper_white = np.array([180, 45, 255])
th = 210

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


def return_center(a):
    return a.center


def return_radius(a):
    return a.radius


def radius_filter(a):
    return 200 > a.radius > 40


def distance_filter(a):
    return 0.5 < a.dist < 5


def nothing(x):
    pass


def make_coordinate(under, middle, up):
    _x1 = under
    _x2 = middle
    _x3 = up
    _x1 = 2500
    _x2 = 2500
    _x3 = 2500
    return (_x1, _x2, _x3)

def send_coordinate(under, middle, up):
    if is_tcp_available:
        b = struct.pack("iii?", under, middle, up, 1)
        cl.send(b)


cv2.namedWindow('image')
cv2.createTrackbar('H', 'image', 0, 255, nothing)
cv2.createTrackbar('S', 'image', 0, 255, nothing)
cv2.createTrackbar('V', 'image', 0, 255, nothing)
cv2.createTrackbar('threshold', 'image', 0, 255, nothing)

cv2.setTrackbarPos('H', 'image', 180)
cv2.setTrackbarPos('S', 'image', 45)
cv2.setTrackbarPos('V', 'image', 255)
cv2.setTrackbarPos('threshold', 'image', th)

try:
    while True:
        try:
            h = cv2.getTrackbarPos('H', 'image')
            s = cv2.getTrackbarPos('S', 'image')
            v = cv2.getTrackbarPos('V', 'image')
            th = cv2.getTrackbarPos('threshold', 'image')

            upper_white = np.array([h, s, v])

            frames = pipeline.wait_for_frames()
            depth = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            color_image = np.asanyarray(color_frame.get_data())

            color_image = cv2.medianBlur(color_image, 5)
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            res_white = cv2.bitwise_and(color_image, color_image, mask=mask_white)

            # 輪郭抽出
            gray = cv2.cvtColor(res_white, cv2.COLOR_RGB2GRAY)
            ret, thresh = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)
            # for y in range(480):
            #    for x in range(640):
            #        dist = depth.get_distance(x, y)
            #        if 5 < dist:
            #            thresh[y][x] = 0
            # print(thresh)
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
            for table in tables:
                img = cv2.circle(color_image, table.center, table.radius, (0, 255, 0), 2)
                img = cv2.circle(color_image, table.center, 3, (0, 255, 0), 2)
                cv2.putText(img,
                            str(table.dist),
                            table.center,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 255), 2,
                            cv2.LINE_AA)
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
                    x1, x2, x3 = make_coordinate(tables[0], tables[1], tables[2])
                    send_coordinate(x1, x2, x3)
        except Exception as error:
            print(error)
except:
    pass
finally:
    pipeline.stop()
