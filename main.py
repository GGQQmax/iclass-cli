# main.py
import argparse
import curses
import asyncio
import sys
from api.auth_module import Authenticator
from api.iclass_api import TronClassAPI
from curses_ui import IClassCursesUI
from cli import handle_cli


def start_ui(stdscr, api):
    ui = IClassCursesUI(api)
    asyncio.run(ui.curses_main(stdscr))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--todo", action="store_true", help="Print todo list")
    parser.add_argument("-c","--courses", action="store_true", help="Print course list")
    parser.add_argument("-b","--bulletins", action="store_true", help="Print bulletins")
    parser.add_argument("-u", "--upload",nargs="?",const="-",help="Upload a file (or read from stdin)")
    parser.add_argument("-s","--submit", action="store_true", help="Summit HomeWork")

    # Global option
    parser.add_argument("--raw", action="store_true", help="Output raw file instead of formatted table")
    parser.add_argument("-p","--page", action="store_true", help="Page of the data. defult is 1")
    parser.add_argument("-z","--size", action="store_true", help="Amount of the data from the page. defult is 10")
    parser.add_argument("-id","--byid", action="store_true", help="Get by id")
    parser.add_argument("-ids","--fileids", action="store_true", help="Send file id as list")


    args = parser.parse_args()

    auth = Authenticator()
    try:
        session = auth.perform_auth()
    except LoginError as e:
        print("Login failed:", e)
    api = TronClassAPI(session)

    # If user provided ANY argument
    if len(sys.argv) > 1:
        asyncio.run(handle_cli(args, api))
        return

    # Otherwise → launch UI
    curses.wrapper(lambda stdscr: start_ui(stdscr,api))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram exited with Ctrl+C")
