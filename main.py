# main.py
import asyncio
import curses
import os
import signal
from api.auth_module import Authenticator
from api.iclass_api import TronClassAPI
from bs4 import BeautifulSoup
from datetime import datetime

def handle_exit(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_exit)

def draw_menu(stdscr, selected_idx, options, title):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, w//2 - len(title)//2, title, curses.A_BOLD | curses.A_UNDERLINE)

    for idx, option in enumerate(options):
        x = w // 2 - 30
        y = 3 + idx
        if idx == selected_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, option)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, option)
    stdscr.refresh()

async def curses_main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    stdscr.addstr(0, 0, "🔐 Logging in...", curses.A_BOLD)
    stdscr.refresh()
    #handle api
    auth = Authenticator()
    session = auth.perform_auth()
    api = TronClassAPI(session)
    
    selected_idx = 0
    menu_options = ["To Do List","My Class","My Files","File Upload"]
    while True:
        draw_menu(stdscr, selected_idx, menu_options + ["Exit"], "Select a Option")
        
        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(menu_options):
            selected_idx += 1
        elif key in [curses.KEY_ENTER, ord('\n')]:
            if selected_idx == len(menu_options):
                break
            if(selected_idx==0):
                await getMyToDoList(stdscr,api)
                pass
            elif(selected_idx==1):
                await mycurses(stdscr,api)
                pass
            elif(selected_idx==2):
                await get_my_files_ui(stdscr, api)
                pass
            elif(selected_idx==3):
                await upload_file_page(stdscr, api)
                pass
    pass

async def getMyToDoList(stdscr, api):
    stdscr.clear()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    result = await api.get_todos()
    todos = result.get("todo_list", [])
    if not todos:
        stdscr.addstr(2, 2, "No pending tasks found.", curses.A_BOLD)
        stdscr.getch()
        return

    tasks = []
    for t in todos:
        due = t.get("end_time", "")
        try:
            # Format ISO 8601 to readable time
            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
            due_str = due_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            due_str = due

        tasks.append(
            f"📄 {t['title']} | ⏰ {due_str}"
        )
    tasks.append("🔙 Back")

    selected = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(1, w // 2 - len("📋 To Do List") // 2, "📋 To Do List", curses.A_BOLD)

        max_visible = h - 6
        top = max(0, selected - max_visible // 2)
        for idx, task in enumerate(tasks[top:top + max_visible]):
            y = 3 + idx
            text = task[:w - 4]
            if top + idx == selected:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, 2, text)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, 2, text)

        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(tasks) - 1:
            selected += 1
        elif key == ord('q'):
            break
        elif key in [curses.KEY_ENTER, ord('\n')]:
            if selected == len(tasks) - 1:
                break
            await activityHandler(stdscr, api, todos[selected]["id"])

