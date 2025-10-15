from enum import auto, Enum


class State(Enum):
    STANDARD = auto()
    RESIZE = auto()
    CREATE_GALAXY = auto()
    TERMINATE = auto()
