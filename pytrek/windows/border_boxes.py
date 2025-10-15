from .base import AbstractWindow


class BorderBox(AbstractWindow):
    def _draw_content(self):
        self.window.box()
