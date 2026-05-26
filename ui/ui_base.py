import curses
import signal

class UIBase:
    def __init__(self, api):
        self.api = api
        self.selected_idx = 0

    def draw_menu(self,stdscr, selected_idx, options, title):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(1, w//2 - len(title)//2, title, curses.A_BOLD | curses.A_UNDERLINE)

        for idx, option in enumerate(options):
            x = w // 2 - 30
            y = 3 + idx
            if idx == selected_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, option)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, option)
            stdscr.refresh()

    def show_message(self, stdscr, message):
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        stdscr.addstr(h//2, w//2 - len(message)//2, message)
        stdscr.addstr(h//2 + 2, w//2 - 10, "Press any key...")
        stdscr.refresh()
        stdscr.getch()

    def handle_exit(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handle_exit)
