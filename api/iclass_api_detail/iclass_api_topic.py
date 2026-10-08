import requests
class TronClassTopicAPI:
    def __init__(self, session):
        self.session = session
    
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

    async def send_likes_all_topics(self, course_id: int, topic_categories_id: int):
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
