import sys
from PyQt5.QtWidgets import (QWidget, QSlider,
    QApplication, QPushButton)
from PyQt5.QtCore import Qt
import socket
import struct


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.under = 2500
        self.middle = 2500
        self.up = 2500
        self.zone = True
        self.init_socket()
        self.init_ui()

    def init_socket(self):
        self.cl = socket.socket()
        self.cl.connect(('localhost', 4000))

    def init_ui(self):

        # 水平方向のスライダー作成
        sld = QSlider(Qt.Horizontal, self)
        sld2 = QSlider(Qt.Horizontal, self)
        sld3 = QSlider(Qt.Horizontal, self)
        # スライダーがフォーカスされないようにする
        sld.setFocusPolicy(Qt.NoFocus)
        sld.setGeometry(30, 40, 100, 30)
        sld2.setFocusPolicy(Qt.NoFocus)
        sld2.setGeometry(30, 80, 100, 30)
        sld3.setFocusPolicy(Qt.NoFocus)
        sld3.setGeometry(30, 120, 100, 30)

        sld.setValue(50)
        sld2.setValue(50)
        sld3.setValue(50)
        # スライダーが動くとchangeValue関数が呼び出される
        sld.valueChanged[int].connect(self.change_value)
        sld2.valueChanged[int].connect(self.change_value2)
        sld3.valueChanged[int].connect(self.change_value3)

        self.button = QPushButton('Send', self)
        self.button.setGeometry(50, 150, 40, 40)
        self.button.clicked.connect(self.send)

        self.button2 = QPushButton('Zone', self)
        self.button2.setGeometry(50, 180, 40, 40)
        self.button2.clicked.connect(self.change_zone)
        self.button2.setStyleSheet('background-color: red')

        self.send()

        self.setWindowTitle('QSlider')
        self.show()

    def change_value(self, value):
        self.up = 30*value + 1000

    def change_value2(self, value):
        self.middle = 30*value + 1000

    def change_value3(self, value):
        self.under = 30*value + 1000

    def send(self):
        b = struct.pack("iii?", self.under, self.middle, self.up, self.zone)
        self.cl.send(b)

    def reconnect(self):
        self.init_socket()

    def change_zone(self):
        if self.zone:
            self.button2.setStyleSheet('background-color: blue')
            self.zone = False
        else:
            self.button2.setStyleSheet('background-color: red')
            self.zone = True
        self.send()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())