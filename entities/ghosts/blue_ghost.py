from .ghost import Ghost
from ..entity import DirVector
from ..pac_man import PacMan
from ...colors import Colors
from ...settings import Settings

from .red_ghost import RedGhost


class BlueGhost(Ghost):
    def __init__(
        self, pac_man: PacMan, red_ghost: RedGhost, player_number: int = 1
    ) -> None:
        super().__init__(
            color=Colors.CYAN,
            corner_target=(Settings.GRID_COLUMNS - 2, Settings.GRID_ROWS - 2),
            # corner_target=(1, 1),
            pac_man=pac_man,
            player_number=player_number,
        )
        self.red_ghost = red_ghost

    def dist_to_chase_target_from(self, vector: DirVector) -> float:
        vector_head = self.pac_man.curr_dir.add_vector_to(
            self.pac_man.position, times=2
        )
        red_ghost_pos = self.red_ghost.position
        pac_man_pos = self.pac_man.position
        target = (
            vector_head[0] - red_ghost_pos[0] + pac_man_pos[0],
            vector_head[1] - red_ghost_pos[1] + pac_man_pos[1],
        )

        return self.euclidean_dist(vector.add_vector_to(self.position), target)
