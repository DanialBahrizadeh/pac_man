import pygame as pg
import socket
import threading
import json

from .entities.ghosts.ghost import GhostMode


from .colors import Colors
from .entities.entity import DirVector
from .settings import Settings
from .map import Map, TailType
from .entities.pac_man import PacMan, PacManMode
from .entities.ghosts.ghosts_manger import GhostManger


class Game:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("localhost", 10000))
        self.sock.listen(2)

        pg.init()
        self.screen = pg.display.set_mode(
            (Settings.WIDTH * 2 + Settings.TAIL_SIZE, Settings.HIGHT), pg.NOFRAME
        )
        self.player_one = Player(self.screen, 1)
        self.player_two = Player(self.screen, 2, self.player_one.pac_man)

        self.player_one_conn = None
        self.player_two_conn = None

        while not self.player_two_conn:
            self.accept_client()

        self.clock = pg.time.Clock()

        self.MOVE_PACMAN = pg.USEREVENT + 1
        pg.time.set_timer(self.MOVE_PACMAN, Settings.MOVMENT_TIME)
        self.SCATTER_CHASE_LOOP = pg.USEREVENT + 2
        pg.time.set_timer(self.SCATTER_CHASE_LOOP, 1000)
        self.EAT_OR_EATEN = pg.USEREVENT + 3
        pg.time.set_timer(self.EAT_OR_EATEN, Settings.MOVMENT_TIME)

        pg.display.set_caption("Pacman")

    def recv_json(self, conn):
        buffer = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                return None

            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                obj = json.loads(line.decode())
                return obj

    def send_json(self, data):
        msg = json.dumps(data) + "\n"
        self.sock.send(msg.encode())

    def accept_client(self):
        conn, addr = self.sock.accept()
        threading.Thread(target=self.handel_client, args=(conn, addr)).start()

    def handel_client(self, conn, addr):
        player_number = 1
        if not self.player_one_conn:
            self.player_one_conn = conn
        elif not self.player_two_conn:
            self.player_two_conn = conn
            player_number = 2

        while True:
            data = self.recv_json(conn)
            if not data:
                break
            print(data)
            key = data["key"]
            print(key)
            if player_number == 1:
                self.player_one.handel_key_down(key)
            else:
                self.player_two.handel_key_down(key)

    def run(self):
        Map.init()

        while Settings.RUNING:
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        Settings.turn_off()
                    case self.EAT_OR_EATEN:
                        self.player_one.handel_eat_or_eaten()
                        self.player_two.handel_eat_or_eaten()
                    case self.MOVE_PACMAN:
                        self.player_one.handel_move_pac_man()
                        self.player_two.handel_move_pac_man()
                    case self.SCATTER_CHASE_LOOP:
                        self.player_one.handel_scatter_change_loop()
                        self.player_two.handel_scatter_change_loop()

            self.screen.fill(Colors.BACKGROUND)

            self.draw_map()
            self.player_one.draw_pac_man()
            self.player_two.draw_pac_man()
            self.player_one.draw_ghosts()
            self.player_two.draw_ghosts()
            self.player_one.show_score()
            self.player_two.show_score()
            pg.display.flip()
            self.clock.tick(60)

        if self.player_one.score > self.player_two.score:
            print("player One won")
        else:
            print("player Two won")

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

    def draw_map(self) -> None:
        for row_idx in range(Settings.GRID_ROWS):
            for col_idx in range(Settings.GRID_COLUMNS * 2 + 1):
                position = (col_idx, row_idx)
                match Map.map[row_idx][col_idx]:
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


class Player:
    def __init__(
        self,
        screen: pg.Surface,
        player_number: int = 1,
        other_player_pac_man: PacMan | None = None,
    ) -> None:
        self.score: int = 0
        self.player_number = player_number
        self.other_player_pac_man = other_player_pac_man
        self.screen = screen

        self.pac_man = PacMan((14, 23), player_number=self.player_number)
        self.ghost_manger = GhostManger(self.pac_man, player_number=self.player_number)

    def handel_key_down(self, key):
        match key:
            # case pg.K_UP:
            case "UP":
                self.pac_man.change_dir(DirVector.UP)
            # case pg.K_RIGHT:
            case "RIGHT":
                self.pac_man.change_dir(DirVector.RIGHT)
            # case pg.K_DOWN:
            case "DOWN":
                self.pac_man.change_dir(DirVector.DOWN)
            # case pg.K_LEFT:
            case "LEFT":
                self.pac_man.change_dir(DirVector.LEFT)

    def handel_eat_or_eaten(self):
        self.score += self.ghost_manger.eat_or_eaten() * 300

    def handel_move_pac_man(self):
        self.ghost_manger.move()
        pacman_position = self.pac_man.move()
        if self.other_player_pac_man:
            if self.pac_man.position == self.other_player_pac_man.position:
                if self.pac_man.mode == PacManMode.GHOST:
                    self.score += 200
                else:
                    self.score -= 200
                Settings.turn_off()
            if self.pac_man.mode == PacManMode.GHOST:
                return

            match Map.get_tail(pacman_position):
                case TailType.FOOD:
                    self.score += 10
                case TailType.PELLET:
                    self.score += 50
                    self.ghost_manger.frighten()

            Map.set_tail(pacman_position, TailType.EMPTY)

    def handel_scatter_change_loop(self):
        self.ghost_manger.scatter_chase_loop()

    def show_score(self):
        scroe_label = pg.font.SysFont("Arial", 24)
        score_surface = scroe_label.render(str(self.score), True, Colors.FONT_COLOR)

        self.screen.blit(
            score_surface, (1 * Settings.TAIL_SIZE, 10.75 * Settings.TAIL_SIZE)
        )

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

    def draw_pac_man(self) -> None:
        self.draw(
            self.pac_man.position,
            Colors.PACMAN,
            kick=0,
            border_radius=Settings.TAIL_SIZE,
        )

    def draw_ghosts(self) -> None:
        for ghost in self.ghost_manger:
            color: tuple[int, int, int] = ghost.color
            if ghost.mode == GhostMode.FRIGHTENED:
                color = Colors.SCARED_GHOST
            elif ghost.mode == GhostMode.EATEN:
                color = Colors.EYE_WHITE
            self.draw(
                ghost.position,
                color,
                kick=0,
                border_radius=Settings.TAIL_SIZE,
            )


if __name__ == "__main__":
    Game().run()
    pg.quit()
