from .ghost import Ghost
from ..entity import DirVector
from ..pac_man import PacMan
from ...colors import Colors


class PinkGhost(Ghost):
    def __init__(self, pac_man: PacMan) -> None:
        super().__init__(color=Colors.PINK, corner_target=(1, 1), pac_man=pac_man)

    def dist_to_chase_target_from(self, vector: DirVector) -> float:
        return self.euclidean_dist(
            vector.add_vector_to(self.position),
            self.pac_man.curr_dir.add_vector_to(self.pac_man.position, times=4),
        )
