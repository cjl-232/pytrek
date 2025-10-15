# TODO I want this to scroll up and the orders to show up after. It'd be cool

import curses

from enum import auto, Enum
from time import time

from .base import AbstractWindow
from .layout import LayoutValue

_TITLE_ANIMATION_INTERVAL = 0.1

_TITLE_CONTENT = [
    "                ,------*------,",
    ",-------------   '---  ------' ",
    " '-------- --'      / /        ",
    "     ,---' '-------/ /--,      ",
    "      '----------------'       ",
    "                               ",
    "THE USS ENTERPRISE --- NCC-1701",
    "                               ",
    "    PRESS ENTER TO PROCEED     ",
]


class Display(Enum):
    TITLE = auto()
    SHORT_RANGE_SENSORS = auto()


class MainScreen(AbstractWindow):
    def __init__(
            self,
            parent: 'curses.window | AbstractWindow',
            top: LayoutValue = [],
            left: LayoutValue = [],
            height: LayoutValue = [],
            width: LayoutValue = [],
    ):
        super().__init__(parent, top, left, height, width)
        self.update_display(Display.TITLE)
        self.content: list[str] = []

    def _draw_title(self):
        height, width = self.window.getmaxyx()
        empty_space = height - len(_TITLE_CONTENT)
        y_pos = max(height - 1 - self._animation_stage, empty_space // 2)
        for line in _TITLE_CONTENT[:self._animation_stage + 1]:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1

    def _draw_content(self):
        match self.display:
            case Display.TITLE:
                self._draw_title()
            case Display.SHORT_RANGE_SENSORS:
                pass

    def draw(self):
        match self.display:
            case Display.TITLE:
                if self._animation_stage >= self.window.getmaxyx()[0]:
                    pass
                elif time() - self._last_updated >= _TITLE_ANIMATION_INTERVAL:
                    self._animation_stage += 1
                    self._last_updated = time()
                    self._draw_required = True
            case Display.SHORT_RANGE_SENSORS:
                pass
        super().draw()

    def update_display(self, display: Display):
        self.display = display
        self._animation_stage = -1
        self._last_updated = 0.0
