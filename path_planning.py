import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random
from bottleflip.objects import Robot, Field, Table, Path, Point
from bottleflip import config
from tcp.Tcp import Tcp
import sys
import socket
import struct

random_move = False
send = False
zone = 'red'

def main(arg):
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
        print(table_under.x, table_middle.x, table_up.x)
    else:
        table_under = Table(arg[0], 5500, config.move_table_width, config.robot_width, ax)
        table_middle = Table(arg[1], 6500, config.move_table_width, config.robot_width, ax)
        table_up = Table(arg[2], 7500, config.move_table_width, config.robot_width, ax)
        print(table_under.x, table_middle.x, table_up.x)
        global zone
        if arg[3] == 1:
            zone = 'red'
        else:
            zone = 'blue'
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
    try:
        send_points = list(points)
        flip_points = path.get_flip_point()
        for i in range(8-len(send_points)):
            send_points.append(Point(0, 0))
        if send:
            tcp = Tcp(host='192.168.11.13', port=10001)
            tcp.connect()
            tcp.send(send_points, flip_points)

            status_led = socket.socket()
            status_led.connect(('192.168.11.14', 10001))
            buf = [0x01]
            packet = struct.pack('B', *buf)
            status_led.send(packet)
    except Exception as error:
        print(error)
        status_led = socket.socket()
        status_led.connect(('192.168.11.14', 10001))
        buf = [0x02]
        packet = struct.pack('B', *buf)
        status_led.send(packet)
    points_x = [point.x for point in points]
    points_y = [point.y for point in points]
    tmp = [(point.x, point.y) for point in send_points]
    # tmp2 = [(point.x, point.y) for point in send_points]
    print(tmp)
    print(path.get_flip_point())

    # plot
    field.plot()
    two_stage_table.plot()
    table_under.plot()
    table_middle.plot()
    table_up.plot()

    ax.plot(points_x, points_y, '.', color='red')
    ax.plot(points_x, points_y, '-', color='green')
    plt.savefig('output/tmp.png')
    # plt.show()


if __name__ == '__main__':
    if len(sys.argv) == 5 or random_move:
        arg = np.array(sys.argv[1:], dtype=np.float)
        arg = np.array(arg, dtype=np.int)
        # arg = list(map(int, sys.argv[1:]))
        main(arg)
    else:
        random_move = True
        main(sys.argv)

