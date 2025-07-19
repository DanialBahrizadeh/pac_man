import socketio
import asyncio
import pygame as pg
import uvicorn
import threading
import sys

from .game import Game
from .settings import Settings
from .map import Map


class Server:
    def __init__(self) -> None:
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self.app = socketio.ASGIApp(self.sio)

        self.game = Game()

        self.player_one_sid = None
        self.player_two_sid = None

        self.run()

    def run(self):
        @self.sio.event
        async def connect(sid, _):
            print(f"[+] Client connected: {sid}")

            if self.player_one_sid is None:
                self.player_one_sid = sid
                self.game.create_player_one()
                return print("→ Assigned as Player 1")

            if self.player_two_sid is None:
                self.player_two_sid = sid
                self.game.create_player_two()
                return print("→ Assigned as Player 2")

            print("× More than two clients tried to connect")
            return False

        @self.sio.on("key_press")  # pyright: ignore
        async def on_key_press(sid, data):
            key = data.get("key", "UP")
            print(key)
            if sid == self.player_one_sid:
                self.game.player_one.handel_key_down(key)
            else:
                self.game.player_two.handel_key_down(key)

        @self.sio.event
        async def disconnect(sid):
            print(f"[-] Client disconnected: {sid}")

    async def broadcast_game_state(self):
        state = {
            "p1": self.game.player_one.get_state(),
            "p2": self.game.player_two.get_state(),
            "map": Map.tranlate_to_str(Map.map),
        }
        await self.sio.emit("update_state", state)

    async def game_loop(self):
        game_started = False
        Map.init()
        while Settings.RUNING:
            if not self.player_one_sid or not self.player_two_sid:
                continue
            for event in pg.event.get():
                if not game_started and event.type == self.game.START_GAME:
                    game_started = True

                if not game_started:
                    continue

                match event.type:
                    case pg.QUIT:
                        Settings.turn_off()
                    case self.game.EAT_OR_EATEN:
                        self.game.player_one.handel_eat_or_eaten()
                        self.game.player_two.handel_eat_or_eaten()
                    case self.game.MOVE_PACMAN:
                        self.game.player_one.handel_move_pac_man()
                        self.game.player_two.handel_move_pac_man()
                    case self.game.SCATTER_CHASE_LOOP:
                        self.game.player_one.handel_scatter_change_loop()
                        self.game.player_two.handel_scatter_change_loop()

                if self.game.player_one.eaten or self.game.player_two.eaten:
                    if self.game.player_two.score > self.game.player_one.score:
                        await self.sio.emit("game_over", to=self.player_one_sid)
                        await self.sio.emit("game_won", to=self.player_two_sid)
                    else:
                        await self.sio.emit("game_over", to=self.player_two_sid)
                        await self.sio.emit("game_won", to=self.player_two_sid)

                    Settings.turn_off()
            self.game.clock.tick(60)

            await self.broadcast_game_state()
            await asyncio.sleep(0)

        pg.quit()

    async def start(self):
        asyncio.create_task(self.game_loop())


if __name__ == "__main__":
    server = Server()

    async def main():
        await server.start()
        while True:
            await asyncio.sleep(1)

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    def run_uvicorn():
        uvicorn.run(server.app, host=Settings.HOST, port=Settings.PORT)

    threading.Thread(target=run_uvicorn).start()
    loop.run_forever()
