import socket
import struct
from bottleflip.objects import Point

"""
[0] checksum | 0x80
[1] x[0] >> 7
[2] x[0] & 0x7f
[3] x[1] >> 7
[4] x[2] & 0x7f
.
.
.
[17] y[0] >> 7
[18] y[0] & 0x7f
[19] y[1] >> 7
[20] y[2] & 0x7f
.
.
.
[32] y[8] & 0x7f
[33] flippoint1 0b0iiiixx iiii=index xx=dir
[34] flippoint2 0b0iiiixx iiii=index xx=dir
[35] flippoint3 0b0iiiixx iiii=index xx=dir
[36] flippoint4 0b0iiiixx iiii=index xx=dir

0 <= index <= 7
xx:
'LEFT':00
'RIGHT':01
'FRONT':11
"""

class Tcp:
    def __init__(self, host='192.168.11.13', port=10001):
        self.host = host
        self.port = port

    def connect(self):
        self._socket = socket.socket()
        self._socket.settimeout(3)
        try:
            self._socket.connect((self.host, self.port))
        except Exception as error:
            raise Exception('Cant\'t connect to host\n' + str(error))

    def send(self, _points, _flip_points):
        points = _points
        flip_points = _flip_points
        points_x = [point.x for point in points]
        points_y = [point.y for point in points]
        x_l = list(map(int, points_x))
        y_l = list(map(int, points_y))

        buf = []
        buf.append(0)
        for x in x_l:
            buf.append(x >> 7)
            buf.append(x & 0x7f)
        for y in y_l:
            buf.append(y >> 7)
            buf.append(y & 0x7f)

        for flip_point in flip_points:
            data = 0
            data += flip_point[0] << 2
            if flip_point[1] == 'LEFT':
                data += 0
            elif flip_point[1] == 'RIGHT':
                data += 1
            elif flip_point[1] == 'FRONT':
                data += 2
            buf.append(data)
        buf[0] = (sum(buf[1:]) & 0x7f) | 0x80
        # for i, b in enumerate(buf):
           #  print("data[{0}]: 0b{1}".format(i, format(b, 'b').zfill(8)))
        print("check_sum:{0}, sum:{1}".format(buf[0] & 0x7f, sum(buf[1:]) & 0x7f))
        print(buf)
        p = struct.pack('B' * len(buf), *buf)
        self._socket.send(p)

    def server(self):
        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversock.bind(('localhost', 4000))  # IPとPORTを指定してバインドします
        self.serversock.listen(10)
        self.clientsock, client_address = self.serversock.accept()  # 接続されればデータを格納

    def receive(self):
        rcvmsg = self.clientsock.recv(13)
        return rcvmsg