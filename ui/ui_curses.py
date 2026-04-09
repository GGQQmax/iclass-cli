import curses
from ui.ui_base import UIBase
from ui.ui_activityHandler import activityHandler

class CursesUI(UIBase):
    def __init__(self, api):
        self.api = api

    async def mycurses(self,stdscr):
        result = await self.api.get_courses()
        courses = result.get("courses", [])
        course_options = [f"{c['id']} - {c['name']}" for c in courses]

        selected_idx = 0
        while True:
            self.draw_menu(stdscr, selected_idx, course_options + ["Exit"], "🎓 Select a Course")
            key = stdscr.getch()
            if key == curses.KEY_UP and selected_idx > 0:
                selected_idx -= 1
            elif key == curses.KEY_DOWN and selected_idx < len(course_options):
                selected_idx += 1
            elif key == ord('q'):
                break
            elif key == ord('u'):
                selected_course = courses[selected_idx]
                await self.show_enrollments(stdscr,selected_course["id"])
                pass
            elif key in [curses.KEY_ENTER, ord('\n')]:
                if selected_idx == len(course_options):
                    break
                selected_course = courses[selected_idx]
                await self.handle_course_actions(stdscr, selected_course["id"])

    async def show_enrollments(self,stdscr, course_id):
        stdscr.clear()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        response = await self.api.get_enrollments(course_id)

        enrollments_meta = []  # Store just ID and preview info
        print("enrollments")
        for enrollments in response["enrollments"]:
            user_id = enrollments.get("user_id", "")
            user = enrollments.get("user","")
            user_name = user.get("name","")
            user_no = user.get("user_no","")
            roles = enrollments.get("roles","")
            preview_line = preview_line = f"👤 {user_id} | {user_name} | {user_no} | {roles[0]}"
            enrollments_meta.append((user_id, preview_line))

        enrollments_meta.append((None, "🔙 Back"))

        selected = 0
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            title = f"👤 enrollments - {course_id}"
            stdscr.addstr(1, w // 2 - len(title) // 2, title, curses.A_BOLD)

            max_visible = h - 6
            top = max(0, selected - max_visible // 2)
            visible_items = enrollments_meta[top:top + max_visible]

            for idx, (_, preview) in enumerate(visible_items):
                y = 3 + idx
                if top + idx == selected:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, 2, preview[:w - 4])
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, 2, preview[:w - 4])


            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(enrollments_meta) - 1:
                selected += 1
            elif key == ord('q'):
                break

    async def handle_course_actions(self,stdscr, course_id):
        stdscr.clear()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        response = await self.api.get_activities(course_id)
        activities_meta = []  # Store just ID and preview info

        for activity in response["activities"]:
            activity_id = activity.get("id", "")
            activity_title = activity.get("title","")
            activity_type = activity.get("type", "")
            deadline = activity.get("deadline", "")
            uploads = activity.get("uploads", [])

            # Preview first upload name if any
            if uploads:
                name = uploads[0].get("name", "")
                preview_line = f"📌 {activity_type} | {activity_title} |  📄 {name}"
            else:
                preview_line = f"📌 {activity_type} | {activity_title} |  No file"

            activities_meta.append((activity_id, preview_line))

        activities_meta.append((None, "🔙 Back"))

        selected = 0
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            title = f"📖 Course Activities - {course_id}"
            stdscr.addstr(1, w // 2 - len(title) // 2, title, curses.A_BOLD)

            max_visible = h - 6
            top = max(0, selected - max_visible // 2)
            visible_items = activities_meta[top:top + max_visible]

            for idx, (_, preview) in enumerate(visible_items):
                y = 3 + idx
                if top + idx == selected:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, 2, preview[:w - 4])
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, 2, preview[:w - 4])

            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(activities_meta) - 1:
                selected += 1
            elif key == ord('q'):
                break
            elif key in [curses.KEY_ENTER, ord("\n")]:
                activity_id, _ = activities_meta[selected]
                if activity_id is None:
                    break
                handler = activityHandler(self.api)
                await handler.activityHandler(stdscr, activity_id)