async def activityHandler(stdscr, api, activity_id):
    stdscr.clear()
    curses.curs_set(0)

    response = await api.get_activitie(activity_id)

    # Extract relevant fields
    activity_type = response.get("type", "N/A")
    deadline = response.get("end_time", "N/A")
    try:
        due_dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
        due_str = due_dt.strftime("%Y-%m-%d %H:%M")
    except:
        due_str = deadline

    upload_list = ["No files uploaded"]
    uploads = response.get("uploads", [])
    if uploads is not None:
        upload_list = [
            f"{upload.get('name', 'N/A')} (ID: {upload.get('reference_id', 'N/A')})"
            for upload in uploads
        ]

    raw_description = response.get("data", {}).get("description", "")
    content = response.get("data", {}).get("content", "")
    link = response.get("data", {}).get("link", "")
    # Format description
    if content: 
        raw_description = content + "\n\n" + raw_description
    if link:
        raw_description += f"\n\n🔗 Link: {link}"
    if not raw_description:
        raw_description = "No description provided."
    
    # Parse HTML description if present
    soup = BeautifulSoup(raw_description, "html.parser")
    description = soup.get_text(separator='\n').strip()

    # Wrap description lines
    wrapped_desc = []
    for line in description.splitlines():
        while len(line) > 60:
            wrapped_desc.append(line[:60])
            line = line[60:]
        wrapped_desc.append(line)

    lines = [
        f"🆔 ID: {response.get('id', 'N/A')}",
        f"📂 Type: {activity_type}",
        f"⏰ Deadline: {due_str}",
        "",
        "📎 Uploaded Files:"
    ] + upload_list + [
        "",
        "📝 Description:"
    ] + wrapped_desc + [
        "",
        "🔙 Press 'q' to go back" + (" | 💾 Press 'd' to download all files" if uploads else "") +
        (" | 📥 Press 'a' to assign files for homework" if activity_type == "homework" else "") +
        (" | 📤 Press 's' to submit homework" if activity_type == "homework" else "")
    ]

    offset = 0
    h, w = stdscr.getmaxyx()
    status = ""
    myfileids = []
    while True:
        stdscr.clear()
        for i, line in enumerate(lines[offset:offset + h - 2]):
            stdscr.addstr(i + 1, 2, line[:w - 4])
        if status:
            stdscr.addstr(h - 1, 2, status[:w - 4], curses.A_BOLD)
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == curses.KEY_UP and offset > 0:
            offset -= 1
        elif key == curses.KEY_DOWN and offset < len(lines) - h + 2:
            offset += 1
        elif key == ord('a') and activity_type == "homework":
            status = "📤 Selecteing files..."
            stdscr.refresh()
            try:
                myfileid = await get_my_files_ui(stdscr, api, sumit=True)
                if not myfileid:
                    status = "❌ No files selected"
                    continue
                myfileids.append(myfileid)
                status = f"✅ Files selected: {', '.join(map(str, myfileids))}"
            except Exception as e:
                status = f"❌ Selected failed: {e}"
        elif key == ord('s') and activity_type=="homework":
            status = "📤 Submitting homework..."
            stdscr.refresh()
            try:
                response = await api.submit_homework(activity_id, myfileids)
                print(response)
                if "success" in response:
                    status = "✅ Submission successful!"
                else:   
                    status = f"❌ Submission failed: {response}"
            except Exception as e:
                status = f"❌ Submission failed: {e}"
        elif key == ord('d') and uploads:
            status = "⬇️ Downloading all files..."
            stdscr.refresh()
            try:
                filepaths = []
                for upload in uploads:
                    filepath = await api.download(upload.get("reference_id", ""))
                    filepaths.append(filepath)
                status = f"✅ All files downloaded successfully: {', '.join(filepaths)}"
            except Exception as e:
                status = f"❌ Download failed: {e}"

async def upload_file_page(stdscr, api):
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
                        uploadedId = await api.upload_file(path)
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

async def mycurses(stdscr,api):
    result = await api.get_courses()
    courses = result.get("courses", [])
    course_options = [f"{c['id']} - {c['name']}" for c in courses]

    selected_idx = 0
    while True:
        draw_menu(stdscr, selected_idx, course_options + ["Exit"], "🎓 Select a Course")
        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(course_options):
            selected_idx += 1
        elif key == ord('q'):
            break
        elif key in [curses.KEY_ENTER, ord('\n')]:
            if selected_idx == len(course_options):
                break
            selected_course = courses[selected_idx]
            await handle_course_actions(stdscr, api, selected_course["id"])

async def handle_course_actions(stdscr, api, course_id):
    stdscr.clear()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    response = await api.get_activities(course_id)
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
            await activityHandler(stdscr, api, activity_id)

async def get_my_files_ui(stdscr, api, sumit=False):
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
                response = await api.get_my_files(5, page)
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
                await api.deleteUpload([file_ref])
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
                        filepath = await api.myfiledownload(file_ref)
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

if __name__ == '__main__':
    try:
        curses.wrapper(lambda stdscr: asyncio.run(curses_main(stdscr)))
    except KeyboardInterrupt:
        print("\nProgram exited with Ctrl+C")
