from enum import Enum, auto

from .settings import Settings


class TailType(Enum):
    WALL = "#"
    EMPTY = "*"
    FOOD = "."
    PELLET = "@"
    BORDER = "!"


class Map:
    map_str_rpre = [
        "#########################################################",
        "#............##............###............##............#",
        "#.####.#####.##.#####.####.###.####.#####.##.#####.####.#",
        "#@####.#####.##.#####.####@###@####.#####.##.#####.####@#",
        "#.####.#####.##.#####.####.###.####.#####.##.#####.####.#",
        "#..........................###..........................#",
        "#.####.##.########.##.####.###.####.##.########.##.####.#",
        "#.####.##.########.##.####.###.####.##.########.##.####.#",
        "#......##....##....##......###......##....##....##......#",
        "######.#####.##.#####.#############.#####.##.#####.######",
        "*****#.#####.##.#####.#*****#*****#.#####.##.#####.#*****",
        "*****#.##..........##.#*****#*****#.##..........##.#*****",
        "*****#.##.###**###.##.#*****#*****#.##.###**###.##.#*****",
        "######.##.#******#.##.#############.##.#******#.##.######",
        "..........#******#..........!..........#******#..........",
        "######.##.#******#.##.#############.##.#******#.##.######",
        "*****#.##.########.##.#*****#*****#.##.########.##.#*****",
        "*****#.##..........##.#*****#*****#.##..........##.#*****",
        "*****#.##.########.##.#*****#*****#.##.########.##.#*****",
        "######.##.########.##.#############.##.########.##.######",
        "#............##............###............##............#",
        "#.####.#####.##.#####.####.###.####.#####.##.#####.####.#",
        "#.####.#####.##.#####.####.###.####.#####.##.#####.####.#",
        "#@..##................##..@###@..##................##..@#",
        "###.##.##.########.##.##.#######.##.##.########.##.##.###",
        "###.##.##.########.##.##.#######.##.##.########.##.##.###",
        "#......##....##....##......###......##....##....##......#",
        "#.##########.##.##########.###.##########.##.##########.#",
        "#.##########.##.##########.###.##########.##.##########.#",
        "#..........................###..........................#",
        "#########################################################",
    ]
    map: list[list[TailType]] = []

    @classmethod
    def init(cls) -> None:
        cls.map = cls.tranlate_from_str(cls.map_str_rpre)

    @classmethod
    def get_tail(cls, position: tuple[int, int]) -> TailType:
        if position[0] not in range(Settings.GRID_COLUMNS * 2 + 1):
            return TailType.EMPTY

        if position[1] not in range(Settings.GRID_ROWS):
            return TailType.EMPTY

        return cls.map[position[1]][position[0]]

    @classmethod
    def set_tail(cls, position: tuple[int, int], value: TailType):
        x, y = position
        if x not in range(Settings.GRID_COLUMNS * 2 + 1):
            return

        if y not in range(Settings.GRID_ROWS):
            return

        if cls.get_tail(position) == TailType.BORDER:
            return None
        cls.map[y][x] = value

    @classmethod
    def tranlate_from_str(cls, map_str_rpre: list[str]):
        map = []
        for row in map_str_rpre:
            map_row = []
            for char in row:
                match char:
                    case "#":
                        map_row.append(TailType.WALL)
                    case ".":
                        map_row.append(TailType.FOOD)
                    case "@":
                        map_row.append(TailType.PELLET)
                    case "!":
                        map_row.append(TailType.BORDER)
                    case _:
                        map_row.append(TailType.EMPTY)

            map.append(map_row)
        return map

    @classmethod
    def tranlate_to_str(cls, map: list[list[TailType]]):
        return [[tile.value for tile in row] for row in map]
