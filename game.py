import pygame as pg

from .entities.ghosts.ghost import GhostMode


from .colors import Colors
from .entities.entity import DirVector
from .settings import Settings
from .map import Map, TailType
from .entities.pac_man import PacMan, PacManMode
from .entities.ghosts.ghosts_manger import GhostManger


class Game:
    def __init__(self) -> None:
        pg.init()
        # self.screen = pg.display.set_mode(
        #     (Settings.WIDTH * 2 + Settings.TAIL_SIZE, Settings.HEIGHT), pg.NOFRAME
        # )

        self.clock = pg.time.Clock()

        self.MOVE_PACMAN = pg.USEREVENT + 1
        pg.time.set_timer(self.MOVE_PACMAN, Settings.MOVMENT_TIME)
        self.SCATTER_CHASE_LOOP = pg.USEREVENT + 2
        pg.time.set_timer(self.SCATTER_CHASE_LOOP, 1000)
        self.EAT_OR_EATEN = pg.USEREVENT + 3
        pg.time.set_timer(self.EAT_OR_EATEN, Settings.MOVMENT_TIME)

        pg.display.set_caption("Pacman")

    def create_player_one(self):
        self.player_one = Player( 1)

    def create_player_two(self):
        self.player_two = Player( 2, self.player_one.pac_man)

    # def draw(
    #     self,
    #     position: tuple[int, int],
    #     color: tuple[int, int, int],
    #     divider: float = 1.0,
    #     kick: float = Settings.TAIL_SIZE / 4,
    #     border_radius: int = 0,
    # ) -> None:
    #     rect = pg.Rect(
    #         position[0] * Settings.TAIL_SIZE + kick,
    #         position[1] * Settings.TAIL_SIZE + kick,
    #         Settings.TAIL_SIZE / divider,
    #         Settings.TAIL_SIZE / divider,
    #     )
    #
    #     pg.draw.rect(self.screen, color, rect, border_radius=border_radius)
    #
    # def draw_map(self) -> None:
    #     for row_idx in range(Settings.GRID_ROWS):
    #         for col_idx in range(Settings.GRID_COLUMNS * 2 + 1):
    #             position = (col_idx, row_idx)
    #             match Map.map[row_idx][col_idx]:
    #                 case TailType.WALL:
    #                     self.draw(
    #                         position,
    #                         Colors.WALL,
    #                         divider=2,
    #                         border_radius=2,
    #                     )
    #                 case TailType.FOOD:
    #                     self.draw(position, Colors.FOOD, divider=4)
    #                 case TailType.PELLET:
    #                     self.draw(
    #                         position,
    #                         Colors.PELLET,
    #                         kick=0,
    #                         border_radius=Settings.TAIL_SIZE,
    #                     )
    #                 case TailType.BORDER:
    #                     self.draw(position, Colors.RED, kick=0, border_radius=3)


class Player:
    def __init__(
        self,
        # screen: pg.Surface,
        player_number: int = 1,
        other_player_pac_man: PacMan | None = None,
    ) -> None:
        self.score: int = 0
        self.player_number = player_number
        self.other_player_pac_man = other_player_pac_man
        # self.screen = screen

        self.pac_man = PacMan((14, 23), player_number=self.player_number)
        self.ghost_manger = GhostManger(self.pac_man, player_number=self.player_number)

    def get_state(self):
        return {
            "score": self.score,
            "entities": [
                (self.pac_man.position, Colors.PACMAN),
                *[(ghost.position, ghost.color) for ghost in self.ghost_manger],
            ],
        }

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

        # self.screen.blit(
        #     score_surface, (1 * Settings.TAIL_SIZE, 10.75 * Settings.TAIL_SIZE)
        # )

    # def draw(
    #     self,
    #     position: tuple[int, int],
    #     color: tuple[int, int, int],
    #     divider: float = 1.0,
    #     kick: float = Settings.TAIL_SIZE / 4,
    #     border_radius: int = 0,
    # ) -> None:
    #     rect = pg.Rect(
    #         position[0] * Settings.TAIL_SIZE + kick,
    #         position[1] * Settings.TAIL_SIZE + kick,
    #         Settings.TAIL_SIZE / divider,
    #         Settings.TAIL_SIZE / divider,
    #     )
    #
    #     pg.draw.rect(self.screen, color, rect, border_radius=border_radius)

    # def draw_pac_man(self) -> None:
    #     self.draw(
    #         self.pac_man.position,
    #         Colors.PACMAN,
    #         kick=0,
    #         border_radius=Settings.TAIL_SIZE,
    #     )

    # def draw_ghosts(self) -> None:
    #     for ghost in self.ghost_manger:
    #         color: tuple[int, int, int] = ghost.color
    #         if ghost.mode == GhostMode.FRIGHTENED:
    #             color = Colors.SCARED_GHOST
    #         elif ghost.mode == GhostMode.EATEN:
    #             color = Colors.EYE_WHITE
    #         self.draw(
    #             ghost.position,
    #             color,
    #             kick=0,
    #             border_radius=Settings.TAIL_SIZE,
    #         )


# if __name__ == "__main__":
# Game().run()
# pg.quit()
