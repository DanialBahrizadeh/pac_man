import socket
import pygame as pg
import json

from .settings import Settings


class Client:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("localhost", 10000))
        pg.init()
        pg.display.set_mode((10, 10))

        while Settings.RUNING:
            for event in pg.event.get():
                match event.type:
                    case pg.KEYDOWN:
                        match event.key:
                            case pg.K_UP:
                                # self.pac_man.change_dir(DirVector.UP)
                                # self.sock.send(b"UP")
                                # self.sock.send(json.dumps({"key": "UP"}).encode())
                                self.send_json({"key": "UP"})
                            case pg.K_RIGHT:
                                # self.pac_man.change_dir(DirVector.RIGHT)
                                # self.sock.send(b"RIGHT")
                                # self.sock.send(json.dumps({"key": "RIGHT"}).encode())
                                self.send_json({"key": "RIGHT"})
                            case pg.K_DOWN:
                                # self.pac_man.change_dir(DirVector.DOWN)
                                # self.sock.send(b"DOWN")
                                # self.sock.send(json.dumps({"key": "DOWN"}).encode())
                                self.send_json({"key": "DOWN"})
                            case pg.K_LEFT:
                                # self.pac_man.change_dir(DirVector.LEFT)
                                # self.sock.send(b"LEFT")
                                # self.sock.send(json.dumps({"key": "LEFT"}).encode())
                                self.send_json({"key": "LEFT"})

    def send_json(self, data):
        msg = json.dumps(data) + "\n"
        self.sock.send(msg.encode())


Client()
