from typing import override
from enum import Enum, auto
from .entity import Entity, DirVector
from ..map import Map, TailType
from ..settings import Settings


class PacManMode(Enum):
    NORMAL = auto()
    GHOST = auto()


class PacMan(Entity[PacManMode]):
    def __init__(self, position, inital_mode=PacManMode.NORMAL, player_number: int = 1):
        super().__init__(
            position, inital_mode, DirVector.LEFT, player_number=player_number
        )

    def go_normal(self):
        self.mode = PacManMode.NORMAL

    def go_ghost(self) -> None:
        self.mode = PacManMode.GHOST

    @override
    def can_move(self, vector) -> bool:
        x, y = vector.add_vector_to(self.position)

        if x not in range(Settings.GRID_COLUMNS * 2 + 1):
            return False

        if y not in range(Settings.GRID_ROWS):
            return False

        if Map.map[y][x] == TailType.WALL:
            return False

        return True

    @override
    def move(self) -> tuple[int, int]:
        if self.player_number == 1:
            if self.position[0] not in range(Settings.GRID_COLUMNS):
                self.go_ghost()
            else:
                self.go_normal()
        else:
            if self.position[0] in range(Settings.GRID_COLUMNS):
                self.go_ghost()
            else:
                self.go_normal()

        return super().move()
