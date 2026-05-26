import curses
from ui.ui_base import UIBase
class BulletinsUI(UIBase):
    def __init__(self, api):
        self.api = api

    async def bulletins(self,stdscr):
        result = await self.api.get_bulletins()
        bulletins = result.get("bulletins", [])
        bulletin_options = [f"{b['id']} - {b['title']}" for b in bulletins]
        selected_idx = 0
        while True:
            self.draw_menu(stdscr, selected_idx, bulletin_options + ["Exit"], "📢 Bulletins")
            key = stdscr.getch()
            if key == curses.KEY_UP and selected_idx > 0:
                selected_idx -= 1
            elif key == curses.KEY_DOWN and selected_idx < len(bulletin_options):
                selected_idx += 1
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
        content = content.replace("<p>", "").replace("</p>", "\n").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n").replace("<sub>", "").replace("</sub>", "")
        #get that url
        content = content.replace("<a href=\"", "🔗 ").replace("\" target=\"_blank\">", " - ").replace("</a>", "")
        uploads = selected_bulletin.get("uploads", [])

        # Simple word wrap
        max_width = 80
        wrapped_desc = []
        for line in content.split("\n"):
            while len(line) > max_width:
                wrapped_desc.append(line[:max_width])
                line = line[max_width:]
            wrapped_desc.append(line)


        lines = wrapped_desc + [""] + [f"📎 {u['name']} (Size: {u['size']} bytes)" for u in uploads] + ["", "🔙 Press 'q' to go back"]
        
        offset = 0
        h, w = stdscr.getmaxyx()

        stdscr.clear()
        for i, line in enumerate(lines[offset:offset + h - 2]):
            stdscr.addstr(i + 1, 2, line[:w - 4])
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            return
        if key == ord('d') and uploads:
            # Download all files
            for upload in uploads:
                file_id = upload["reference_id"]
                res = await self.api.download_file(file_id)
                if res:
                    self.show_message(stdscr, f"✅ Downloaded: {upload['name']}")
                else:
                    self.show_message(stdscr, f"❌ Failed to download: {upload['name']}")
            pass
    
