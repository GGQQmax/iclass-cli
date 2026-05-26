# cli.py
import asyncio
from texttable import Texttable
from datetime import date
import sys
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
    
    if args.submit:
        # Collect file ids to submit. Support stdin ("-") or comma-separated list.
        fileids = []
        if args.id:
            id = args.id
        else:
            print("No activity id provided for submission")
            return
        
        if getattr(args, 'fileids', None):
            # Support: '-' to read file ids from stdin, a list from argparse,
            # or a comma-separated string.
            if isinstance(args.fileids, (list, tuple)):
                # Single '-' in a list means read from stdin
                if len(args.fileids) == 1 and args.fileids[0] == '-':
                    fileids = [line.strip() for line in sys.stdin if line.strip()]
                else:
                    fileids = list(args.fileids)
            else:
                if args.fileids == "-":
                    fileids = [line.strip() for line in sys.stdin if line.strip()]
                else:
                    fileids = [f.strip() for f in str(args.fileids).split(',') if f.strip()]

        if not fileids:
            print("No file ids provided for submission")
            return
        

        try:
            result = await api.submit_homework(id,fileids)
            if args.raw:
                print(result)
            else:
                print(f"Submitted {len(fileids)} file(s): {', '.join(fileids)}")
        except Exception as e:
            print(f"Submission failed: {e}")
        return
    
    if args.bulletins:

        result = await api.get_bulletins()
        if args.raw:
            print(result)
            return
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["l", "l", "l"])
        table.set_cols_valign(["m", "m", "m"])

        # Header row
        table.add_rows([
            ["Title", 'content', 'date']
        ])

        Bulletins = result.get("bulletins", [])

        for Bulletin in Bulletins:
            course_name = Bulletin.get("course_name", "").strip()
            title = Bulletin.get("title", "")
            date = Bulletin.get("date", "")

            table.add_row([course_name, title, date])
        print(table.draw())
        return
    
    if args.upload:
        # Determine input source
        if args.upload == "-":
            # Read from stdin (pipe)
            files = [line.strip() for line in sys.stdin if line.strip()]
        else:
            files = [args.upload]

        if not files:
            print("No files to upload")
            return

        # Upload files (sequential)
        for f in files:
            try:
                uploaded_id = await api.upload_file(f)
                if args.raw:
                    print(uploaded_id)
                else:
                    print(f"Uploaded: {f} -> {uploaded_id}")
            except Exception as e:
                print(f"Failed: {f} -> {e}")

        return

    print("No CLI command matched. Use --help.")

