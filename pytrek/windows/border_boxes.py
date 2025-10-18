from curses import window
from pytrek.windows.layout import LayoutValueComponent
from .base import AbstractWindow


class BorderBox(AbstractWindow):
    def __init__(
            self,
            parent: window | AbstractWindow,
            top: list[LayoutValueComponent] = [],
            left: list[LayoutValueComponent] = [],
            height: list[LayoutValueComponent] = [],
            width: list[LayoutValueComponent] = [],
            title: str = ''
    ):
        super().__init__(parent, top, left, height, width)
        self._title = title

    def _draw_content(self):
        self.window.box()
        if not self._title:
            return
        available_width = self.window.getmaxyx()[1] - 6
        if available_width <= 0:
            return
        self.window.addnstr(0, 2, f' {self._title} ', available_width)
