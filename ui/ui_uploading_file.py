import curses
import os
from ui.ui_base import UIBase

class UploadFileUI(UIBase):
    def __init__(self, api):
        self.api = api

    async def upload_file_page(self,stdscr):
        curses.curs_set(1)
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        input_path = ""
        msg = "Enter file path to upload and press Enter: press ESC to go back"
        result = ""
        uploadedIds = []
        while True:
            stdscr.clear()
            stdscr.addstr(1, w // 2 - len("📤 File Upload") // 2, "📤 Filuploadedidse Upload", curses.A_BOLD | curses.A_UNDERLINE)
            stdscr.addstr(3, 2, msg)
            stdscr.addstr(5, 4, input_path)
            if result:
                stdscr.addstr(7, 2, result, curses.A_BOLD)
            stdscr.refresh()

            key = stdscr.getch()

            if key in (curses.KEY_ENTER, ord("\n")):
                input_pathList = input_path.split(',')
                for path in input_pathList:
                    if os.path.isfile(str(path)):
                        try:
                            uploadedId = await self.api.upload_file(path)
                            uploadedIds.append(uploadedId)
                            result = f"✅ Uploaded: ".join(str(x) for x in uploadedIds)
                        except Exception as e:
                            result = f"❌ Upload failed: {str(e)}"
                    else:
                        result = f"❌{path} is Invalid file path. press ESC to go back"
            elif key == 27:  # ESC to go back
                break
            elif key in (curses.KEY_BACKSPACE, 127):
                input_path = input_path[:-1]
            elif 32 <= key <= 126:
                input_path += chr(key)
