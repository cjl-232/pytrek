# TODO I want this to scroll up and the orders to show up after. It'd be cool

# GO up until centre reached
# On game start... go up again. How? Hm... allow the timer to continue?
# Ensure the timer is linked to the centre after a resize

import curses

from enum import auto, Enum
from time import time

from .base import BaseManagedWindow
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


class Animation(Enum):
    TITLE_ENTRY = auto()
    TITLE_CENTRED = auto()
    TITLE_EXIT = auto()
    ORDERS_ENTRY = auto()
    ORDERS_CENTRED = auto()


class TitleScreen(BaseManagedWindow):
    def __init__(
            self,
            parent: 'curses.window | BaseManagedWindow',
            top: LayoutValue = [],
            left: LayoutValue = [],
            height: LayoutValue = [],
            width: LayoutValue = [],
    ):
        super().__init__(parent, top, left, height, width)
        self._animation = Animation.TITLE_ENTRY
        self._animation_stage = -1
        self._last_updated = 0.0
        self._orders: None | str = None

    def _draw_title_entry(self):
        height, width = self.window.getmaxyx()
        empty_space = height - len(_TITLE_CONTENT)
        y_pos = height - 1 - self._animation_stage
        if y_pos < empty_space // 2:
            y_pos = empty_space // 2
            self._animation = Animation.TITLE_CENTRED
        for line in _TITLE_CONTENT[:self._animation_stage + 1]:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1

    def _draw_title_centred(self):
        height, width = self.window.getmaxyx()
        empty_space = height - len(_TITLE_CONTENT)
        y_pos = empty_space // 2
        for line in _TITLE_CONTENT:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1

    def _draw_title_exit(self):
        height, width = self.window.getmaxyx()
        empty_space = height - len(_TITLE_CONTENT)
        y_pos = empty_space // 2 - self._animation_stage
        for line in _TITLE_CONTENT:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1
        if y_pos <= 0:
            self._animation = Animation.ORDERS_ENTRY

    def _draw_content(self):
        match self._animation:
            case Animation.TITLE_ENTRY:
                self._draw_title_entry()
            case Animation.TITLE_CENTRED:
                self._draw_title_centred()
            case Animation.TITLE_EXIT:
                self._draw_title_exit()
            case Animation.ORDERS_ENTRY:
                pass
            case Animation.ORDERS_CENTRED:
                pass

    def draw(self):
        match self._animation:
            case Animation.TITLE_ENTRY | Animation.TITLE_EXIT:
                if time() - self._last_updated >= _TITLE_ANIMATION_INTERVAL:
                    self._animation_stage += 1
                    self._last_updated = time()
                    self._draw_required = True
                pass
            case Animation.TITLE_CENTRED:
                pass
            case Animation.ORDERS_ENTRY:
                pass
            case Animation.ORDERS_CENTRED:
                pass
        super().draw()

    def set_orders(self, orders: None | str):
        self._orders = orders
