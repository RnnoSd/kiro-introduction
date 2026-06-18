from enum import Enum, auto


class State(Enum):
    """Game state machine states."""
    IDLE = auto()
    PLAYING = auto()
    GAME_OVER = auto()
