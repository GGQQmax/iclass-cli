# cli.py
import asyncio
from texttable import Texttable
async def handle_cli(args, api):
    """
    Simple CLI dispatcher with optional JSON output
    """

    if args.todo:
        result = await api.get_todos()
        print(result)
        return

    if args.courses:
        result = await api.get_courses()
        print(result)
        return

    if args.upload:
        uploaded_id = await api.upload_file(args.upload)
        print("Uploaded:", uploaded_id)
        return

    if args.nofullui:
        print("no full UI mode triggered")
        return

    print("No CLI command matched. Use --help.")

