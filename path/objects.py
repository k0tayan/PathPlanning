import numpy as np

LEFT = 'LEFT'
RIGHT = 'RIGHT'
FRONT = 'FRONT'

RED = 1
BLUE = 0

UNDER = 0
MIDDLE = 1
UP = 2

X_MIN = 400
X_MAX = 4600

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return f"{self.x}, {self.y}"


class Robot:
    def __init__(self, width):
        self.width = width
        self.radius = width/2 * np.sqrt(2)


class Table(Point):
    def __init__(self, x, y, width, robot_width):
        super().__init__(x, y)
        self.width = width
        self.left_goal: Point = Point(self.fix(x - width / 2 - robot_width / 2), y)
        self.right_goal: Point = Point(self.fix(x + width / 2 + robot_width / 2), y)
        self.front_goal: Point = Point(x, y - width / 2 - robot_width / 2)
        self.goal: Point = None
        self.goal_state: str = None

    def fix(self, coord):
        if coord < X_MIN:
            return X_MIN
        elif coord > X_MAX:
            return X_MAX
        else:
            return coord

    def set_goal(self, direction):
        """

        :param direction: LEFT, RIGHT, FRONT
        :return:
        """
        if direction == LEFT:
            self.goal = self.left_goal
            self.goal_state = LEFT
        elif direction == RIGHT:
            self.goal = self.right_goal
            self.goal_state = RIGHT
        elif direction == FRONT:
            self.goal = self.front_goal
            self.goal_state = FRONT
        else:
            raise Exception('Please set valid direction.')


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.red_start_zone = Point(700, 700)
        self.blue_start_zone = Point(4400, 700)