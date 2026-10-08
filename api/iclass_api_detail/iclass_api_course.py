import requests
from datetime import date
from dateutil.relativedelta import relativedelta
import urllib.parse
import json

class TronClassCourseAPI:
    def __init__(self, session):
        self.session = session

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

    async def get_todos(self):
        todos_url = "https://iclass.tku.edu.tw/api/todos"
        try:
            response = self.session.get(todos_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching todos: {str(e)}"}