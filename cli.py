# cli.py
import asyncio
from texttable import Texttable
async def handle_cli(args, api):
    """
    Simple CLI dispatcher with optional JSON output
    """

    if args.todo:
        result = await api.get_todos()
        if args.raw:
            print(result)
            return
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "l", "l", "l"])
        table.set_cols_valign(["m", "m", "m", "m"])

        # Header row
        table.add_rows([
            ["Course", "Title", "Due", "Id"]
        ])

        todolist = result.get("todo_list", [])

        for todo in todolist:
            course_name = todo.get("course_name", "").strip()
            title = todo.get("title", "")
            due = todo.get("end_time", "")
            id = todo.get("id", "")

            table.add_row([course_name, title, due,id])
        print(table.draw())
        return

    if args.courses:
        result = await api.get_courses()
        if args.raw:
            print(result)
            return
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "l", "l"])
        table.set_cols_valign(["m", "m", "m"])

        # Header row
        table.add_rows([
            ["Course", "Title", "Due"]
        ])

        Courses = result.get("courses", [])

        for Course in Courses:
            course_name = Course.get("name", "").strip()
            title = Course.get("title", "")
            
            table.add_row([course_name, title, due])
        print(table.draw())
        return

    if args.upload:
        uploaded_id = await api.upload_file(args.upload)
        print("Uploaded:", uploaded_id)
        return

    print("No CLI command matched. Use --help.")

