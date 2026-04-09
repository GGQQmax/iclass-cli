import curses
from bs4 import BeautifulSoup
from datetime import datetime
from ui.ui_base import UIBase as BaseUI

class activityHandler(BaseUI):
    async def activityHandler(self,stdscr, activity_id):
        stdscr.clear()
        curses.curs_set(0)

        response = await self.api.get_activitie(activity_id)

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
                    myfileid = await self.get_my_files_ui(stdscr, sumit=True)
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
                    response = await self.api.submit_homework(activity_id, myfileids)
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
                        filepath = await self.api.download(upload.get("reference_id", ""))
                        filepaths.append(filepath)
                    status = f"✅ All files downloaded successfully: {', '.join(filepaths)}"
                except Exception as e:
                    status = f"❌ Download failed: {e}"
