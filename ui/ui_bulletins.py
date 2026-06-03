import curses
import re
from ui.ui_base import UIBase
class BulletinsUI(UIBase):
    def __init__(self, api):
        self.api = api

    async def bulletins(self,stdscr, org_mode=False):
        page = 1
        page_size = 10
        selected_idx = 0
        cached_pages = {}

        result = await self.api.get_courses()
        courses = result.get("courses", [])
        course_map = {c['id']: c['name'] for c in courses}

        while True:
            if page not in cached_pages:
                result = await self.api.get_bulletins(org_mode=org_mode, page=page, size=page_size)
                if result.get("error"):
                    self.show_message(stdscr, f"❌ {result['error']}")
                    return
                cached_pages[page] = result

            page_result = cached_pages[page]
            bulletins = page_result.get("bulletins", [])
            total_pages = page_result.get("pages") or page_result.get("total_pages") or 1
            if total_pages == 1 and len(bulletins) == page_size:
                total_pages = page + 1

            if org_mode:  # there is no course name in org mode, so just show the title with (Org Mode) tag
                bulletin_options = [f"{b['title']} (Org Mode)" for b in bulletins]
            else:
                bulletin_options = [f"{course_map.get(b['course_id'], b['course_id'])} - {b['title']}" for b in bulletins]

            selected_idx = min(selected_idx, len(bulletin_options))
            title = f"📢 Bulletins (Page {page}/{total_pages})"
            self.draw_paged_menu(stdscr, selected_idx, bulletin_options + ["Exit"], title, page, total_pages)
            key = stdscr.getch()

            if key == curses.KEY_UP and selected_idx > 0:
                selected_idx -= 1
            elif key == curses.KEY_DOWN and selected_idx < len(bulletin_options):
                selected_idx += 1
            elif key == curses.KEY_RIGHT and page < total_pages:
                page += 1
                selected_idx = 0
            elif key == curses.KEY_LEFT and page > 1:
                page -= 1
                selected_idx = 0
            elif key == ord('o'):
                org_mode = not org_mode
                page = 1
                selected_idx = 0
                cached_pages.clear()
            elif key in [curses.KEY_ENTER, ord('\n')]:
                if selected_idx == len(bulletin_options):
                    break
                selected_bulletin = bulletins[selected_idx]
                await self.bulletins_detail(stdscr, selected_bulletin)

        pass

    async def bulletins_detail(self,stdscr, selected_bulletin):
        stdscr.clear()
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        title = f"📢 {selected_bulletin['title']}"
        content = selected_bulletin.get("content", "")
        #get that url
        content = re.sub(
            r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            r'\n🔗 \2 (\1)',
            content,
            flags=re.DOTALL
        )

        content = content.replace("<p>", "").replace("</p>", "\n").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n").replace("<sub>", "").replace("</sub>", "")
        content = re.sub(r"<[^>]+>", "", content) # remove anything else dont need
        uploads = selected_bulletin.get("uploads", [])
        
        
        # Simple word wrap using terminal width
        h, w = stdscr.getmaxyx()
        wrap_width = max(10, w - 4)
        wrapped_desc = []
        for line in content.split("\n"):
            while len(line) > wrap_width:
                wrapped_desc.append(line[:wrap_width])
                line = line[wrap_width:]
            wrapped_desc.append(line)
        

        lines = wrapped_desc + [""] + [f"📎 {u['name']} (Size: {u['size']} bytes)" for u in uploads] + ["", "🔙 Press 'q' to go back"]
        
        offset = 0
        page_size = max(1, h - 3)
        total_pages = max(1, (len(lines) + page_size - 1) // page_size)

        while True:
            stdscr.clear()
            visible = lines[offset:offset + page_size]
            for i, line in enumerate(visible):
                stdscr.addstr(i + 1, 2, line[:w - 4])

            footer = f"Page {offset // page_size + 1}/{total_pages} | ← Previous page | → Next page | q Back"
            if uploads:
                footer += " | d Download all"
            stdscr.addstr(h - 1, 2, footer[:w - 4], curses.A_BOLD)
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q'):
                return
            elif key == curses.KEY_RIGHT and offset + page_size < len(lines):
                offset = min(offset + page_size, len(lines) - page_size)
            elif key == curses.KEY_LEFT and offset > 0:
                offset = max(0, offset - page_size)
            elif key == curses.KEY_DOWN and offset + page_size < len(lines):
                offset += 1
            elif key == curses.KEY_UP and offset > 0:
                offset -= 1
            elif key == ord('d') and uploads:
                for upload in uploads:
                    file_id = upload["reference_id"]
                    res = await self.api.download_file(file_id)
                    if res:
                        self.show_message(stdscr, f"✅ Downloaded: {upload['name']}")
                    else:
                        self.show_message(stdscr, f"❌ Failed to download: {upload['name']}")
            # Keep offset aligned to page boundaries when page size changes
            total_pages = max(1, (len(lines) + page_size - 1) // page_size)
            offset = min(offset, max(0, len(lines) - page_size))
    
