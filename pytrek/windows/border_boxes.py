from .base import BaseManagedWindow


class BorderBox(BaseManagedWindow):
    def _draw_content(self):
        self.window.box()
