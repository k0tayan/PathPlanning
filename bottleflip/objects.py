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