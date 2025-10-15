from enum import auto, Enum


class State(Enum):
    STANDARD = auto()
    RESIZE = auto()
    TERMINATE = auto()
