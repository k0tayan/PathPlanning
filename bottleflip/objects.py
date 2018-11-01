import numpy as np

LEFT = 'LEFT'
RIGHT = 'RIGHT'
FRONT = 'FRONT'

RED = 1
BLUE = 0

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
        self.left_goal: Point = Point(x - width / 2 - robot_width / 2, y)
        self.right_goal: Point = Point(x + width / 2 + robot_width / 2, y)
        self.front_goal: Point = Point(x, y - width / 2 - robot_width / 2)
        self.goal: Point = None
        self.goal_state: str = None

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
        elif direction == FRONT:
            self.goal = self.front_goal
            self.goal_state = FRONT
        else:
            raise Exception('Please set valid direction.')


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height