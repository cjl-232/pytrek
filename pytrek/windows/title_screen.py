# TODO I want this to scroll up and the orders to show up after. It'd be cool

# GO up until centre reached
# On game start... go up again. How? Hm... allow the timer to continue?
# Ensure the timer is linked to the centre after a resize

import curses

from enum import auto, Enum
from textwrap import wrap
from time import time

from pytrek.states import State

from .base import AbstractFocusableWindow
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
    SHOW_TITLE = auto()
    DISPLAY_TITLE = auto()
    HIDE_TITLE = auto()
    SHOW_ORDERS = auto()
    DISPLAY_ORDERS = auto()


class TitleScreen(AbstractFocusableWindow):
    def __init__(
            self,
            parent: 'curses.window | AbstractFocusableWindow',
            top: LayoutValue = [],
            left: LayoutValue = [],
            height: LayoutValue = [],
            width: LayoutValue = [],
    ):
        super().__init__(parent, top, left, height, width)
        self._animation = Animation.SHOW_TITLE
        self._animation_stage = -1
        self._last_updated = 0.0
        self._orders = ''

    def _draw_show_title(self):
        height, width = self.window.getmaxyx()
        empty_space = height - len(_TITLE_CONTENT)
        y_pos = height - 1 - self._animation_stage
        if y_pos < empty_space // 2:
            y_pos = empty_space // 2
            self._animation = Animation.DISPLAY_TITLE
        for line in _TITLE_CONTENT[:self._animation_stage + 1]:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1

    def _draw_display_title(self):
        height, width = self.window.getmaxyx()
        empty_space = height - len(_TITLE_CONTENT)
        y_pos = empty_space // 2
        for line in _TITLE_CONTENT:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1

    def _draw_hide_title(self):
        height, width = self.window.getmaxyx()
        empty_space = height - len(_TITLE_CONTENT)
        y_pos = empty_space // 2 - self._animation_stage
        for line in _TITLE_CONTENT:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}{y_pos}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1
        if y_pos < 0:
            self._animation = Animation.SHOW_ORDERS
            self._animation_stage = -1
            self._last_updated = 0.0

    def _draw_show_orders(self):
        height, width = self.window.getmaxyx()
        lines = wrap(self._orders, min(60, width))
        lines += ['', 'PRESS ENTER TO BEGIN YOUR MISSION...']
        empty_space = height - len(lines)
        y_pos = height - 1 - self._animation_stage
        if y_pos < empty_space // 2:
            y_pos = empty_space // 2
            self._animation = Animation.DISPLAY_ORDERS
        for line in lines[:self._animation_stage + 1]:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1

    def _draw_display_orders(self):
        height, width = self.window.getmaxyx()
        lines = wrap(self._orders, min(60, width))
        lines += ['', 'PRESS ENTER TO BEGIN YOUR MISSION...']
        empty_space = height - len(lines)
        y_pos = empty_space // 2
        for line in lines:
            if 0 <= y_pos < height:
                padded_line = f'{line:{' '}^{width}}'
                self.window.addnstr(y_pos, 0, padded_line, width - 1)
            y_pos += 1

    def _draw_content(self):
        match self._animation:
            case Animation.SHOW_TITLE:
                self._draw_show_title()
            case Animation.DISPLAY_TITLE:
                self._draw_display_title()
            case Animation.HIDE_TITLE:
                self._draw_hide_title()
            case Animation.SHOW_ORDERS:
                self._draw_show_orders()
            case Animation.DISPLAY_ORDERS:
                self._draw_display_orders()

    def draw(self):
        match self._animation:
            case (
                Animation.SHOW_TITLE |
                Animation.HIDE_TITLE |
                Animation.SHOW_ORDERS
            ):
                if time() - self._last_updated >= _TITLE_ANIMATION_INTERVAL:
                    self._animation_stage += 1
                    self._last_updated = time()
                    self._draw_required = True
                pass
            case _:
                pass
        super().draw()

    def set_orders(self, orders: str):
        self._orders = orders

    def handle_key(self, key: int) -> State:
        match (self._animation, key):
            case (Animation.DISPLAY_TITLE, curses.KEY_ENTER | 10):
                self._animation = Animation.HIDE_TITLE
                self._animation_stage = 0
                self._last_updated = 0.0
                return State.CREATE_GALAXY
            case (Animation.DISPLAY_ORDERS, curses.KEY_ENTER | 10):
                return State.ENTER_GALAXY
            case _:
                return State.STANDARD
        return State.STANDARD
