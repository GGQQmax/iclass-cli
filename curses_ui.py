import curses
import asyncio
import os
from datetime import datetime
from bs4 import BeautifulSoup

from ui.ui_base import UIBase
from ui.ui_bulletins import BulletinsUI
from ui.ui_todo import todo
from ui.ui_curses import CursesUI
from ui.ui_getfile import GetFileUI
from ui.ui_uploading_file import UploadFileUI
from ui.ui_rollcall import RollCallUI

class IClassCursesUI(UIBase):
    def __init__(self, api):    
        self.api = api

    async def curses_main(self,stdscr):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        selected_idx = 0
        menu_options = [
            "To Do List",
            "My Class",
            "My Files",
            "File Upload",
            "Bulletins",
            "Rollcall"
        ]
        
        while True:
            self.draw_menu(stdscr, selected_idx, menu_options + ["Exit"], "Select a Option")

            key = stdscr.getch()
            if key == curses.KEY_UP and selected_idx > 0:
                selected_idx -= 1
            elif key == curses.KEY_DOWN and selected_idx < len(menu_options):
                selected_idx += 1
            elif key in [curses.KEY_ENTER, ord('\n')]:
                if selected_idx == len(menu_options):
                    break
                if(selected_idx==0):
                    todo_ui = todo(self.api)
                    await todo_ui.getMyToDoList(stdscr)
                    pass
                elif(selected_idx==1):
                    mycurses_ui = CursesUI(self.api)
                    await mycurses_ui.mycurses(stdscr)
                    pass
                elif(selected_idx==2):
                    getfile_ui = GetFileUI(self.api)
                    await getfile_ui.get_my_files_ui(stdscr)
                    pass
                elif(selected_idx==3):
                    upload_ui = UploadFileUI(self.api)
                    await upload_ui.upload_file_page(stdscr)
                    pass
                elif(selected_idx==4):
                    bulletins_ui = BulletinsUI(self.api)
                    await bulletins_ui.bulletins(stdscr)
                elif(selected_idx==5):
                    rollcall_ui = RollCallUI(self.api)
                    await rollcall_ui.rollcall_menu(stdscr)
        pass

