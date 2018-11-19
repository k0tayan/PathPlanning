import numpy as np
from path import *
from path.objects import (LEFT, RIGHT, FRONT, UNDER, MIDDLE, UP)
import sys
import coloredlogs, logging
import threading

coloredlogs.install()

class PathPlanning:
    def __init__(self, send=True):
        self.use_send = send
        # 立っていたらTrue、立っていなかったらFalse
        self.result = [None, None, None]
        self.shot = [False, False, False]
        self.log = True
        self.tcp = None
        self.retry_start = False
        self.retry_start_angle = None
        if send:
            self.receive()

    def send_packet(self, packet, use_clientsock=False):
        try:
            if use_clientsock:
                self.serv.clientsock.send(packet)
            else:
                self.tcp.connect()
                self.tcp.send(packet)
            logging.info("send:success")
        except Exception as error:
            logging.error(str(error))

    def send_packet_retry(self, packet):
        try:
            self.serv.clientsock.send(packet)
            logging.info("send:retry success")
        except Exception as error:
            print(error)

    def send(self, points, flip_points, retry):
        if self.use_send:
            try:
                if not retry and self.serv.clientsock is None:
                    self.tcp = Tcp(host='192.168.11.3', port=10001)
                    packet = self.tcp.create_packet(points, flip_points, retry)
                    thread = threading.Thread(target=self.send_packet, args=(packet,), daemon=True)
                    thread.start()
                elif not retry and self.serv.clientsock:
                    self.tcp = Tcp(host='192.168.11.3', port=10001)
                    packet = self.tcp.create_packet(points, flip_points, retry)
                    thread = threading.Thread(target=self.send_packet, args=(packet, True), daemon=True)
                    thread.start()
                elif self.serv.clientsock is None:
                    self.tcp = Tcp(host='192.168.11.3', port=10001)
                    packet = self.tcp.create_packet(points, flip_points, retry)
                    thread = threading.Thread(target=self.send_packet, args=(packet,), daemon=True)
                    thread.start()
                else:
                    packet = self.tcp.create_packet(points, flip_points, retry)
                    thread = threading.Thread(target=self.send_packet_retry, args=(packet,), daemon=True)
                    thread.start()
            except Exception as error:
                logging.error(str(error))

    def __receive(self):
        self.serv = Tcp(host='0.0.0.0', port=10001)
        self.serv.server()
        print('start receive')
        while True:
            msg = self.serv.receive()
            if not msg:
                continue
            else:
                if msg == b'\x01':
                    print("1200で発射")
                    self.shot[UNDER] = True
                elif msg == b'\x02':
                    print("1500で発射")
                    self.shot[MIDDLE] = True
                elif msg == b'\x03':
                    print("1800で発射")
                    self.shot[UP] = True
                    self.retry_start = True
                else:
                    print(msg)
            # self.serv.clientsock.sendall(b'0')
            # print(msg)

    def receive(self):
        thread = threading.Thread(target=self.__receive, daemon=True)
        thread.start()

    def fix(self, coord):
        return (lambda x: 1250 if x < 1250 else (3750 if x > 3750 else x))(coord)

    def create_instance(self, arg):
        # create instance
        robot = Robot(config.robot_width)
        field = Field(config.field_width, config.field_height)
        under, middle, up, arg_zone = arg
        under = self.fix(under)
        middle = self.fix(middle)
        up = self.fix(up)
        table_under = Table(under, config.move_table_under_y, config.move_table_width, config.robot_width)
        table_middle = Table(middle, config.move_table_middle_y, config.move_table_width, config.robot_width)
        table_up = Table(up, config.move_table_up_y, config.move_table_width, config.robot_width)
        logging.info(f'\nunder:{table_under.x} middle:{table_middle.x} up:{table_up.x}')
        if arg_zone:
            two_stage_table = Table(config.two_stage_table_red_zone_x, config.two_stage_table_red_zone_y,
                                    config.two_stage_table_width, config.robot_width)
            two_stage_table.set_goal(LEFT)
        else:
            two_stage_table = Table(config.two_stage_table_blue_zone_x, config.two_stage_table_blue_zone_y,
                                    config.two_stage_table_width, config.robot_width)
            two_stage_table.set_goal(RIGHT)
        path = Path(field=field,
                    robot=robot,
                    two_stage_table=two_stage_table,
                    table_under=table_under,
                    table_middle=table_middle,
                    table_up=table_up,
                    zone=arg_zone)
        return path

    def main(self, arg):
        # create instance
        path = self.create_instance(arg)

        # path planning
        points = path.path_planning()
        flip_points = path.get_flip_point()

        self.retry_start_angle = flip_points[-1][1]

        if self.log:
            logging.info("path_planning start")
            print(f"移動距離:{path.get_distance(points)}mm")
            p = list(map(str, points))
            logging.info(f"points:{p}")
            logging.info(f"flip_points:{path.get_flip_point()}")
            logging.info("path_planning end")
        self.log = False

        return points, flip_points

    def retry(self, arg, results):
        # create instance
        path = self.create_instance(arg)

        # retry path planning
        points = path.retry_path_planning(results, UP, self.retry_start_angle)
        p = list(map(str, points))
        logging.info(f"retry points:{p}")
        retry_flip_points = path.retry_flip_points
        logging.info(f"retry flip_points:{retry_flip_points}")
        return points, retry_flip_points


    def set_result(self, under, middle, up):
        self.result = [under, middle, up]

    def set_result_by_list(self, result):
        self.result = result


if __name__ == '__main__':
    plan = PathPlanning(True)
    if len(sys.argv):
        arg = np.array(sys.argv[1:], dtype=np.float)
        arg = np.array(arg, dtype=np.int)
        # arg = list(map(int, sys.argv[1:]))
        plan.main(arg)
    else:
        print('引数がおかしい')
