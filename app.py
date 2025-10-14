import curses

from states import State
from windows.base import BaseManagedWindow
from windows.border_boxes import BorderBox
from windows.layout import LayoutMetric, LayoutValueComponent
from windows.main_screen import MainScreen


class ManagedWindow(BaseManagedWindow):
    def _draw_content(self):
        self.window.addnstr('ALPHA', 5)


class App:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        main_screen_border_box = BorderBox(
            parent=stdscr,
            height=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-8, LayoutMetric.CHARACTERS),
            ],
            width=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-34, LayoutMetric.CHARACTERS),
            ],
        )
        secondary_screen_border_box = BorderBox(
            parent=stdscr,
            left=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-34, LayoutMetric.CHARACTERS),
            ],
            height=[
                LayoutValueComponent(10, LayoutMetric.CHARACTERS),
            ],
            width=[
                LayoutValueComponent(34, LayoutMetric.CHARACTERS),
            ],
        )
        message_log_border_box = BorderBox(
            parent=stdscr,
            top=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-8, LayoutMetric.CHARACTERS),
            ],
            height=[
                LayoutValueComponent(8, LayoutMetric.CHARACTERS),
            ],
            width=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-34, LayoutMetric.CHARACTERS),
            ],
        )
        options_menu_border_box = BorderBox(
            parent=stdscr,
            top=[
                LayoutValueComponent(10, LayoutMetric.CHARACTERS),
            ],
            left=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-34, LayoutMetric.CHARACTERS),
            ],
            height=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-10, LayoutMetric.CHARACTERS),
            ],
            width=[
                LayoutValueComponent(34, LayoutMetric.CHARACTERS),
            ],
        )
        self._windows = (
            main_screen_border_box,
            secondary_screen_border_box,
            message_log_border_box,
            options_menu_border_box,
            MainScreen(
                parent=main_screen_border_box,
                top=[
                    LayoutValueComponent(1, LayoutMetric.CHARACTERS),
                ],
                left=[
                    LayoutValueComponent(1, LayoutMetric.CHARACTERS),
                ],
                height=[
                    LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                    LayoutValueComponent(-2, LayoutMetric.CHARACTERS),
                ],
                width=[
                    LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                    LayoutValueComponent(-2, LayoutMetric.CHARACTERS),
                ],
            ),
        )
        self._windows = list(self._windows)

    def _loop_iteration(self, state: State):
        assert state != State.TERMINATE
        for window in self._windows:
            window.draw()
        match state:
            case State.STANDARD:
                key = self.stdscr.getch()
                match key:
                    case curses.KEY_F1:
                        raise Exception([x.debug_draw_count for x in self._windows])
                    case curses.KEY_F2:
                        raise Exception([x.window.getmaxyx() for x in self._windows])
                    case curses.KEY_F3:
                        raise Exception([x._parent_window.getmaxyx() for x in self._windows])
                    case curses.KEY_RESIZE:
                        return State.RESIZE
                    case 27:  # Esc
                        return State.TERMINATE
                    case _:
                        pass
            case State.RESIZE:
                self.stdscr.clear()
                self.stdscr.refresh()
                for window in self._windows:
                    window.place()
        return State.STANDARD

    def run(self):
        """Launches the main loop, continuing until a termination occurs."""
        state = State.STANDARD
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        self.stdscr.clear()
        self.stdscr.refresh()
        for window in self._windows:
            window.place()
        while state != State.TERMINATE:
            try:
                state = self._loop_iteration(state)
            except KeyboardInterrupt:
                state = State.TERMINATE


def main(stdscr: curses.window):
    app = App(stdscr)
    app.run()


curses.set_escdelay(25)
curses.wrapper(main)
