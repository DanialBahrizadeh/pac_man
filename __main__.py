import pygame as pg

from .entities.ghosts.ghost import GhostMode


from .colors import Colors
from .entities.entity import DirVector
from .settings import Settings
from .map import Map, TailType
from .entities.pac_man import PacMan, PacManMode
from .entities.ghosts.ghosts_manger import GhostManger


class Game:
    def __init__(self, player_number: int = 1) -> None:
        pg.init()

        self.score: int = 0
        self.player_number = player_number

        self.screen = pg.display.set_mode(
            (Settings.WIDTH * 2 + Settings.TAIL_SIZE, Settings.HIGHT), pg.NOFRAME
        )
        self.clock = pg.time.Clock()

        self.MOVE_PACMAN = pg.USEREVENT + 1
        pg.time.set_timer(self.MOVE_PACMAN, Settings.MOVMENT_TIME)
        self.SCATTER_CHASE_LOOP = pg.USEREVENT + 2
        pg.time.set_timer(self.SCATTER_CHASE_LOOP, 1000)
        self.EAT_OR_EATEN = pg.USEREVENT + 3
        pg.time.set_timer(self.EAT_OR_EATEN, Settings.MOVMENT_TIME)

        pg.display.set_caption("Pacman")

    def run(self) -> None:
        Map.init()
        self.pac_man = PacMan((14, 23), player_number=self.player_number)
        self.ghost_manger = GhostManger(self.pac_man, player_number=self.player_number)
        while Settings.RUNING:
            for event in pg.event.get():
                match event.type:
                    case pg.QUIT:
                        Settings.turn_off()

                    case pg.KEYDOWN:
                        match event.key:
                            case pg.K_UP:
                                self.pac_man.change_dir(DirVector.UP)
                            case pg.K_RIGHT:
                                self.pac_man.change_dir(DirVector.RIGHT)
                            case pg.K_DOWN:
                                self.pac_man.change_dir(DirVector.DOWN)
                            case pg.K_LEFT:
                                self.pac_man.change_dir(DirVector.LEFT)

                    case self.EAT_OR_EATEN:
                        self.score += self.ghost_manger.eat_or_eaten() * 300

                    case self.MOVE_PACMAN:
                        self.ghost_manger.move()
                        pacman_position = self.pac_man.move()
                        if self.pac_man.mode == PacManMode.GHOST:
                            break

                        match Map.get_tail(pacman_position):
                            case TailType.FOOD:
                                self.score += 10
                            case TailType.PELLET:
                                self.score += 50
                                self.ghost_manger.frighten()

                        Map.set_tail(pacman_position, TailType.EMPTY)

                    case self.SCATTER_CHASE_LOOP:
                        self.ghost_manger.scatter_chase_loop()

            self.screen.fill(Colors.BACKGROUND)

            self.draw_map()
            self.draw_pac_man()
            self.draw_ghosts()
            self.show_score()
            pg.display.flip()
            self.clock.tick(60)

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
    Game(1).run()
    pg.quit()
