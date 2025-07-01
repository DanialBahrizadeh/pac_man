class Settings:
    TAIL_SIZE = 20
    GRID_ROWS = 31
    GRID_COLUMNS = 28

    WIDTH = GRID_COLUMNS * TAIL_SIZE
    HIGHT = GRID_ROWS * TAIL_SIZE

    HOST = "127.0.0.1"
    PORT = "8080"

    RUNING = True

    MOVMENT_TIME = 200

    @classmethod
    def turn_off(cls) -> None:
        cls.RUNING = False
