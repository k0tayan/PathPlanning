import socket
import struct
from .objects import Point, LEFT, RIGHT, FRONT

class Tcp:
    def __init__(self, host='192.168.11.3', port=10001):
        self.host = host
        self.port = port

    def connect(self):
        self._socket = socket.socket()
        self._socket.settimeout(1)
        try:
            self._socket.connect((self.host, self.port))
        except Exception as error:
            raise Exception('Cant\'t connect to host\n' + str(error))

    def send(self, packet):
        self._socket.send(packet)
        self._socket.close()

    def server(self):
        self.clientsock = None
        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversock.bind((self.host, self.port))
        self.serversock.listen(10)
        self.clientsock, client_address = self.serversock.accept()

    def receive(self):
        rcvmsg = self.clientsock.recv(1)
        return rcvmsg

    def create_packet(self, points, flip_points, retry=False):
        send_points = points.copy()
        for i in range(8 - len(send_points)):
            send_points.append(Point(0, 0))
        points_x = [point.x for point in send_points]
        points_y = [point.y for point in send_points]
        x_l = list(map(int, points_x))
        y_l = list(map(int, points_y))
        if not retry:
            x_l[0] = 0 # とらないようにするために、0, 0にしている
            y_l[0] = 0

        buf = []
        buf.append(0)
        for x in x_l:
            buf.append(x >> 7)
            buf.append(x & 0x7f)
        for y in y_l:
            buf.append(y >> 7)
            buf.append(y & 0x7f)

        for i, flip_point in enumerate(flip_points):
            data = 0
            data += flip_point[0] << 2
            if flip_point[1] == LEFT:
                data += 0x00
            elif flip_point[1] == RIGHT:
                data += 0x01
            elif flip_point[1] == FRONT:
                data += 0x02
            data += 0x20
            buf.append(data)

        for i in range(4 - len(flip_points)):
            buf.append(0)
        buf[0] = (sum(buf[1:]) & 0x7f) | 0x80
        # for i, tmp in enumerate(buf):
        #    print(f"[{i}]", bin(tmp))
        p = struct.pack('B' * len(buf), *buf)
        return p
