from ...settings import Settings
from ..pac_man import PacMan
from .ghost import GhostMode
from .red_ghost import RedGhost
from .orange_ghost import OrangeGhost
from .pink_ghost import PinkGhost
from .blue_ghost import BlueGhost

import pygame as pg
import sys


class GhostManger:
    def __init__(self, pac_man: PacMan, player_number: int = 1) -> None:
        self.red_ghost = RedGhost(pac_man, player_number=player_number)
        self.orange_ghost = OrangeGhost(pac_man, player_number=player_number)
        self.pink_ghost = PinkGhost(pac_man, player_number=player_number)
        self.blue_ghost = BlueGhost(
            pac_man, self.red_ghost, player_number=player_number
        )

        self._mode = GhostMode.SCATTER
        self.pac_man: PacMan = pac_man
        self.scatter_chase_timer: int = 0
        self.frighten_timer: int = 0

    def __iter__(self):
        yield self.red_ghost
        yield self.orange_ghost
        yield self.pink_ghost
        yield self.blue_ghost

    def swtich_mode_to(self, mode: GhostMode) -> None:
        if mode == self.mode:
            return None
        self.mode = mode

        for ghost in self:
            ghost.path = []
            ghost.mode = mode
            ghost.curr_dir = ghost.curr_dir.opp_dir()

    def move(self) -> None:
        for ghost in self:
            ghost.move()

    @property
    def mode(self) -> GhostMode:
        return self._mode

    @mode.setter
    def mode(self, mode: GhostMode) -> None:
        if not isinstance(mode, GhostMode):
            return None

        self._mode = mode

    def inc_timer(self) -> None:
        if self.mode in [GhostMode.CHASE, GhostMode.SCATTER]:
            self.scatter_chase_timer += 1
        elif self.mode == GhostMode.FRIGHTENED:
            self.frighten_timer += 1

    def scatter_chase_loop(self) -> None:
        if self.pac_man.position[0] in range(
            Settings.GRID_COLUMNS, Settings.GRID_COLUMNS * 2 + 1
        ):
            if self.mode != GhostMode.SCATTER:
                self.swtich_mode_to(GhostMode.SCATTER)

            return None

        self.inc_timer()
        if self.mode == GhostMode.FRIGHTENED:
            if self.frighten_timer > 5:
                self.un_frighten()
                self.frighten_timer = 0
            return

        match self.scatter_chase_timer:
            case 7:
                self.swtich_mode_to(GhostMode.CHASE)
            case 27:
                self.swtich_mode_to(GhostMode.SCATTER)
            case 34:
                self.swtich_mode_to(GhostMode.CHASE)
            case 54:
                self.swtich_mode_to(GhostMode.SCATTER)
            case 59:
                self.swtich_mode_to(GhostMode.CHASE)

    def eat_or_eaten(self) -> int:
        eaten_ghosts: int = 0
        for ghost in self:
            if ghost.mode == GhostMode.EATEN and ghost.position in ghost.BASE:
                ghost.mode = self.mode
                continue
            if ghost.position == self.pac_man.position:
                match ghost.mode:
                    case GhostMode.FRIGHTENED:
                        ghost.mode = GhostMode.EATEN
                        eaten_ghosts += 1
                    case GhostMode.EATEN:
                        pass
                    case _:
                        Settings.turn_off()
                        pg.quit()
                        sys.exit(0)

        return eaten_ghosts

    def frighten(self) -> None:
        self.swtich_mode_to(GhostMode.FRIGHTENED)

    def un_frighten(self) -> None:
        if self.scatter_chase_timer in range(7):
            self.swtich_mode_to(GhostMode.CHASE)
        if self.scatter_chase_timer in range(7, 27):
            self.swtich_mode_to(GhostMode.SCATTER)
        if self.scatter_chase_timer in range(27, 34):
            self.swtich_mode_to(GhostMode.CHASE)
        if self.scatter_chase_timer in range(34, 54):
            self.swtich_mode_to(GhostMode.SCATTER)
        if self.scatter_chase_timer >= 59:
            self.swtich_mode_to(GhostMode.CHASE)
