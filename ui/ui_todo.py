import curses
from datetime import datetime
from zoneinfo import ZoneInfo
from ui.ui_base import UIBase as BaseUI
from ui.ui_activityHandler import activityHandler
class todo(BaseUI):
    def __init__(self, api):
        self.api = api

    async def getMyToDoList(self,stdscr):       
        stdscr.clear()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        result = await self.api.get_todos()
        todos = result.get("todo_list", [])
        if not todos:
            stdscr.addstr(2, 2, "No pending tasks found.", curses.A_BOLD)
            stdscr.getch()
            return

        tasks = []
        for t in todos:
            due = t.get("end_time", "")
            try:
                # Handle Z suffix from API
                utc_time = datetime.fromisoformat(
                    due.replace("Z", "+00:00")
                )

                taiwan_time = utc_time.astimezone(
                    ZoneInfo("Asia/Taipei")
                )

                due_str = taiwan_time.strftime("%Y-%m-%d %H:%M")

            except Exception:
                due_str = due

            tasks.append(
                f"📄 {t['title']} | ⏰ {due_str}"
            )
        tasks.append("🔙 Back")

        selected = 0
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            stdscr.addstr(1, w // 2 - len("📋 To Do List") // 2, "📋 To Do List", curses.A_BOLD)

            max_visible = h - 6
            top = max(0, selected - max_visible // 2)
            for idx, task in enumerate(tasks[top:top + max_visible]):
                y = 3 + idx
                text = task[:w - 4]
                if top + idx == selected:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, 2, text)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, 2, text)

            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(tasks) - 1:
                selected += 1
            elif key == ord('q'):
                break
            elif key in [curses.KEY_ENTER, ord('\n')]:
                if selected == len(tasks) - 1:
                    break
                else:
                    activity_id = todos[selected].get("id")
                    if activity_id:
                        handler = activityHandler(self.api)
                        await handler.activityHandler(stdscr, activity_id)
                    else:
                        self.show_message(stdscr, "❌ Invalid activity ID")
