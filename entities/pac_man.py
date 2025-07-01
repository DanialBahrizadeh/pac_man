from enum import Enum, auto

from .entity import Entity, DirVector


class PacManMode(Enum):
    NORMAL = auto()
    GHOST = auto()


class PacMan(Entity[PacManMode]):
    def __init__(self, position, inital_mode=PacManMode.NORMAL):
        super().__init__(position, inital_mode, DirVector.LEFT)

    def go_normal(self):
        self.mode = PacManMode.NORMAL

    def go_ghost(self) -> None:
        self.mode = PacManMode.GHOST
