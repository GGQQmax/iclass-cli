import json
import os
import requests
import urllib.parse
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from pathlib import Path

class TronClassAPI:
    def __init__(self, session):
        self.session = session

    async def get_todos(self):
        todos_url = "https://iclass.tku.edu.tw/api/todos"
        try:
            response = self.session.get(todos_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching todos: {str(e)}"}

    async def get_bulletins(self,org_mode:bool=False,start_date=None,end_date=None,page:int=1,size:int=10,course_ids:list=[]):
        base_url = 'https://iclass.tku.edu.tw/api/course-bulletins'
        if org_mode:
            base_url = 'https://iclass.tku.edu.tw/api/org-bulletin/bulletins'

        if end_date == None:
            end_date = date.today()
        
        if start_date == None:
            start_date = end_date - relativedelta(months=1)#one_month_ago
        
        conditions = {}
        if start_date == "" or end_date == "":
            # keep it empty string if user want to use default value
            conditions = {
            "start_date":"",
            "end_date": "",
            "keyword": "",
            "course_ids": course_ids
            }

        else:
            conditions = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "keyword": "",
            "course_ids": course_ids
            }

        query_string = urllib.parse.urlencode({
            "conditions": json.dumps(conditions),
            "page": page,
            "page_size": size
        })

        url = f"{base_url}?{query_string}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching bulletins: {str(e)}"}

    async def fileDownloader(self,url,downloads_dir=None):
        response = self.session.get(url, stream=True)

        # Get filename from Content-Disposition (RFC 5987 format)
        cd = response.headers.get('Content-Disposition')
        filename = 'downloaded_file'  # fallback

        if cd and "filename*=" in cd:
            encoded_filename = cd.split(";")[-1]
            encoded_filename = encoded_filename.replace(" filename=UTF-8''","")
            filename = urllib.parse.unquote(encoded_filename)

        if downloads_dir is None:
            downloads_dir = Path.home() / 'Downloads'

        os.makedirs(downloads_dir, exist_ok=True)  # Create if it doesn't exist

        file_path = downloads_dir / filename

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return str(file_path)

    async def download(self, reference_id):
        url = f"https://iclass.tku.edu.tw/api/uploads/reference/{reference_id}/blob"
        file_path = await self.fileDownloader(url)
        return file_path
    
    async def myfiledownload(self, file_id):
        url = f"https://iclass.tku.edu.tw/api/uploads/{file_id}/blob"
        file_path = await self.fileDownloader(url)
        return file_path

    async def get_courses(self):
        url = 'https://iclass.tku.edu.tw/api/my-courses?conditions={"status":["ongoing"]}'
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching courses: {str(e)}"}

    async def get_enrollments(self,course_id,data:dict=None):
        url = f"https://iclass.tku.edu.tw/api/course/{course_id}/enrollments"
        """
        data example:
        data = {"fields":"id,user(id,email,name,nickname,user_no,comment,grade(id,name),klass(id,name,code),department(id,name,code),org(id,name),program(id,name),user_attributes(tag)),roles,aliases,retake_status,seat_number,data,imported_from"}
        """
        try:
            if data is not None:
                response = self.session.post(
                url,
                json=data,
                headers={"Content-Type": "application/json;charset=UTF-8"}
                )
            else:
                response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching enrollments: {str(e)}"}
    
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
            return {"Submission failed", response.status_code, response.text}

    async def get_my_files(self,numberOfRequest,page):
        url = "https://iclass.tku.edu.tw/api/user/resources?conditions={%22keyword%22:%22%22,%22includeSlides%22:false,%22limitTypes%22:[%22file%22,%22video%22,%22document%22,%22image%22,%22audio%22,%22scorm%22,%22evercam%22,%22swf%22,%22wmpkg%22,%22link%22],%22fileType%22:%22all%22,%22parentId%22:0,%22sourceType%22:%22MyResourcesFile%22,%22no-intercept%22:true}&page="+str(page)+"&page_size="+str(numberOfRequest)
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching courses: {str(e)}"}

    async def upload_file(self,file_path:str):
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
        except:
            return "unable to find file"
        
        metadata_url = "https://iclass.tku.edu.tw/api/uploads"

        headers_metadata = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://iclass.tku.edu.tw",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)..."
        }

        metadata_payload = {
            "name": file_name,
            "size": file_size,
            "parent_type": None,
            "parent_id": 0,
            "is_scorm": False,
            "is_wmpkg": False,
            "source": "",
            "is_marked_attachment": False,
            "embed_material_type": ""
        }
        response_metadata = self.session.post(
            metadata_url,
            headers=headers_metadata,
            data=json.dumps(metadata_payload)
        )

        if response_metadata.status_code != 201:
            print("❌ Failed to get upload URL")
            print(response_metadata.status_code, response_metadata.text)
            return {"error":f"Failed to get upload URL, status_code:{response_metadata.status_code}"}

        upload_info = response_metadata.json()
        upload_url = upload_info["upload_url"]
        upload_file_name = upload_info["name"]
        upload_file_id = upload_info["id"]
        upload_file_type = upload_info["type"]

        with open(file_path, 'rb') as f:
            files = {
                'file': (upload_file_name, f, upload_file_type)
            }
            headers_upload = {
                "Origin": "https://iclass.tku.edu.tw",
                "Referer": "https://iclass.tku.edu.tw/",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)..."
            }

            upload_response = self.session.put(upload_url, files=files, headers=headers_upload)

        return upload_file_id
    
    async def deleteUpload(self, upload_ids: list):
        url = "https://iclass.tku.edu.tw/api/user/uploads"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://iclass.tku.edu.tw',
            'referer': 'https://iclass.tku.edu.tw/user/resources/files',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        }
        payload = {
            "upload_ids": upload_ids
        }
        try:
            response = self.session.delete(url, headers=headers, data=json.dumps(payload))
            if response.ok:
                return {"Deletion successful": response.status_code}
            else:
                return {"Deletion failed": response.status_code, "details": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error deleting uploads: {str(e)}"}

    async def read_activity(self, activity_id: int, course_id: int = None):
        """
        Mark a course activity / upload as read.
        POST https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}
        """
        url = f"https://iclass.tku.edu.tw/api/course/activities-read/{activity_id}"
        activity_details = await self.get_activitie(activity_id)  # Get activity details to determine if it's an upload or has a duration
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/learning-activity/full-screen"

        payloads = [{}]

        upload_id = activity_details.get("upload_id")
        if upload_id is not None:
            payloads[0]["upload_id"] = upload_id

        elif "data" in activity_details and "duration" in activity_details["data"]:
            duration = activity_details["data"]["duration"]
            duration_seconds = int(duration)
            payloads = [
                {"start": start, "end": min(start + 100, duration_seconds), "duration": duration}
                for start in range(0, duration_seconds, 100)
            ] or [{"start": 0, "end": duration_seconds, "duration": duration}]

        try:
            results = []
            for payload in payloads:
                response = self.session.post(url, headers=headers, json=payload)
                # print(f"Response for marking activity {activity_id} as read: {response.status_code}, {response.text}")  # Debugging line
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
                        error["failed_segment"] = {"start": payload["start"], "end": payload["end"]}
                    return error

            if len(results) == 1:
                return results[0]
            return {"success": True, "segments": results}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error marking activity as read: {str(e)}"}
    
    async def get_topic_categories(self, course_id: int):
        """
        Get discussion topic categories for a course.
        GET https://iclass.tku.edu.tw/api/courses/{course_id}/topic-categories
        """
        url = f"https://iclass.tku.edu.tw/api/courses/{course_id}/topic-categories"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://iclass.tku.edu.tw/course/{course_id}/forum",
        }
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching topic categories: {str(e)}"}

    async def get_topic(self, topic_id: int, course_id: int = None):
        """
        Get details of a specific topic.
        GET https://iclass.tku.edu.tw/api/topics/{topic_id}
        """
        url = f"https://iclass.tku.edu.tw/api/topics/{topic_id}"
        headers = {
            "Accept": "application/json, text/plain, */*",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/forum"

        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching topic: {str(e)}"}

    async def reply_topic(self, topic_id: int, content: str, uploads: list = None, course_id: int = None):
        """
        Reply to a topic.
        POST https://iclass.tku.edu.tw/api/topics/{topic_id}/replies
        """
        url = f"https://iclass.tku.edu.tw/api/topics/{topic_id}/replies"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/forum"

        payload = {
            "content": content,
            "uploads": uploads if uploads is not None else [],
        }
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
            return {"error": f"Error replying to topic: {str(e)}"}


    async def create_topic(self, category_id: int, title: str, content: str, uploads: list = None, course_id: int = None):
        """
        Create a new topic in a category.
        POST https://iclass.tku.edu.tw/api/topics
        """
        url = "https://iclass.tku.edu.tw/api/topics"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/forum"

        payload = {
            "title": title,
            "content": content,
            "uploads": uploads if uploads is not None else [],
            "category_id": category_id,
        }
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
            return {"error": f"Error creating topic: {str(e)}"}

    async def like_topic(self, topic_id: int, course_id: int = None):
        """
        Like a topic.
        POST https://iclass.tku.edu.tw/api/topics/{topic_id}/likes
        """
        url = f"https://iclass.tku.edu.tw/api/topics/{topic_id}/likes"
        headers = {
            "Accept": "application/json, text/plain, */*",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/forum"

        try:
            response = self.session.post(url, headers=headers)
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
            return {"error": f"Error liking topic: {str(e)}"}

    async def send_likes(self, course_id: int, topic_categories_id: int):
        try:
            topic_categories = await self.get_topic_categories(course_id)
        except Exception as e:
            return {"error": f"Error fetching topic categories: {str(e)}"}

        topics_c = topic_categories.get("topic_categories", [])
        topic_ids = []
        
        for category in topics_c:
            if category.get("id") == topic_categories_id:
                topics = category.get("topics", [])
                for topic in topics:
                    topic_id = topic.get("id")
                    if topic_id is not None:
                        topic_ids.append(topic_id)

        print(f"Found {len(topic_ids)} topics in course {course_id}. Sending likes...")

        for topic_id in topic_ids:
            print(f"Liking topic ID: {topic_id}")
            try:
                await self.like_topic(topic_id, course_id=course_id)
            except Exception as e:
                print(f"Error liking topic ID {topic_id}: {str(e)}")
                continue  # Continue with the next topic even if there's an error

        return {"success": f"Sent likes to {len(topic_ids)} topics in course {course_id}."}

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


