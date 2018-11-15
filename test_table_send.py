import cv2
import numpy as np
from realsense.view import FieldView
from path_planning import PathPlanning

def f(x):
    return x - 1250

planner = PathPlanning(send=True)
size = 720, 1280, 3
v = FieldView()
window_name = 'main'
cv2.namedWindow(window_name)

pos1, pos2, pos3, zone = 3750, 3750, 3750, 1
move_table_pos = (pos1, pos2, pos3)
points, flip_points = planner.main((pos1, pos2, pos3, zone))
planner.send(points, flip_points)

v.zone = zone
img = v.draw_field(move_table_pos, points)
img = cv2.resize(img, (int(1280 * 0.65), int(720 * 0.65)))
cv2.imshow(window_name, img)
k = cv2.waitKey(0)