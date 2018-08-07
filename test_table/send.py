import socket
import struct

cl = socket.socket()
cl.connect(('localhost',4000))
b = struct.pack("iii", 2500, 1200, 2600)
cl.send(b)
b = struct.pack("iii", 2510, 1200, 2600)
cl.send(b)
b = struct.pack("iii", 3500, 1200, 2600)
cl.send(b)
cl.close()
