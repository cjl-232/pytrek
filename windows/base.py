import abc
import curses

from .layout import LayoutMetric, LayoutValue


def _calc_position(
        layout_value: LayoutValue,
        parent_position: int,
        parent_size: int,
):
    offset = 0.0
    for component in layout_value:
        match component.metric:
            case LayoutMetric.CHARACTERS:
                offset += component.value
            case LayoutMetric.PERCENTAGE:
                offset += parent_size * component.value / 100.0
    return parent_position + round(offset)


def _calc_size(
        layout_value: LayoutValue,
        parent_size: int,
):
    result = 0.0
    for component in layout_value:
        match component.metric:
            case LayoutMetric.CHARACTERS:
                result += component.value
            case LayoutMetric.PERCENTAGE:
                result += parent_size * component.value / 100.0
    return round(result)


class BaseManagedWindow(abc.ABC):
    def __init__(
            self,
            parent: 'curses.window | BaseManagedWindow',
            top: LayoutValue = [],
            left: LayoutValue = [],
            height: LayoutValue = [],
            width: LayoutValue = [],
    ):
        self._parent = parent
        self._top = top
        self._left = left
        self._height = height
        self._width = width
        self.debug_draw_count = 0
        self.place()

    def place(self):
        if isinstance(self._parent, curses.window):
            self._parent_window = self._parent
        else:
            self._parent_window = self._parent.window
        parent_top, parent_left = self._parent_window.getbegyx()
        parent_height, parent_width = self._parent_window.getmaxyx()
        self.window = curses.newwin(
            _calc_size(self._height, parent_height),
            _calc_size(self._width, parent_width),
            _calc_position(self._top, parent_top, parent_height),
            _calc_position(self._left, parent_left, parent_width),
        )
        self._draw_required = True

    @abc.abstractmethod
    def _draw_content(self):
        ...

    def draw(self):
        if not self._draw_required:
            return
        self.window.erase()
        self._draw_content()
        self.window.refresh()
        self._draw_required = False
        self.debug_draw_count += 1
