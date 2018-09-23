import numpy as np
import matplotlib.pyplot as plt
import random
from bottleflip.objects import Robot, Field, Table, Path, Point
from bottleflip import config
from tcp.Tcp import Tcp
import sys
import coloredlogs, logging

coloredlogs.install()
random_move = False
zone = 'red'

class PathPlanning:
    def __init__(self, send=True):
        self.send = send
    def main(self, arg, show=False):
        logging.info("path_planning start")
        # plot setting
        plt.figure()
        ax = plt.axes()
        plt.axis("equal")
        plt.grid(True)
        plt.xticks(list(range(0, config.field_width+1, 1000)))
        plt.yticks(list(range(0, config.field_height+1, 1000)))
        ax.set_xlim(0, config.field_width)
        ax.set_ylim(0, config.field_height)

        # create instance
        robot = Robot(config.robot_width)
        field = Field(config.field_width, config.field_height, ax)
        if random_move:
            table_under = Table(random.randint(config.move_table_randomize_area_min, config.move_table_randomize_area_max+1), 5500, config.move_table_width, config.robot_width, ax)
            table_middle = Table(random.randint(config.move_table_randomize_area_min, config.move_table_randomize_area_max+1), 6500, config.move_table_width, config.robot_width, ax)
            table_up = Table(random.randint(config.move_table_randomize_area_min, config.move_table_randomize_area_max+1), 7500, config.move_table_width, config.robot_width, ax)
        else:
            table_under = Table(arg[0], 5500, config.move_table_width, config.robot_width, ax)
            table_middle = Table(arg[1], 6500, config.move_table_width, config.robot_width, ax)
            table_up = Table(arg[2], 7500, config.move_table_width, config.robot_width, ax)
            global zone
            if arg[3] == 1:
                zone = 'red'
            else:
                zone = 'blue'
        logging.info(f'\nunder:{(table_under.x, 5500)}\nmiddle:{(table_middle.x, 6500)}\nup:{(table_up.x, 7500)}')
        if zone == 'red':
            two_stage_table = Table(config.two_stage_table_red_zone_x, config.two_stage_table_red_zone_y, config.two_stage_table_width, config.robot_width, ax)
            two_stage_table.set_goal('LEFT')
        else: # zone == 'blue
            two_stage_table = Table(config.two_stage_table_blue_zone_x, config.two_stage_table_blue_zone_y, config.two_stage_table_width, config.robot_width, ax)
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
        print(f"移動距離:{path.get_distance(points)}mm")
        try:
            send_points = list(points)
            flip_points = path.get_flip_point()
            for i in range(8-len(send_points)):
                send_points.append(Point(0, 0))
            if self.send:
                tcp = Tcp(host='192.168.0.14', port=10001)
                tcp.connect()
                tcp.send(send_points, flip_points)
        except Exception as error:
            logging.error(str(error))
        points_x = [point.x for point in points]
        points_y = [point.y for point in points]
        logging.debug(f"flip_points:{path.get_flip_point()}")

        # plot
        field.plot()
        two_stage_table.plot()
        table_under.plot()
        table_middle.plot()
        table_up.plot()

        ax.plot(points_x, points_y, '.', color='red')
        ax.plot(points_x, points_y, '-', color='green')
        plt.savefig('output/tmp.png')
        if show:
            plt.show()
        plt.close()
        logging.info("path_planning end")


if __name__ == '__main__':
    plan = PathPlanning(False)
    if len(sys.argv) == 5 or random_move:
        arg = np.array(sys.argv[1:], dtype=np.float)
        arg = np.array(arg, dtype=np.int)
        # arg = list(map(int, sys.argv[1:]))
        plan.main(arg, True)
    else:
        random_move = True
        plan.main(sys.argv, True)


