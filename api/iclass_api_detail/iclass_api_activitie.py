import requests
import json

class TronClassActivityAPI:
    def __init__(self, session):
        self.session = session

    async def get_activities(self,course_id):
        url = f'https://iclass.tku.edu.tw/api/courses/{course_id}/activities?sub_course_id=0'
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching courses: {str(e)}"}

    async def get_activitie(self,activities_id):
        url = f'https://iclass.tku.edu.tw/api/activities/{activities_id}?sub_course_id=0'
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching courses: {str(e)}"}

    async def submit_homework(self, activity_id:int, upload_ids:list):
        url = f'https://iclass.tku.edu.tw/api/course/activities/{activity_id}/submissions'

        headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://iclass.tku.edu.tw',
        }

        payload = {
            "comment": "",
            "uploads": upload_ids,  # List of uploaded file IDs
            "slides": [],
            "is_draft": False,
            "mode": "normal",
            "other_resources": [],
            "uploads_in_rich_text": []
        }

        response = self.session.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 201:
            return {"Submission successful":response.status_code}
        else:
            return {"Submission failed": response.status_code, "details": response.text}
    
    async def read_activity(self, activity_id: int, course_id: int = None):
        """
        Mark a course activity / upload as read.
        POST https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}
        """
        activity_details = await self.get_activitie(activity_id)  # Get activity details to determine if it's an upload or has a duration
        if not isinstance(activity_details, dict):
            return {"error": "Invalid activity details received"}
        if "error" in activity_details:
            return activity_details

        if not course_id and activity_details.get("course_id"):
            course_id = activity_details.get("course_id")

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/learning-activity/full-screen"

        # Check if activity is a video (either online_video type, duration in data, or upload containing video)
        is_video = False
        if activity_details.get("type") in ("online_video", "video"):
            is_video = True
        elif isinstance(activity_details.get("data"), dict) and activity_details["data"].get("duration") is not None:
            is_video = True
        elif isinstance(activity_details.get("uploads"), list):
            for upload in activity_details["uploads"]:
                if isinstance(upload, dict) and (upload.get("videos") or upload.get("type") == "video"):
                    is_video = True
                    break

        if is_video:
            return await self.read_video_activity(activity_id, course_id=course_id, activity_details=activity_details)

        uploads = activity_details.get("uploads")
        if uploads and isinstance(uploads, list) and len(uploads) > 0:
            results = []
            for upload in uploads:
                if isinstance(upload, dict):
                    res = await self.read_file_activity(
                        activity_id,
                        course_id=course_id,
                        upload_id=upload.get("id"),
                        activity_details=activity_details,
                    )
                    print(f"Marked upload {upload.get('id')} of activity {activity_id} as read: {res}")
                    results.append(res)
            if len(results) == 1:
                return results[0]
            return {"success": True, "results": results}

        # Fallback for plain activity types
        url = f"https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}"
        try:
            response = self.session.post(url, headers=headers, json={})
            print(f"Response for marking activity {activity_id} as read: {response.status_code}, {response.text}")

            if response.ok:
                try:
                    return response.json()
                except ValueError:
                    return {"success": True, "status_code": response.status_code}
            else:
                try:
                    return {"error": f"Failed with status {response.status_code}", "details": response.json()}
                except ValueError:
                    return {"error": f"Failed with status {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error marking activity as read: {str(e)}"}

    async def read_file_activity(self, activity_id: int, course_id: int = None, upload_id: int = None, activity_details: dict = None):
        """
        Mark a file activity as read.
        POST https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}
        """
        url = f"https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}"
        if activity_details is None:
            activity_details = await self.get_activitie(activity_id)

        if not isinstance(activity_details, dict):
            return {"error": "Invalid activity details received"}
        if "error" in activity_details:
            return activity_details

        if not course_id and activity_details.get("course_id"):
            course_id = activity_details.get("course_id")

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/learning-activity/full-screen"

        if upload_id is None and isinstance(activity_details.get("uploads"), list) and len(activity_details["uploads"]) > 0:
            first_upload = activity_details["uploads"][0]
            if isinstance(first_upload, dict):
                upload_id = first_upload.get("id")

        payload = {"upload_id": upload_id} if upload_id is not None else {}

        try:
            response = self.session.post(url, headers=headers, json=payload)
            if response.ok:
                try:
                    return response.json()
                except ValueError:
                    return {"success": True, "status_code": response.status_code}
            else:
                try:
                    return {"error": f"Failed with status {response.status_code}", "details": response.json()}
                except ValueError:
                    return {"error": f"Failed with status {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error marking file activity as read: {str(e)}"}

    async def read_video_activity(self, activity_id: int, course_id: int = None, activity_details: dict = None):
        """
        Mark a video activity as read.
        POST https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}
        """
        url = f"https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}"
        if activity_details is None:
            activity_details = await self.get_activitie(activity_id)

        if not isinstance(activity_details, dict):
            return {"error": "Invalid activity details received"}
        if "error" in activity_details:
            return activity_details

        if not course_id and activity_details.get("course_id"):
            course_id = activity_details.get("course_id")

        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/learning-activity/full-screen"

        # 1. URL video: duration is saved in activity_details["data"]["duration"]
        duration = None
        data = activity_details.get("data")
        if isinstance(data, dict) and data.get("duration") is not None:
            duration = data["duration"]

        # 2. File video: duration is saved in upload["videos"][...]["duration"]
        if not duration:
            uploads = activity_details.get("uploads")
            if isinstance(uploads, list):
                for upload in uploads:
                    if not isinstance(upload, dict):
                        continue
                    videos = upload.get("videos")
                    if isinstance(videos, list) and len(videos) > 0:
                        for v in videos:
                            if isinstance(v, dict) and v.get("duration") is not None:
                                duration = v["duration"]
                                break
                    if duration is not None:
                        break
                    if upload.get("duration") is not None:
                        duration = upload["duration"]
                        break

        payloads = [{}]
        if duration is not None:
            try:
                duration_float = float(duration)
                duration_seconds = int(duration_float)
                if duration_seconds > 0:
                    payloads = [
                        {"start": start, "end": min(start + 100, duration_seconds), "duration": duration}
                        for start in range(0, duration_seconds, 100)
                    ] or [{"start": 0, "end": duration_seconds, "duration": duration}]
                elif duration_float > 0:
                    payloads = [{"start": 0, "end": 1, "duration": duration}]
            except (ValueError, TypeError):
                pass

        try:
            results = []
            for payload in payloads:
                response = self.session.post(url, headers=headers, json=payload)
                print(f"Response for marking video activity {activity_id} as read: {response.status_code}, {response.text}")

                if response.ok:
                    try:
                        result = response.json()
                    except ValueError:
                        result = {"success": True, "status_code": response.status_code}
                    results.append(result)
                else:
                    try:
                        details = response.json()
                    except ValueError:
                        details = response.text
                    error = {"error": f"Failed with status {response.status_code}", "details": details}
                    if len(payloads) > 1:
                        error["completed_segments"] = len(results)
                        error["failed_segment"] = {"start": payload.get("start"), "end": payload.get("end")}
                    return error

            if len(results) == 1:
                return results[0]
            return {"success": True, "segments": results}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error marking video activity as read: {str(e)}"}

    async def read_all_activities(self, course_id: int):
        try:
            activities_response = await self.get_activities(course_id)
        except Exception as e:
            return {"error": f"Error fetching activities: {str(e)}"}

        activities = activities_response.get("activities", [])
        read_results = []
        

        for activity in activities:
            activity_id = activity.get("id")
            if activity_id is not None:
                try:
                    result = await self.read_activity(activity_id, course_id=course_id)
                    read_results.append({"activity_id": activity_id, "result": result})
                except Exception as e:
                    read_results.append({"activity_id": activity_id, "error": str(e)})

        return {"read_results": read_results}