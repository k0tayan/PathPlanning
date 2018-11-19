import cv2
import numpy as np
from realsense.view import FieldView
from path_planning import PathPlanning

def f(x):
    return x - 1250

planner = PathPlanning(send=False)
size = 720, 1280, 3
v = FieldView()
window_name = 'main'
cv2.namedWindow(window_name)
cv2.createTrackbar('table_1', window_name, f(1250), f(3750), int)
cv2.createTrackbar('table_2', window_name, f(1250), f(3750), int)
cv2.createTrackbar('table_3', window_name, f(1250), f(3750), int)
cv2.createTrackbar('table1_result', window_name, 0, 1, int)
cv2.createTrackbar('table2_result', window_name, 0, 1, int)
cv2.createTrackbar('table3_result', window_name, 0, 1, int)
cv2.createTrackbar('zone', window_name, 0, 1, int)
cv2.setTrackbarPos('table_1', window_name, f(2500))
cv2.setTrackbarPos('table_2', window_name, f(2500))
cv2.setTrackbarPos('table_3', window_name, f(2500))


while True:
    pos1 = cv2.getTrackbarPos('table_1', window_name) + 1250
    pos2 = cv2.getTrackbarPos('table_2', window_name) + 1250
    pos3 = cv2.getTrackbarPos('table_3', window_name) + 1250
    results = [
        cv2.getTrackbarPos('table1_result', window_name),
        cv2.getTrackbarPos('table2_result', window_name),
        cv2.getTrackbarPos('table3_result', window_name)
    ]
    zone = cv2.getTrackbarPos('zone', window_name)
    move_table_pos = (pos1, pos2, pos3)
    v.zone = zone
    points, flip_points = planner.main((pos1, pos2, pos3, zone))
    retry_points, retry_flip_points = planner.retry((pos1, pos2, pos3, zone), results)
    img = v.draw_retry(move_table_pos, points, retry_points, results)
    img = cv2.resize(img, (int(1280 * 0.65), int(720 * 0.65)))
    cv2.imshow(window_name, img)
    k = cv2.waitKey(1)

    if k == ord('q'):
        break