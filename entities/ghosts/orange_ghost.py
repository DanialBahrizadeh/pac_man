from .ghost import Ghost
from ..entity import DirVector
from ..pac_man import PacMan
from ...colors import Colors
from ...settings import Settings


class OrangeGhost(Ghost):
    def __init__(self, pac_man: PacMan) -> None:
        super().__init__(
            color=Colors.ORANGE,
            corner_target=(1, Settings.GRID_ROWS - 2),
            pac_man=pac_man,
        )

    def dist_to_corner_from(self, vector: DirVector) -> float:
        return self.euclidean_dist(
            vector.add_vector_to(self.position), self.corner_target
        )

    def dist_to_chase_target_from(self, vector: DirVector) -> float:
        dist = self.euclidean_dist(
            vector.add_vector_to(self.position),
            self.pac_man.position,
        )

        if dist > 8:
            return dist

        return self.dist_to_corner_from(vector)
