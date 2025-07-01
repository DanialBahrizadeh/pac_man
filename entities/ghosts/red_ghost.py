from .ghost import Ghost
from ..entity import DirVector
from ..pac_man import PacMan
from ...colors import Colors
from ...settings import Settings


class RedGhost(Ghost):
    def __init__(self, pac_man: PacMan) -> None:
        super().__init__(
            color=Colors.RED,
            corner_target=(Settings.GRID_COLUMNS - 2, 1),
            pac_man=pac_man,
        )

    def dist_to_chase_target_from(self, vector: DirVector) -> float:
        return self.euclidean_dist(
            vector.add_vector_to(self.position),
            self.pac_man.position,
        )
