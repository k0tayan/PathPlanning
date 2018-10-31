import numpy as np
import matplotlib.pyplot as plt
import random
from bottleflip import *
import sys
import coloredlogs, logging
import threading
import cv2

coloredlogs.install()
random_move = False
zone = 'red'


class PathPlanning:
    def __init__(self, send=True):
        self.send = send
        # 立っていたらTrue、立っていなかったらFalse
        self.result = [False, False, False]
        self.log = True
        self.tcp = None

        self.error = False

    def send_packet(self, packet):
        try:
            self.tcp.connect()
            self.tcp.send(packet)
            logging.info("send:success")
        except Exception as error:
            logging.error(str(error))

    def fix(self, coord):
        if coord < 1250:
             return 1250
        elif coord > 3750:
            return 3750
        else:
            return coord

    def main(self, arg, show=False):
        self.error = False
        # plot setting
        plt.figure()
        ax = plt.axes()
        plt.axis("equal")
        plt.grid(True)
        plt.xticks(list(range(0, config.field_width + 1, 1000)))
        plt.yticks(list(range(0, config.field_height + 1, 1000)))
        ax.set_xlim(0, config.field_width)
        ax.set_ylim(0, config.field_height)

        # create instance
        robot = Robot(config.robot_width)
        field = Field(config.field_width, config.field_height, ax)
        if random_move:
            table_under = Table(
                random.randint(config.move_table_randomize_area_min, config.move_table_randomize_area_max), config.move_table_under_y,
                config.move_table_width, config.robot_width, ax)
            table_middle = Table(
                random.randint(config.move_table_randomize_area_min, config.move_table_randomize_area_max), config.move_table_middle_y,
                config.move_table_width, config.robot_width, ax)
            table_up = Table(
                random.randint(config.move_table_randomize_area_min, config.move_table_randomize_area_max), config.move_table_up_y,
                config.move_table_width, config.robot_width, ax)
        else:
            under, middle, up, arg_zone = arg
            under = self.fix(under)
            middle = self.fix(middle)
            up = self.fix(up)
            table_under = Table(under, config.move_table_under_y, config.move_table_width, config.robot_width, ax)
            table_middle = Table(middle, config.move_table_middle_y, config.move_table_width, config.robot_width, ax)
            table_up = Table(up, config.move_table_up_y, config.move_table_width, config.robot_width, ax)
            global zone
            if arg_zone == 1:
                zone = 'red'
            else:
                zone = 'blue'
        logging.info(f'\nunder:{table_under.x} middle:{table_middle.x} up:{table_up.x}')
        if zone == 'red':
            two_stage_table = Table(config.two_stage_table_red_zone_x, config.two_stage_table_red_zone_y,
                                    config.two_stage_table_width, config.robot_width, ax)
            two_stage_table.set_goal('LEFT')
        else:  # zone == 'blue
            two_stage_table = Table(config.two_stage_table_blue_zone_x, config.two_stage_table_blue_zone_y,
                                    config.two_stage_table_width, config.robot_width, ax)
            two_stage_table.set_goal('RIGHT')
        path = Path(field=field,
                    robot=robot,
                    two_stage_table=two_stage_table,
                    table_under=table_under,
                    table_middle=table_middle,
                    table_up=table_up,
                    zone=zone)

        # path planning
        points = path.path_planning()
        send_points = list(points)
        flip_points = path.get_flip_point()
        for i in range(8 - len(send_points)):
            send_points.append(Point(0, 0))
        if self.send:
            try:
                self.tcp = Tcp(host='192.168.0.14', port=10001)
                packet = self.tcp.create_packet(send_points, flip_points, self.result)
                thread = threading.Thread(target=self.send_packet, args=(packet,), daemon=True)
                thread.start()
            except Exception as error:
                logging.error(str(error))
                self.error = True
        points_x = [point.x for point in points]
        points_y = [point.y for point in points]

        # plot
        field.plot()
        two_stage_table.plot()
        table_under.plot()
        table_middle.plot()
        table_up.plot()

        ax.plot(points_x, points_y, '.', color='red')
        ax.plot(points_x, points_y, '-', color='green')
        try:
            plt.savefig('output/tmp.png')
        except:
            pass
        if self.log:
            logging.info("path_planning start")
            print(f"移動距離:{path.get_distance(points)}mm")
            p = list(map(str, points))
            logging.info(f"points:{p}")
            logging.info(f"flip_points:{path.get_flip_point()}")
            logging.info("path_planning end")
        self.log = False
        if show:
            plt.show()
        plt.close()

        return points, flip_points, self.error

    def set_result(self, under, middle, up):
        self.result = [under, middle, up]

    def set_result_by_list(self, result):
        self.result = result


if __name__ == '__main__':
    plan = PathPlanning(True)
    if len(sys.argv) == 5 or random_move:
        arg = np.array(sys.argv[1:], dtype=np.float)
        arg = np.array(arg, dtype=np.int)
        # arg = list(map(int, sys.argv[1:]))
        plan.main(arg, True)
    else:
        random_move = True
        plan.main(sys.argv, True)
