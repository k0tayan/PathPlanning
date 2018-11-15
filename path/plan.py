import numpy as np
from .objects import *
from .config import *

class FlipPoint:
    def __init__(self, field, robot, table_under, table_middle, table_up):
        self.field: Field = field
        self.robot: Robot = robot
        self.table_under: Table = table_under
        self.table_middle: Table = table_middle
        self.table_up: Table = table_up
        self.move_table_width = self.table_under.width

    def set_right_all(self):
        self.table_under.set_goal(RIGHT)
        self.table_middle.set_goal(RIGHT)
        self.table_up.set_goal(RIGHT)

    def set_left_all(self):
        self.table_under.set_goal(LEFT)
        self.table_middle.set_goal(LEFT)
        self.table_up.set_goal(LEFT)

    def set_goal(self, under_goal, middle_goal, up_goal):
        self.table_under.set_goal(under_goal)
        self.table_middle.set_goal(middle_goal)
        self.table_up.set_goal(up_goal)

    def set_goal_by_zone(self, zone):
        if zone == RED:
            self.set_left_all()
        else:
            self.set_right_all()

    def can_through(self, width):
        return width > self.robot.width + 2 * (self.move_table_width / 2)

    def make_flip_point(self):
        if self.table_under.x < self.field.width / 2:
            if self.table_middle.x < self.field.width / 2:
                if abs(self.table_under.x - self.table_middle.x) < self.robot.width + 2 * (self.move_table_width / 2):
                    if self.table_middle.x + (self.move_table_width / 2 + self.robot.width / 2) < self.table_up.x:
                        print(1)
                        self.set_goal(RIGHT, RIGHT, FRONT)
                    elif self.table_up.x < self.table_middle.x - (self.move_table_width / 2 + self.robot.width / 2):
                        print(2)
                        self.set_goal(LEFT, LEFT, FRONT)
                    else:
                        print(3)
                        self.set_goal(RIGHT, RIGHT, RIGHT)
                else:
                    if self.table_under.x < self.table_middle.x:
                        if self.table_up.x < self.table_middle.x - (self.move_table_width / 2 + self.robot.width / 2):
                            print(4)
                            self.set_goal(RIGHT, LEFT, FRONT)
                        else:
                            print(5)
                            self.set_goal(RIGHT, LEFT, LEFT)
                    else:
                        if self.table_middle.x + (self.move_table_width / 2 + self.robot.width / 2) < self.table_up.x:
                            print(6)
                            self.set_goal(LEFT, RIGHT, FRONT)
                        else:
                            print(7)
                            self.set_goal(LEFT, RIGHT, RIGHT)

            else:
                if abs(self.table_under.x - self.table_middle.x) < self.robot.width + 2 * (self.move_table_width / 2):
                    if self.table_middle.x + (self.move_table_width / 2 + self.robot.width / 2) < self.table_up.x:
                        print(8)
                        self.set_goal(RIGHT, RIGHT, FRONT)
                    elif self.table_up.x < self.table_middle.x - (self.move_table_width / 2 + self.robot.width / 2):
                        print(9)
                        self.set_goal(LEFT, LEFT, FRONT)
                    else:
                        print(10)
                        self.set_goal(RIGHT, RIGHT, RIGHT)
                else:
                    if self.table_up.x < self.table_middle.x - (self.move_table_width / 2 + self.robot.width / 2):
                        print(11)
                        self.set_goal(RIGHT, LEFT, FRONT)
                    else:
                        print(12)
                        self.set_goal(RIGHT, LEFT, LEFT)
        else:
            if self.table_middle.x < self.field.width / 2:
                if abs(self.table_under.x - self.table_middle.x) < self.robot.width + 2 * (self.move_table_width / 2):
                    if self.table_middle.x + (self.move_table_width / 2 + self.robot.width / 2) < self.table_up.x:
                        print(13)
                        self.set_goal(RIGHT, RIGHT, FRONT)
                    elif self.table_up.x < self.table_middle.x - (self.move_table_width / 2 + self.robot.width / 2):
                        print(14)
                        self.set_goal(LEFT, LEFT, FRONT)
                    else:
                        print(15)
                        self.set_goal(LEFT, LEFT, LEFT)

                else:
                    if self.table_middle.x + (self.move_table_width / 2 + self.robot.width / 2) < self.table_up.x:
                        print(16)
                        self.set_goal(LEFT, RIGHT, FRONT)
                    else:
                        print(17)
                        self.set_goal(LEFT, RIGHT, RIGHT)

            else:
                if abs(self.table_under.x - self.table_middle.x) < self.robot.width + 2 * (self.move_table_width / 2):
                    if self.table_middle.x + (self.move_table_width / 2 + self.robot.width / 2) < self.table_up.x:
                        print(18)
                        self.set_goal(RIGHT, RIGHT, FRONT)
                    elif self.table_up.x < self.table_middle.x - (self.move_table_width / 2 + self.robot.width / 2):
                        print(19)
                        self.set_goal(LEFT, LEFT, FRONT)
                    else:
                        print(20)
                        self.set_goal(LEFT, LEFT, LEFT)
                else:
                    if self.table_under.x < self.table_middle.x:
                        if self.table_up.x < self.table_middle.x - (self.move_table_width / 2 + self.robot.width / 2):
                            print(21)
                            self.set_goal(RIGHT, LEFT, FRONT)
                        else:
                            print(22)
                            self.set_goal(RIGHT, LEFT, LEFT)
                    else:

                        if self.table_middle.x + (self.move_table_width / 2 + self.robot.width / 2) < self.table_up.x:
                            print(23)
                            self.set_goal(LEFT, RIGHT, FRONT)
                        else:
                            print(24)
                            self.set_goal(LEFT, RIGHT, RIGHT)

    def make_flip_point2(self, zone):
        if self.table_under.x >= self.table_middle.x and self.table_middle.x <= self.table_up.x:
            if abs(self.table_under.x - self.table_middle.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                    print(1)
                    self.set_goal(LEFT, RIGHT, LEFT)
                else:
                    if abs(self.table_middle.x - self.table_up.x) > self.robot.width / 2 + turn_margin:
                        print(2)
                        self.set_goal(LEFT, RIGHT, FRONT)
                    else:
                        print(3)
                        self.set_goal(LEFT, RIGHT, RIGHT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        print(4)
                        self.set_goal(RIGHT, RIGHT, LEFT)
                    else:
                        if abs(self.table_middle.x - self.table_up.x) > self.robot.width / 2 + turn_margin:
                            print(5)
                            if zone == RED:
                                self.set_goal_by_zone(zone)
                            else:
                                self.set_goal(RIGHT, RIGHT, FRONT)
                        else:
                            print(6)
                            self.set_goal_by_zone(zone)
                else:
                    print(7)
                    self.set_goal_by_zone(zone)
        elif self.table_under.x >= self.table_middle.x >= self.table_up.x:
            if abs(self.table_under.x - self.table_middle.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                self.set_goal(LEFT, RIGHT, RIGHT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    self.set_goal_by_zone(zone)
                else:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        print(9)
                        self.set_goal(LEFT, LEFT, RIGHT)
                    else:
                        print(10)
                        if abs(self.table_middle.x - self.table_up.x) > self.robot.width / 2 + turn_margin:
                            self.set_goal(LEFT, LEFT, FRONT)
                        else:
                            self.set_goal_by_zone(zone)
        elif (self.table_under.x <= self.table_middle.x) and (self.table_middle.x >= self.table_up.x):
            if abs(self.table_under.x - self.table_middle.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                    print(11)
                    self.set_goal(RIGHT, LEFT, RIGHT)
                else:
                    print(12)
                    if abs(self.table_middle.x - self.table_up.x) > self.robot.width / 2 + turn_margin:
                        self.set_goal(RIGHT, LEFT, FRONT)
                    else:
                        self.set_goal(RIGHT, LEFT, LEFT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    print(13)
                    if abs(self.table_middle.x - self.table_up.x) > self.robot.width / 2 + turn_margin:
                        if zone == RED:
                            self.set_goal(LEFT, LEFT, FRONT)
                        else:
                            self.set_goal_by_zone(zone)
                    else:
                        self.set_goal_by_zone(zone)
                else:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        print(14)
                        if zone == RED:
                            self.set_goal(LEFT, LEFT, RIGHT)
                        else:
                            self.set_goal(LEFT, LEFT, RIGHT)
                            # self.set_goal_by_zone(zone)
                    else:
                        print(15)
                        if abs(self.table_middle.x - self.table_up.x) > self.robot.width / 2 + turn_margin:
                            if zone == RED:
                                self.set_goal(LEFT, LEFT, FRONT)
                            else:
                                self.set_goal_by_zone(zone)
                        else:
                            self.set_goal_by_zone(zone)
        elif self.table_under.x <= self.table_middle.x <= self.table_up.x:
            if abs(self.table_under.x - self.table_middle.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                print(16)
                self.set_goal(RIGHT, LEFT, LEFT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        print(17)
                        self.set_goal(RIGHT, RIGHT, LEFT)
                    else:
                        print(18)
                        if abs(self.table_middle.x - self.table_up.x) > self.robot.width / 2 + turn_margin:
                            self.set_goal(RIGHT, RIGHT, FRONT)
                        else:
                            self.set_goal_by_zone(zone)
                else:
                    print(19)
                    self.set_goal_by_zone(zone)
        else:
            raise Exception('おかしいよ')

    def make_simple_flip_points(self, zone):
        self.set_goal_by_zone(zone)


class Path(FlipPoint):
    def __init__(self, field, robot, two_stage_table, table_under, table_middle, table_up, zone):
        super().__init__(field, robot, table_under, table_middle, table_up)
        self.two_stage_table: Table = two_stage_table
        self.zone = zone

    def make_mid_point(self, _table1: Table, _table2: Table):
        table1: Table = _table1
        table2: Table = _table2
        if table1.y > table2.y:
            tmp = table2
            table2 = table1
            table1 = tmp
        if table1.x < table2.x:
            if table1.goal_state == LEFT and table2.goal_state == LEFT:
                return Point(table1.goal.x, table2.goal.y)
            elif table1.goal_state == RIGHT and table2.goal_state == LEFT:
                return None
            elif table1.goal_state == RIGHT and table2.goal_state == RIGHT:
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == RIGHT and table2.goal_state == RIGHT:
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == RIGHT and table2.goal_state == FRONT:
                return None
            else:
                raise Exception('kotayan is foolish! More think!')
        else:
            if table1.goal_state == LEFT and table2.goal_state == LEFT:
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == LEFT and table2.goal_state == RIGHT:
                return None
            elif table1.goal_state == RIGHT and table2.goal_state == RIGHT:
                return Point(table1.goal.x, table2.goal.y)
            elif table1.goal_state == LEFT and table2.goal_state == RIGHT:
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == LEFT and table2.goal_state == FRONT:
                return None
            else:
                raise Exception('kotayan is foolish! More think!')

    def make_path(self):
        self.flip_points = []
        flip_point_index = 0
        path = []
        path.append(self.two_stage_table.goal)
        self.flip_points.append((flip_point_index, self.two_stage_table.goal_state))
        flip_point_index += 1
        if self.zone == RED and self.table_under.goal.x < self.two_stage_table.goal.x:
            path.append(Point(self.table_under.goal.x, 4500))
            flip_point_index += 1
            self.flip_points.append((flip_point_index, self.table_under.goal_state))
        elif self.zone == BLUE and self.table_under.goal.x > self.two_stage_table.goal.x:
            path.append(Point(self.table_under.goal.x, 4700))
            flip_point_index += 1
            self.flip_points.append((flip_point_index, self.table_under.goal_state))
        else:
            if self.zone == BLUE:
                path.append(Point(self.two_stage_table.goal.x, 4700))
                if self.table_under.goal.x <= self.two_stage_table.goal.x and self.table_under.goal_state == RIGHT:
                    flip_point_index += 1
                else:
                    path.append(Point(self.table_under.goal.x, 4700))
                    flip_point_index += 2
            else:
                path.append(Point(self.two_stage_table.goal.x, 4500))
                if self.two_stage_table.goal.x <= self.table_under.goal.x and self.table_under.goal_state == LEFT:
                    flip_point_index += 1
                else:
                    path.append(Point(self.table_under.goal.x, 4500))
                    flip_point_index += 2
            self.flip_points.append((flip_point_index, self.table_under.goal_state))
        path.append(self.table_under.goal)
        flip_point_index += 1
        mid = self.make_mid_point(self.table_under, self.table_middle)
        if mid is None or self.compare_points(mid, self.table_under.goal) or self.compare_points(mid, self.table_middle.goal):
            flip_point_index += 0
        else:
            path.append(mid)
            flip_point_index += 1
        path.append(self.table_middle.goal)
        self.flip_points.append((flip_point_index, self.table_middle.goal_state))
        flip_point_index += 1
        mid = self.make_mid_point(self.table_middle, self.table_up)
        if mid is None or self.compare_points(mid, self.table_middle.goal) or self.compare_points(mid, self.table_up.goal):
            flip_point_index += 0
        else:
            path.append(mid)
            flip_point_index += 1
        path.append(self.table_up.goal)
        self.flip_points.append((flip_point_index, self.table_up.goal_state))
        return path

    def path_planning(self):
        self.make_flip_point2(self.zone)
        points = self.make_path()
        return points

    def retry_path_planning(self, result, start):
        pass

    def get_flip_point(self):
        return self.flip_points

    def get_distance(self, points):
        distance = 0
        size = len(points)
        for i, point in enumerate(points):
            if i == size-1:
                break
            a = np.array([point.x, point.y])
            b = np.array([points[i+1].x, points[i+1].y])
            distance += np.linalg.norm(a - b)
        return distance

    def compare_points(self, point_1, point_2):
        return (point_1.x == point_2.x) and (point_1.y == point_2.y)