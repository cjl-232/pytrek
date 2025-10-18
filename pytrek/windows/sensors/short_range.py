import curses

from ..base import AbstractWindow
from ..layout import LayoutValue
from ...enterprise import Enterprise
from ...galaxies import LocalMap


class ShortRangeDisplay(AbstractWindow):
    def __init__(
            self,
            parent: 'curses.window | AbstractWindow',
            enterprise: Enterprise,
            top: LayoutValue = [],
            left: LayoutValue = [],
            height: LayoutValue = [],
            width: LayoutValue = [],
    ):
        super().__init__(parent, top, left, height, width)
        self._local_map: LocalMap | None = None
        self._enterprise = enterprise

    def _draw_content(self):
        if self._local_map is None:
            return
        self._local_map.draw(
            self.window,
            self._enterprise.sector_coordinates,
        )

    def draw(self):
        super().draw()

    def set_local_map(self, local_map: LocalMap):
        self._local_map = local_map
