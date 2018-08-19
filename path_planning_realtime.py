import numpy as np
import matplotlib
from PIL import Image
import matplotlib.pyplot as plt
import random
from bottleflip.objects import Robot, Field, Table, Path, Point, MoveTableCoordinate
from tcp.Tcp import Tcp
import threading, struct, queue
random_move = False
robot_width = 1000
two_stage_table_red_zone_x, two_stage_table_red_zone_y = 3000, 3500
two_stage_table_blue_zone_x, two_stage_table_blue_zone_y = 2000, 3500
two_stage_table_width = 800
move_table_width = 500
field_width, field_height = 5000, 8500
move_table_randomize_area_min, move_table_randomize_area_max = 1250, 3750

queue = queue.Queue()
kizunaai = Image.open("./kizunaai/kizunaai.jpg")
kizunaai_list = np.asarray(kizunaai)

# plot setting
fig = plt.figure()
ax = plt.axes()
plt.imshow(kizunaai_list)
tcp = Tcp('localhost', 4000)


class prosess(threading.Thread):  # マルチスレッド処理
    def run(self):
        while True:
            rcvmsg = tcp.receive()
            if len(rcvmsg) == 13:
                data = struct.unpack('iii?', rcvmsg)
                mt = MoveTableCoordinate(data[0], data[1], data[2], data[3])
                queue.put(mt)

def main(count=0):
    # create instance
    robot = Robot(robot_width)
    field = Field(field_width, field_height)

    plt.pause(0.1)
    # server setup
    tcp.server()
    t1 = prosess()
    t1.daemon = True
    t1.start()

    def __init_plot():
        plt.axis("equal")
        plt.grid(True)
        plt.xticks(list(range(0, field_width + 1, 1000)))
        plt.yticks(list(range(0, field_height + 1, 1000)))
        ax.set_xlim(0, field_width)
        ax.set_ylim(0, field_height)
        field.set_ax(ax)
        table_under.set_ax(ax)
        table_middle.set_ax(ax)
        table_up.set_ax(ax)
        two_stage_table.set_ax(ax)
        field.plot()
        two_stage_table.plot()
        table_under.plot()
        table_middle.plot()
        table_up.plot()

        ax.plot(points_x, points_y, '.', color='red')
        ax.plot(points_x, points_y, '-', color='green')

    while True:
        if queue.qsize() == 0:
            plt.pause(0.01)
            continue
        mt = queue.get()
        ax.clear()
        table_under = Table(mt.under, 5500, move_table_width, robot_width)
        table_middle = Table(mt.middle, 6500, move_table_width, robot_width)
        table_up = Table(mt.up, 7500, move_table_width, robot_width)
        if mt.zone: # zone == 'red'
            two_stage_table = Table(two_stage_table_red_zone_x, two_stage_table_red_zone_y, two_stage_table_width, robot_width)
            two_stage_table.set_goal('LEFT')
            zone = 'red'
        else: # zone == 'blue
            two_stage_table = Table(two_stage_table_blue_zone_x, two_stage_table_blue_zone_y, two_stage_table_width, robot_width)
            two_stage_table.set_goal('RIGHT')
            zone = 'blue'
        path = Path(field=field,
                    robot=robot,
                    two_stage_table=two_stage_table,
                    table_under=table_under,
                    table_middle=table_middle,
                    table_up=table_up,
                    zone=zone)

        # path planning
        points = path.path_planning()
        try:
            send_points = list(points)
            flip_points = path.get_flip_point()
            for i in range(8-len(send_points)):
                print(i)
                send_points.append(Point(0, 0))
            #to_xport = Tcp()
            #to_xport.connect()
            #to_xport.send(send_points, flip_points)
        except Exception as error:
            print(error)
        points_x = [point.x for point in points]
        points_y = [point.y for point in points]
        tmp = [(point.x, point.y) for point in points]
        # tmp2 = [(point.x, qpoint.y) for point in send_points]
        print(tmp)
        print(path.get_flip_point())

        # plot
        __init_plot()
        plt.pause(0.01)

if __name__ == '__main__':
    main()

