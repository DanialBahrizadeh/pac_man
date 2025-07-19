import socketio
import pygame as pg
import sys

# import socketio

from .settings import Settings
from .map import Map, TailType
from .colors import Colors


class Client:
    def __init__(self) -> None:
        self.sio = socketio.Client()
        self.game_state = {
            "p1": {"score": 0, "entities": []},
            "p2": {"score": 0, "entities": []},
            "map": [],
        }
        self.screen = pg.display.set_mode(
            (Settings.WIDTH * 2 + Settings.TAIL_SIZE, Settings.HEIGHT), pg.NOFRAME
        )
        self.clock = pg.time.Clock()
        self.running = True

    def handel_events(self):
        @self.sio.event
        def connect():
            print("Connect to the server")

        @self.sio.event
        def disconnect():
            print("Disconnect from the server")
            self.running = False

        @self.sio.on("update_state")  # pyright: ignore
        def on_update_state(data):
            # print(data)
            data["map"] = Map.tranlate_from_str(data["map"])
            self.game_state = data

        @self.sio.on("game_over")  # pyright: ignore
        def on_game_over():
            print("you lost")
            self.running = False

        @self.sio.on("game_won")  # pyright: ignore
        def on_game_won():
            print("you won")
            self.running = False

    def connect(self):
        self.sio.connect(f"http://{Settings.HOST}:{Settings.PORT}")

    def start(self):
        pg.init()

        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    self.sio.disconnect()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    key_map = {
                        pg.K_UP: "UP",
                        pg.K_DOWN: "DOWN",
                        pg.K_LEFT: "LEFT",
                        pg.K_RIGHT: "RIGHT",
                    }

                    if event.key in key_map:
                        self.sio.emit("key_press", {"key": key_map[event.key]})

            self.screen.fill((0, 0, 0))
            if self.game_state:
                self.draw_map()
                self.draw_entities()
                self.show_score()

            pg.display.flip()
            self.clock.tick(60)

        pg.quit()
        self.sio.disconnect()
        print("Client shutting down.")

    def draw(
        self,
        position: tuple[int, int],
        color: tuple[int, int, int],
        divider: float = 1.0,
        kick: float = Settings.TAIL_SIZE / 4,
        border_radius: int = 0,
    ) -> None:
        rect = pg.Rect(
            position[0] * Settings.TAIL_SIZE + kick,
            position[1] * Settings.TAIL_SIZE + kick,
            Settings.TAIL_SIZE / divider,
            Settings.TAIL_SIZE / divider,
        )

        pg.draw.rect(self.screen, color, rect, border_radius=border_radius)

    def draw_entities(self):
        for entity in self.game_state["p1"]["entities"]:
            self.draw(
                entity[0],
                entity[1],
                kick=0,
                border_radius=Settings.TAIL_SIZE,
            )

        for entity in self.game_state["p2"]["entities"]:
            self.draw(
                entity[0],
                entity[1],
                kick=0,
                border_radius=Settings.TAIL_SIZE,
            )

    def draw_map(self) -> None:
        for row_idx in range(len(self.game_state["map"])):
            for col_idx in range(len(self.game_state["map"][0])):
                position = (col_idx, row_idx)
                # print(self.game_state)
                match self.game_state["map"][row_idx][col_idx]:
                    case TailType.WALL:
                        self.draw(
                            position,
                            Colors.WALL,
                            divider=2,
                            border_radius=2,
                        )
                    case TailType.FOOD:
                        self.draw(position, Colors.FOOD, divider=4)
                    case TailType.PELLET:
                        self.draw(
                            position,
                            Colors.PELLET,
                            kick=0,
                            border_radius=Settings.TAIL_SIZE,
                        )
                    case TailType.BORDER:
                        self.draw(position, Colors.RED, kick=0, border_radius=3)

    def show_score(self):
        scroe_label = pg.font.SysFont("Arial", 24)
        player1_score_surface = scroe_label.render(
            str(self.game_state["p1"]["score"]), True, Colors.FONT_COLOR
        )
        player2_score_surface = scroe_label.render(
            str(self.game_state["p2"]["score"]), True, Colors.FONT_COLOR
        )

        self.screen.blit(
            player1_score_surface, (1 * Settings.TAIL_SIZE, 10.75 * Settings.TAIL_SIZE)
        )

        self.screen.blit(
            player2_score_surface,
            (
                (2 + Settings.GRID_COLUMNS) * Settings.TAIL_SIZE,
                10.75 * Settings.TAIL_SIZE,
            ),
        )


if __name__ == "__main__":
    client = Client()
    client.handel_events()
    client.connect()
    client.start()
