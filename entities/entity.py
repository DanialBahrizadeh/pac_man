from typing import TypeVar, Generic
from enum import Enum
from ..map import Map, TailType
from ..settings import Settings

T = TypeVar("T")


class DirVector(Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, +1)
    LEFT = (-1, 0)

    def add_vector_to(self, pos: tuple[int, int], times: int = 1) -> tuple[int, int]:
        dx, dy = self.value

        return (pos[0] + (dx * times), pos[1] + (dy * times))

    def opp_dir(self):
        match self:
            case DirVector.UP:
                return DirVector.DOWN
            case DirVector.DOWN:
                return DirVector.UP
            case DirVector.RIGHT:
                return DirVector.LEFT
            case DirVector.LEFT:
                return DirVector.RIGHT
            case _:
                return DirVector.UP


class Entity(Generic[T]):
    def __init__(
        self, position: tuple[int, int], inital_mode: T, curr_dir: DirVector
    ) -> None:
        self.position = position
        self.__mode = inital_mode
        self.curr_dir = curr_dir
        self.next_dir = curr_dir

    def change_dir(self, vector: DirVector):
        self.next_dir = vector

    def move(self) -> tuple[int, int]:
        if self.can_move(self.next_dir):
            self.curr_dir = self.next_dir

        if not self.can_move(self.curr_dir):
            return self.position

        self.position = self.curr_dir.add_vector_to(self.position)

        return self.position

    @staticmethod
    def can_move_to(point: tuple[int, int]) -> bool:
        x, y = point
        if x not in range(Settings.GRID_COLUMNS):
            return False

        if y not in range(Settings.GRID_ROWS):
            return False

        if Map.map[y][x] == TailType.WALL:
            return False

        return True

    def can_move(self, vector: DirVector) -> bool:
        return self.can_move_to(vector.add_vector_to(self.position))

    @property
    def mode(self) -> T:
        return self.__mode

    @mode.setter
    def mode(self, mode: T) -> None:
        if type(mode) is not type(self.mode):
            return None

        self.__mode = mode

    def opp_dir(self) -> DirVector:
        return self.curr_dir.opp_dir()
