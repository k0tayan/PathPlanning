import socket
import struct

class Tcp:
    def __init__(self, host='192.168.0.14', port=10001):
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
        self.serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serversock.bind((self.host, self.port))  # IPとPORTを指定してバインドします
        self.serversock.listen(10)
        self.clientsock, client_address = self.serversock.accept()  # 接続されればデータを格納

    def receive(self):
        rcvmsg = self.clientsock.recv(13)
        return rcvmsg

    def create_packet(self, points, flip_points, fail):
        points_x = [point.x for point in points]
        points_y = [point.y for point in points]
        points_x[0] = 0
        points_y[0] = 0
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

        for i, flip_point in enumerate(flip_points):
            data = 0
            data += flip_point[0] << 2
            if flip_point[1] == 'LEFT':
                data += 0x00
            elif flip_point[1] == 'RIGHT':
                data += 0x01
            elif flip_point[1] == 'FRONT':
                data += 0x02
            if i == 1 and fail[0] or i == 2 and fail[1] or i == 3 and fail[2]:
                data += 0x20
            buf.append(data)
        buf[0] = (sum(buf[1:]) & 0x7f) | 0x80
        p = struct.pack('B' * len(buf), *buf)
        return p
