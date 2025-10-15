from dataclasses import dataclass
from enum import auto, Enum


class LayoutMetric(Enum):
    CHARACTERS = auto()
    PERCENTAGE = auto()


@dataclass
class LayoutValueComponent:
    value: int | float
    metric: LayoutMetric


type LayoutValue = list[LayoutValueComponent]
