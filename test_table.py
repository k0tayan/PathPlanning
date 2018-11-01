import cv2
import numpy as np
from path_planning import PathPlanning

planner = PathPlanning(send=False)
size = 720, 1280, 3
pos1, pos2, pos3, zone = 1250, 1250, 3750, 0
move_table_pos = (pos1, pos2, pos3)
points, flip_points = planner.main((pos1, pos2, pos3, zone))
from realsense.view import FieldView

v = FieldView()
img = v.draw_field(move_table_pos, points)
cv2.namedWindow("img", cv2.WINDOW_AUTOSIZE)
cv2.imshow("img", img)
k = cv2.waitKey()
exit()
