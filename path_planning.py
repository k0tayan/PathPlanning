import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random
from bottleflip.objects import Robot, Field, Table, Path, Point
from tcp.Tcp import Tcp

random_move = True
send = False
zone = 'red'
robot_width = 1200
two_stage_table_red_zone_x, two_stage_table_red_zone_y = 3000, 3500
two_stage_table_blue_zone_x, two_stage_table_blue_zone_y = 2000, 3500
two_stage_table_width = 800
move_table_width = 500
field_width, field_height = 5000, 8500
move_table_randomize_area_min, move_table_randomize_area_max = 1250, 3750

def main(count=0):
    # plot setting
    plt.figure()
    ax = plt.axes()
    plt.axis("equal")
    plt.grid(True)
    plt.xticks(list(range(0, field_width+1, 1000)))
    plt.yticks(list(range(0, field_height+1, 1000)))
    ax.set_xlim(0, field_width)
    ax.set_ylim(0, field_height)

    # create instance
    robot = Robot(robot_width)
    field = Field(field_width, field_height)
    if random_move:
        table_under = Table(random.randint(move_table_randomize_area_min, move_table_randomize_area_max+1), 5500, move_table_width, robot_width)
        table_middle = Table(random.randint(move_table_randomize_area_min, move_table_randomize_area_max+1), 6500, move_table_width, robot_width)
        table_up = Table(random.randint(move_table_randomize_area_min, move_table_randomize_area_max+1), 7500, move_table_width, robot_width)
        print(table_under.x, table_middle.x, table_up.x)
    else:
        table_under = Table(2500, 5500, move_table_width, robot_width)
        table_middle = Table(2500, 6500, move_table_width, robot_width)
        table_up = Table(2500, 7500, move_table_width, robot_width)
    if zone == 'red':
        two_stage_table = Table(two_stage_table_red_zone_x, two_stage_table_red_zone_y, two_stage_table_width, robot_width)
        two_stage_table.set_goal('LEFT')
    else: # zone == 'blue
        two_stage_table = Table(two_stage_table_blue_zone_x, two_stage_table_blue_zone_y, two_stage_table_width, robot_width)
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
            tcp = Tcp()
            tcp.connect()
            tcp.send(send_points, flip_points)
    except Exception as error:
        print(error)
    points_x = [point.x for point in points]
    points_y = [point.y for point in points]
    tmp = [(point.x, point.y) for point in send_points]
    # tmp2 = [(point.x, point.y) for point in send_points]
    print(tmp)
    print(path.get_flip_point())

    # plot
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
    if count != 0:
         plt.savefig(f'output/figure{count}.png')
    plt.show()


if __name__ == '__main__':
    main(0)

