from abc import ABC, abstractmethod
from enum import Enum, auto
from random import choice

from ..pac_man import PacMan

from ..entity import Entity, DirVector
from ...settings import Settings


class GhostMode(Enum):
    SCATTER = auto()
    CHASE = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class Ghost(Entity, ABC):
    BASE: list[tuple[int, int]] = [(i, j) for i in range(11, 16) for j in range(14, 16)]

    def __init__(
        self,
        color: tuple[int, int, int],
        corner_target: tuple[int, int],
        pac_man: PacMan,
    ) -> None:
        super().__init__(
            position=choice(Ghost.BASE),
            inital_mode=GhostMode.SCATTER,
            curr_dir=DirVector.UP,
        )
        self.color = color
        self.corner_target = corner_target
        self.pac_man = pac_man
        self.path: list[DirVector] = []

    def chose_dir(self) -> DirVector:
        if self.position[0] == 0:
            return DirVector.RIGHT
        if self.position[0] == Settings.GRID_COLUMNS:
            return DirVector.LEFT

        match self.mode:
            case GhostMode.SCATTER:
                return self.scatter_dir()
            case GhostMode.FRIGHTENED:
                return self.frightened_dir()
            case GhostMode.EATEN:
                return self.eaten_dir()
            case GhostMode.CHASE:
                return self.chase_dir()
            case _:
                return DirVector.UP

    def move(self) -> tuple[int, int]:
        super().change_dir(self.chose_dir())
        return super().move()

    def eaten(self):
        self.mode = GhostMode.EATEN

    @staticmethod
    def euclidean_dist(
        first_point: tuple[int, int], second_point: tuple[int, int]
    ) -> float:
        return (
            (first_point[0] - second_point[0]) ** 2
            + (first_point[1] - second_point[1]) ** 2
        ) ** 0.5

    def scatter_dir(self) -> DirVector:
        if not self.path:
            self.path = self.find_path(self.position, self.corner_target) or [
                self.curr_dir
            ]

        return self.path.pop(0)

    def frightened_dir(self) -> DirVector:
        all_choices = [
            dir for dir in DirVector if dir != self.opp_dir() and self.can_move(dir)
        ]
        if not all_choices:
            return self.curr_dir

        return choice(all_choices)

    def eaten_dir(self) -> DirVector:
        if not self.path:
            print("start")
            self.path = self.find_path(self.position, (13, 14))
        return self.path.pop(0)

    def chase_dir(self) -> DirVector:
        dist: dict[DirVector, float] = {
            dir: self.dist_to_chase_target_from(dir)
            for dir in DirVector
            if dir != self.opp_dir() and self.can_move(dir)
        }

        if not dist:
            return self.curr_dir

        return min(dist.keys(), key=lambda x: dist[x])

    @abstractmethod
    def dist_to_chase_target_from(self, vector: DirVector) -> float: ...

    def dir_get_closer(
        self,
        index: int,
        path: list[DirVector],
        dist: list[float],
        ban_move: set[tuple[int, DirVector]],
        visited: set[tuple[int, int]],
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> DirVector | None:
        chosen_dir: DirVector | None = None
        for dir in DirVector:
            if path and dir == path[-1].opp_dir():
                continue

            if (index, dir) in ban_move:
                continue

            new_pos = dir.add_vector_to(start)
            new_dist = self.euclidean_dist(new_pos, goal)

            if not self.can_move_to(new_pos):
                continue

            if new_pos in visited and new_pos != goal:
                continue

            if new_dist < dist[-1]:
                chosen_dir = dir

            continue

        return chosen_dir

    def dir_valid_move(
        self,
        index: int,
        path: list[DirVector],
        ban_move: set[tuple[int, DirVector]],
        visited: set[tuple[int, int]],
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> DirVector | None:
        dist: dict[DirVector, float] = {}

        for dir in DirVector:
            if (index, dir) in ban_move:
                continue

            if path and dir == path[-1].opp_dir():
                continue

            new_pos = dir.add_vector_to(start)
            new_dist = self.euclidean_dist(new_pos, goal)

            if not self.can_move_to(new_pos):
                continue

            if new_pos in visited and new_pos != goal:
                continue

            dist[dir] = new_dist

        if not dist:
            return None

        return min(dist.keys(), key=lambda dir: dist[dir])

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[DirVector]:
        path: list[DirVector] = [self.curr_dir]
        ban_move: set[tuple[int, DirVector]] = set()
        visited: set[tuple[int, int]] = {start}
        index = 0
        dist = [self.euclidean_dist(start, goal)]

        if start == goal:
            dir = self.dir_valid_move(index, path, ban_move, visited, start, goal)
            if not dir:
                return []

            path.append(dir)
            start = dir.add_vector_to(start)
            visited.add(start)
            dist.append(self.euclidean_dist(start, goal))

        while start != goal:
            index += 1
            chosen_dir: DirVector | None = self.dir_get_closer(
                index, path, dist, ban_move, visited, start, goal
            )

            if chosen_dir:
                path.append(chosen_dir)
                start = chosen_dir.add_vector_to(start)
                dist.append(self.euclidean_dist(start, goal))
                visited.add(start)
                index += 1
            else:
                chosen_dir = self.dir_valid_move(
                    index, path, ban_move, visited, start, goal
                )

                if chosen_dir:
                    path.append(chosen_dir)
                    start = chosen_dir.add_vector_to(start)
                    dist.append(self.euclidean_dist(start, goal))
                    visited.add(start)
                    index += 1
                    continue

                dir = path.pop()
                dist.pop()
                ban_move.add((index, dir))
                index -= 1
                visited.remove(start)
                start = dir.opp_dir().add_vector_to(start)

        return path[1:]
