import numpy as np
import matplotlib.pyplot as plt
import random
from bottleflip import *
import sys
import coloredlogs, logging
import threading
import cv2

coloredlogs.install()

class PathPlanning:
    def __init__(self, send=True):
        self.use_send = send
        # 立っていたらTrue、立っていなかったらFalse
        self.result = [False, False, False]
        self.log = True
        self.tcp = None

    def send_packet(self, packet):
        try:
            self.tcp.connect()
            self.tcp.send(packet)
            logging.info("send:success")
        except Exception as error:
            logging.error(str(error))

    def send(self, points, flip_points):
        if self.use_send:
            try:
                self.tcp = Tcp(host='192.168.0.14', port=10001)
                packet = self.tcp.create_packet(points, flip_points, self.result)
                thread = threading.Thread(target=self.send_packet, args=(packet,), daemon=True)
                thread.start()
            except Exception as error:
                logging.error(str(error))

    def fix(self, coord):
        if coord < 1250:
             return 1250
        elif coord > 3750:
            return 3750
        else:
            return coord

    def main(self, arg):
        # create instance
        robot = Robot(config.robot_width)
        field = Field(config.field_width, config.field_height)
        under, middle, up, arg_zone = arg
        under = self.fix(under)
        middle = self.fix(middle)
        up = self.fix(up)
        table_under = Table(under, config.move_table_under_y, config.move_table_width, config.robot_width)
        table_middle = Table(middle, config.move_table_middle_y, config.move_table_width, config.robot_width)
        table_up = Table(up, config.move_table_up_y, config.move_table_width, config.robot_width)
        logging.info(f'\nunder:{table_under.x} middle:{table_middle.x} up:{table_up.x}')
        if arg_zone:
            two_stage_table = Table(config.two_stage_table_red_zone_x, config.two_stage_table_red_zone_y,
                                    config.two_stage_table_width, config.robot_width)
            two_stage_table.set_goal('LEFT')
        else:
            two_stage_table = Table(config.two_stage_table_blue_zone_x, config.two_stage_table_blue_zone_y,
                                    config.two_stage_table_width, config.robot_width)
            two_stage_table.set_goal('RIGHT')
        path = Path(field=field,
                    robot=robot,
                    two_stage_table=two_stage_table,
                    table_under=table_under,
                    table_middle=table_middle,
                    table_up=table_up,
                    zone=arg_zone)

        # path planning
        points = path.path_planning()
        flip_points = path.get_flip_point()

        if self.log:
            logging.info("path_planning start")
            print(f"移動距離:{path.get_distance(points)}mm")
            p = list(map(str, points))
            logging.info(f"points:{p}")
            logging.info(f"flip_points:{path.get_flip_point()}")
            logging.info("path_planning end")
        self.log = False

        return points, flip_points

    def set_result(self, under, middle, up):
        self.result = [under, middle, up]

    def set_result_by_list(self, result):
        self.result = result


if __name__ == '__main__':
    plan = PathPlanning(True)
    if len(sys.argv):
        arg = np.array(sys.argv[1:], dtype=np.float)
        arg = np.array(arg, dtype=np.int)
        # arg = list(map(int, sys.argv[1:]))
        plan.main(arg)
    else:
        print('引数がおかしい')
