import curses

from .color_pairs import ColorPair
from .enterprise import Enterprise
from .galaxies import Galaxy, LocalMap
from .settings import settings
from .states import State
from .windows.base import AbstractFocusableWindow
from .windows.border_boxes import BorderBox
from .windows.layout import LayoutMetric, LayoutValueComponent
from .windows.sensors.short_range import ShortRangeDisplay
from .windows.title_screen import TitleScreen


class ManagedWindow(AbstractFocusableWindow):
    def _draw_content(self):
        self.window.addnstr('ALPHA', 5)


class App:
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self._galaxy: Galaxy | None = None
        self._enterprise = Enterprise()
        self._local_map: LocalMap | None = None
        short_range_sensors_border_box = BorderBox(
            parent=stdscr,
            height=[
                LayoutValueComponent(10, LayoutMetric.CHARACTERS),
            ],
            width=[
                LayoutValueComponent(33, LayoutMetric.CHARACTERS),
            ],
            title='Short-Range Sensors',
        )
        long_range_sensors_border_box = BorderBox(
            parent=stdscr,
            left=[
                LayoutValueComponent(33, LayoutMetric.CHARACTERS),
            ],
            height=[
                LayoutValueComponent(5, LayoutMetric.CHARACTERS),
            ],
            width=[
                LayoutValueComponent(33, LayoutMetric.CHARACTERS),
            ],
            title='Long-Range Sensors',
        )
        message_log_border_box = BorderBox(
            parent=stdscr,
            left=[
                LayoutValueComponent(66, LayoutMetric.CHARACTERS),
            ],
            height=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
            ],
            width=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-66, LayoutMetric.CHARACTERS),
            ],
        )
        controls_border_box = BorderBox(
            parent=stdscr,
            top=[
                LayoutValueComponent(100, LayoutMetric.PERCENTAGE),
                LayoutValueComponent(-8, LayoutMetric.CHARACTERS),
            ],
            height=[
                LayoutValueComponent(8, LayoutMetric.CHARACTERS),
            ],
            width=[
                LayoutValueComponent(66, LayoutMetric.CHARACTERS),
            ],
        )
        self._short_range_display = ShortRangeDisplay(
            parent=short_range_sensors_border_box,
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
            enterprise=self._enterprise,
        )
        self._game_windows = (
            short_range_sensors_border_box,
            long_range_sensors_border_box,
            message_log_border_box,
            controls_border_box,
            self._short_range_display,
        )
        self._windows = list(self._game_windows)
        self.title_screen = TitleScreen(
            parent=stdscr,
            height=[LayoutValueComponent(100, LayoutMetric.PERCENTAGE)],
            width=[LayoutValueComponent(100, LayoutMetric.PERCENTAGE)],
        )
        self._windows = [self.title_screen]
        self._focused_window = self.title_screen

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
                        return self._focused_window.handle_key(key)
            case State.RESIZE:
                self.stdscr.clear()
                self.stdscr.refresh()
                if self._local_map is not None:
                    assert self._enterprise is not None
                    self._local_map.draw(
                        self._short_range_display.window,
                        self._enterprise.sector_coordinates,
                    )
                for window in self._windows:
                    window.place()
            case State.CREATE_GALAXY:
                self._enterprise = Enterprise()
                self._galaxy = Galaxy()
                quadrant_map = self._galaxy.quadrants
                initial_quadrant = self._enterprise.quadrant_coordinates
                initial_sector = self._enterprise.sector_coordinates
                self._local_map = LocalMap(
                    quadrant=quadrant_map[initial_quadrant],
                    player_sector_coordinates=initial_sector,
                )
                self.title_screen.set_orders(self._galaxy.orders)
            case State.ENTER_GALAXY:
                if self._local_map is not None:
                    assert self._enterprise is not None
                    self._windows = self._game_windows
                    self._short_range_display.set_local_map(
                        self._local_map,
                    )
            case _:
                pass
        return State.STANDARD

    def run(self):
        """Launches the main loop, continuing until a termination occurs."""
        state = State.STANDARD
        curses.curs_set(0)
        # Initialise colours:
        if curses.can_change_color():
            background_color = curses.COLOR_BLACK
            klingon_color = curses.COLOR_GREEN
            text_color = curses.COLOR_WHITE
        else:
            background_color = curses.COLOR_BLACK
            klingon_color = curses.COLOR_GREEN
            text_color = curses.COLOR_WHITE
        curses.init_pair(
            ColorPair.TEXT,
            text_color,
            background_color,
        )
        curses.init_pair(
            ColorPair.KLINGON,
            klingon_color,
            background_color,
        )
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
