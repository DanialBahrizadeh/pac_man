from enum import Enum

from .settings import Settings


class TailType(Enum):
    WALL = 0
    EMPTY = 1
    FOOD = 2
    PELLET = 3


class Map:
    map_str_rpre = [
        "############################",
        "#............##............#",
        "#.####.#####.##.#####.####.#",
        "#@####.#####.##.#####.####@#",
        "#.####.#####.##.#####.####.#",
        "#..........................#",
        "#.####.##.########.##.####.#",
        "#.####.##.########.##.####.#",
        "#......##....##....##......#",
        "######.#####.##.#####.######",
        "*****#.#####.##.#####.#*****",
        "*****#.##..........##.#*****",
        "*****#.##.###**###.##.#*****",
        "######.##.#******#.##.######",
        "..........#******#..........",
        "######.##.#******#.##.######",
        "*****#.##.########.##.#*****",
        "*****#.##..........##.#*****",
        "*****#.##.########.##.#*****",
        "######.##.########.##.######",
        "#............##............#",
        "#.####.#####.##.#####.####.#",
        "#.####.#####.##.#####.####.#",
        "#@..##................##..@#",
        "###.##.##.########.##.##.###",
        "###.##.##.########.##.##.###",
        "#......##....##....##......#",
        "#.##########.##.##########.#",
        "#.##########.##.##########.#",
        "#..........................#",
        "############################",
    ]
    map: list[list[TailType]] = []

    @classmethod
    def init(cls) -> None:
        for row in cls.map_str_rpre:
            map_row = []
            for char in row:
                match char:
                    case "#":
                        map_row.append(TailType.WALL)
                    case ".":
                        map_row.append(TailType.FOOD)
                    case "@":
                        map_row.append(TailType.PELLET)
                    case _:
                        map_row.append(TailType.EMPTY)

            cls.map.append(map_row)

    @classmethod
    def get_tail(cls, position: tuple[int, int]) -> TailType:
        if position[0] not in range(Settings.GRID_COLUMNS):
            return TailType.EMPTY

        if position[1] not in range(Settings.GRID_ROWS):
            return TailType.EMPTY

        return cls.map[position[1]][position[0]]

    @classmethod
    def set_tail(cls, position: tuple[int, int], value: TailType):
        if position[0] not in range(Settings.GRID_COLUMNS):
            return

        if position[1] not in range(Settings.GRID_ROWS):
            return

        cls.map[position[1]][position[0]] = value
