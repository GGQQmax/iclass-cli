import curses
from ui.ui_base import UIBase

class GetFileUI(UIBase):
    def __init__(self, api):
        self.api = api
    async def get_my_files_ui(self,stdscr, sumit=False):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        page = 1
        selected = 0
        cached_pages = {}

        while True:
            stdscr.clear()
            stdscr.addstr(1, 2, f"📁 My Files - Page {page}", curses.A_BOLD)

            if page not in cached_pages:
                try:
                    response = await self.api.get_my_files(5, page)
                    cached_pages[page] = response
                except Exception as e:
                    stdscr.addstr(3, 2, f"❌ Failed to fetch files: {e}")
                    stdscr.refresh()
                    stdscr.getch()
                    return

            response = cached_pages[page]
            uploads = response.get("uploads", [])
            max_pages = response.get("pages", 1)

            entries = []
            file_ids = []  # map entries to file reference IDs

            for upload in uploads:
                name = upload.get("name", "Unnamed")
                file_id = upload.get("id", "N/A")  # use reference_id if available
                size_kb = upload.get("size", 0) // 1024
                date = upload.get("created_at", "N/A")
                entries.append(f"📄 {name} ({file_id}) - {size_kb} KB - {date}")
                file_ids.append(file_id)

            # Add navigation
            entries.append("➡️ Next Page" if page < max_pages else "🔙 Back")
            entries.append("🔙 Back" if page < max_pages else "")

            h, w = stdscr.getmaxyx()
            top = max(0, selected - (h - 5) // 2)
            visible = entries[top:top + h - 4]

            for idx, entry in enumerate(visible):
                y = 3 + idx
                if top + idx == selected:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, 2, entry[:w - 4])
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(y, 2, entry[:w - 4])

            if sumit:
                stdscr.addstr(h - 2, 2, "Press 'enter' to select file for submission", curses.A_BOLD)

            stdscr.refresh()
            key = stdscr.getch()

            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(entries) - 1:
                selected += 1
            elif key == curses.KEY_RIGHT and page < max_pages:
                page += 1
                selected = 0
            elif key == curses.KEY_LEFT and page > 1:
                page -= 1
                selected = 0
            elif key == curses.KEY_DC:  # Delete key
                try:
                    file_ref = file_ids[selected]
                    await self.api.deleteUpload([file_ref])
                    cached_pages.pop(page, None)
                    stdscr.clear()
                    stdscr.addstr(3, 2, f"✅ File deleted successfully.")
                except Exception as e:
                    stdscr.clear()
                    stdscr.addstr(3, 2, f"❌ File deletion failed: {e}")
                stdscr.addstr(5, 2, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
            elif key in [curses.KEY_ENTER, ord("\n")]:
                if selected == len(entries) - 2:
                    if page < max_pages:
                        page += 1
                        selected = 0
                    else:
                        break
                elif selected == len(entries) - 1:
                    if page > 1:
                        page -= 1
                        selected = 0
                    else:
                        break
                else:
                    # Download selected file
                    if sumit:
                        return file_ids[selected]
                    else:
                        file_ref = file_ids[selected]
                        try:
                            filepath = await self.api.myfiledownload(file_ref)
                            stdscr.clear()
                            stdscr.addstr(3, 2, f"✅ Downloaded to: {filepath}")
                        except Exception as e:
                            stdscr.clear()
                            stdscr.addstr(3, 2, f"❌ Download failed: {e}")
                        stdscr.addstr(5, 2, "Press any key to continue...")
                        stdscr.refresh()
                        stdscr.getch()
            elif key == ord('q'):
                break
