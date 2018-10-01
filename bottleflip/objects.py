import numpy as np
import matplotlib

LEFT = 'LEFT'
RIGHT = 'RIGHT'
FRONT = 'FRONT'

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Robot:
    def __init__(self, width):
        self.width = width
        self.radius = width/2 * np.sqrt(2)


class Rect:
    def __init__(self, x, y, width):
        self.lupx = x - width / 2
        self.lupy = y + width / 2
        self.ludx = x - width / 2
        self.ludy = y - width / 2
        self.rudx = x + width / 2
        self.rudy = y - width / 2
        self.rupx = x + width / 2
        self.rupy = y + width / 2

        self.x_list = [self.lupx, self.ludx, self.rudx, self.rupx]
        self.y_list = [self.lupy, self.ludy, self.rudy, self.rupy]


class Table(Rect, Point):
    def __init__(self, x, y, width, robot_width, ax):
        super().__init__(x, y, width)
        self.x = x
        self.y = y
        self.width = width
        self.left_goal: Point = Point(x - width / 2 - robot_width / 2, y)
        self.right_goal: Point = Point(x + width / 2 + robot_width / 2, y)
        self.front_goal: Point = Point(x, y - width / 2 - robot_width / 2)
        self.ax = ax
        self.goal: Point = None
        self.goal_state: str = None

    def plot(self):
        if self.ax is None:
            raise Exception('Please set matplotlib ax')
        self.ax.plot(self.x, self.y, '.', color='black')
        self.ax.plot(self.x_list + [self.lupx], self.y_list + [self.lupy], '-', color='blue')

    def set_goal(self, direction):
        """

        :param direction: LEFT, RIGHT, RIGHT
        :return:
        """
        if direction == LEFT:
            self.goal = self.left_goal
            self.goal_state = LEFT
        elif direction == RIGHT:
            self.goal = self.right_goal
            self.goal_state = RIGHT
        elif direction == RIGHT:
            self.goal = self.front_goal
            self.goal_state = RIGHT
        else:
            raise Exception('Please set valid direction.')


class Field:
    def __init__(self, width, height, ax):
        self.width = width
        self.height = height
        self.ax = ax

    def plot(self):
        if self.ax is None:
            raise Exception('Please set matplotlib ax')
        self.ax.plot([0, 0], [0, self.height], '-', color='black')
        self.ax.plot([self.width, self.width], [0, self.height], '-', color='black')
        self.ax.plot([self.width / 2, self.width / 2], [0, self.height], linestyle="dotted")


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
        if zone == 'red':
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
                    self.set_goal(LEFT, RIGHT, LEFT)
                else:
                    self.set_goal(LEFT, RIGHT, RIGHT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        self.set_goal(RIGHT, RIGHT, LEFT)
                    else:
                        self.set_goal_by_zone(zone)
                else:
                    self.set_goal_by_zone(zone)
        elif self.table_under.x >= self.table_middle.x >= self.table_up.x:
            if abs(self.table_under.x - self.table_middle.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                self.set_goal(LEFT, RIGHT, RIGHT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    self.set_goal_by_zone(zone)
                else:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        self.set_goal(LEFT, LEFT, RIGHT)
                    else:
                        self.set_goal_by_zone(zone)
        elif self.table_under.x <= self.table_middle.x and self.table_middle.x >= self.table_up.x:
            if abs(self.table_under.x - self.table_middle.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                    self.set_goal(RIGHT, LEFT, RIGHT)
                else:
                    self.set_goal(RIGHT, LEFT, LEFT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    self.set_goal_by_zone(zone)
                else:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        self.set_goal(LEFT, LEFT, RIGHT)
                    else:
                        self.set_goal_by_zone(zone)
        elif self.table_under.x <= self.table_middle.x <= self.table_up.x:
            if abs(self.table_under.x - self.table_middle.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                self.set_goal(RIGHT, LEFT, LEFT)
            else:
                if (self.table_under.x + self.table_middle.x) / 2 < 2500:
                    if abs(self.table_middle.x - self.table_up.x) > 2 * (self.move_table_width / 2) + self.robot.width:
                        self.set_goal(RIGHT, RIGHT, LEFT)
                    else:
                        self.set_goal_by_zone(zone)
                else:
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

    def make_mid_point(self, _table1: Table, _table2: Table) -> Point:
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
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == RIGHT and table2.goal_state == RIGHT:
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == RIGHT and table2.goal_state == RIGHT:
                return Point(table2.goal.x, table1.goal.y)
            else:
                raise Exception('kotayan is foolish! More think!')
        else:
            if table1.goal_state == LEFT and table2.goal_state == LEFT:
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == LEFT and table2.goal_state == RIGHT:
                return Point(table2.goal.x, table1.goal.y)
            elif table1.goal_state == RIGHT and table2.goal_state == RIGHT:
                return Point(table1.goal.x, table2.goal.y)
            elif table1.goal_state == LEFT and table2.goal_state == RIGHT:
                return Point(table2.goal.x, table1.goal.y)
            else:
                raise Exception('kotayan is foolish! More think!')

    def make_path(self):
        self.flip_points = []
        flip_point_index = 0
        path = []
        path.append(self.two_stage_table.goal)
        self.flip_points.append((flip_point_index, self.two_stage_table.goal_state))
        flip_point_index += 1
        if self.zone == 'red' and self.table_under.goal.x < self.two_stage_table.goal.x:
            path.append(Point(self.table_under.goal.x, 4500))
            flip_point_index += 1
            self.flip_points.append((flip_point_index, self.table_under.goal_state))
        elif self.zone == 'blue' and self.table_under.goal.x > self.two_stage_table.goal.x:
            path.append(Point(self.table_under.goal.x, 4500))
            flip_point_index += 1
            self.flip_points.append((flip_point_index, self.table_under.goal_state))
        else:
            path.append(Point(self.two_stage_table.goal.x, 4500))
            path.append(Point(self.table_under.goal.x, 4500))
            flip_point_index += 2
            self.flip_points.append((flip_point_index, self.table_under.goal_state))
        path.append(self.table_under.goal)
        flip_point_index += 1
        mid = self.make_mid_point(self.table_under, self.table_middle)
        if self.compare_points(mid, self.table_under.goal):
            flip_point_index += 0
        else:
            path.append(mid)
            flip_point_index += 1
        path.append(self.table_middle.goal)
        self.flip_points.append((flip_point_index, self.table_middle.goal_state))
        flip_point_index += 1
        mid = self.make_mid_point(self.table_middle, self.table_up)
        if self.compare_points(mid, self.table_middle.goal):
            flip_point_index += 0
        else:
            path.append(mid)
            flip_point_index += 1
        path.append(self.table_up.goal)
        self.flip_points.append((flip_point_index, self.table_up.goal_state))
        return path

    def path_planning(self):
        self.make_flip_point2(self.zone)
        points_1 = self.make_path()
        distance_1 = self.get_distance(points_1)

        self.make_simple_flip_points(self.zone)
        points_2 = self.make_path()
        distance_2 = self.get_distance(points_2)
        print(f"simplified:{distance_2}")
        if distance_1 < distance_2:
            return points_1
        else:
            return points_2

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
