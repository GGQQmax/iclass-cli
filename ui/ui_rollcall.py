import curses
from ui.ui_base import UIBase as BaseUI
class RollCallUI(BaseUI):
    def __init__(self, api):
        self.api = api
    async def rollcall_menu(self,stdscr):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        selected_idx = 0
        from api.rollcall import TronClassRollCallAPI

        rollcallAPI = TronClassRollCallAPI(self.api.session)
        rollcall_id , rollcall_type = await rollcallAPI.getRollCall()
        if not rollcall_id:
            self.show_message(stdscr, "❌ No active rollcall found")
            return
        menu_options = [f"{rollcall_id} | {rollcall_type}"]

        while True:
            self.draw_menu(stdscr, selected_idx, menu_options + ["Exit"], "Select a Option")

            key = stdscr.getch()

            if key == curses.KEY_UP and selected_idx > 0:
                selected_idx -= 1
            elif key == curses.KEY_DOWN and selected_idx < len(menu_options):
                selected_idx += 1
            elif key == ord('q'):
                break
            elif key in [curses.KEY_ENTER, ord('\n')]:
                if selected_idx == len(menu_options):
                    break

                if selected_idx == 0:
                    await self.handle_rollcall_type(
                        stdscr,
                        rollcallAPI,
                        rollcall_id,
                        rollcall_type
                    )

    async def handle_rollcall_type(self, stdscr, api, rollcall_id, rollcall_type):
        rollcall_type = str(rollcall_type).lower()

        if "number" in rollcall_type:
            await self.rollcall_number_page(stdscr, rollcall_id)

        elif "radar" in rollcall_type:
            await self.rollcall_radar_page(stdscr, api, rollcall_id)

        else:
            self.show_message(stdscr, f"❌ Unknown type: {rollcall_type}")

    async def rollcall_radar_page(self, stdscr, api, rollcall_id):
        curses.curs_set(0)

        result = "⏳ Submitting radar rollcall..."

        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()

            stdscr.addstr(2, w//2 - 10, "📡 Radar Rollcall", curses.A_BOLD)
            stdscr.addstr(4, 2, f"Rollcall ID: {rollcall_id}")
            stdscr.addstr(6, 2, result)

            stdscr.refresh()

            try:
                res = await api.answer_rollcall_radar(rollcall_id)
                result = f"✅ Success: {res}"
            except Exception as e:
                result = f"❌ Failed: {str(e)}"

            stdscr.addstr(8, 2, "Press any key to go back...")
            stdscr.getch()
            break

    async def rollcall_number_page(self, stdscr, rollcall_id):
        from api.rollcall import TronClassRollCallAPI

        curses.curs_set(1)

        api = TronClassRollCallAPI(self.api.session)

        number = ""
        result = ""

        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()

            stdscr.addstr(1, w//2 - 10, "📱 Rollcall Input", curses.A_BOLD)
            stdscr.addstr(3, 2, f"Rollcall ID: {rollcall_id}")
            stdscr.addstr(5, 2, "Enter number (ESC to go back):")
            stdscr.addstr(6, 4, number)

            if result:
                stdscr.addstr(8, 2, result, curses.A_BOLD)

            stdscr.refresh()

            key = stdscr.getch()

            if key in (curses.KEY_ENTER, ord("\n")):
                try:
                    res = await api.answer_rollcall_number(rollcall_id, int(number))
                    result = f"✅ Success: {res}"
                except Exception as e:
                    result = f"❌ Failed: {str(e)}"

            elif key == 27 or  key == ord('q'):  # ESC and Q
                break

            elif key in (curses.KEY_BACKSPACE, 127):
                number = number[:-1]

            elif 48 <= key <= 57:  # only digits
                number += chr(key)
