import curses

from .app import App


def main(stdscr: curses.window):
    app = App(stdscr)
    app.run()


curses.set_escdelay(25)
curses.wrapper(main)
