import requests
import json
from typing import Any, Dict, List, Optional, Union


class TronClassExamAPI:
    """
    API client for TronClass / TKU iClass Exams.
    Provides methods to read exam information & questions, modify/save answers in progress,
    and submit completed exams.
    """

    def __init__(self, session: requests.Session):
        self.session = session

    # ==========================================
    # Helper formatting methods
    # ==========================================

    @staticmethod
    def format_subject(
        subject_id: int,
        answer_option_ids: Optional[List[int]] = None,
        answer_text: str = "",
        answers: Optional[List[Dict[str, Any]]] = None,
        subject_updated_at: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Format a subject payload item for `save_exam_storage` or `submit_exam`.

        :param subject_id: ID of the question/subject
        :param answer_option_ids: List of selected option IDs (for choice questions)
        :param answer_text: Text answer (for short answer / essay)
        :param answers: List of blank answers [{"sort": 0, "content": "..."}] (for fill-in-blank / cloze)
        :param subject_updated_at: ISO timestamp of subject's last update
        :param parent_id: Container subject ID if this is a sub-subject (e.g. matching)
        """
        payload: Dict[str, Any] = {
            "subject_id": subject_id,
            "answer_option_ids": list(answer_option_ids) if answer_option_ids is not None else [],
        }
        if subject_updated_at:
            payload["subject_updated_at"] = subject_updated_at
        if answer_text:
            payload["answer"] = answer_text
        if answers:
            payload["answers"] = answers
        if parent_id:
            payload["parent_id"] = parent_id
        return payload

    @staticmethod
    def format_subject_answer(
        index: int,
        subject_id: int,
        answer_option_ids: Optional[List[int]] = None,
        answer_text: str = "",
        answers: Optional[List[Dict[str, Any]]] = None,
        subject_updated_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Format a subject answer item for `update_exam_answers` (multiple-subjects PUT).
        """
        answer_data: Dict[str, Any] = {
            "subject_id": subject_id,
            "answer_option_ids": list(answer_option_ids) if answer_option_ids is not None else [],
        }
        if subject_updated_at:
            answer_data["subject_updated_at"] = subject_updated_at
        if answer_text:
            answer_data["answer"] = answer_text
        if answers:
            answer_data["answers"] = answers

        return {
            "index": index,
            "subject_id": subject_id,
            "answer": answer_data,
        }

    # ==========================================
    # Read APIs
    # ==========================================

    async def get_course_exams(self, course_id: int) -> Union[Dict[str, Any], List[Any]]:
        """
        Get all exams under a given course.
        GET https://iclass.tku.edu.tw/api/courses/{course_id}/exams
        """
        url = f"https://iclass.tku.edu.tw/api/courses/{course_id}/exams"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching course exams: {str(e)}"}

    async def get_exam(self, exam_id: int) -> Dict[str, Any]:
        """
        Get metadata and configuration for a specific exam.
        GET https://iclass.tku.edu.tw/api/exams/{exam_id}
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching exam: {str(e)}"}

    async def get_exam_questions(self, exam_id: int) -> Dict[str, Any]:
        """
        Get the exam paper distribution containing exam_paper_instance_id and subjects questions.
        GET https://iclass.tku.edu.tw/api/exams/{exam_id}/distribute
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}/distribute"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching exam questions: {str(e)}"}

    async def get_exam_distribute(self, exam_id: int) -> Dict[str, Any]:
        """Alias for get_exam_questions."""
        return await self.get_exam_questions(exam_id)

    async def get_exam_subjects_summary(self, exam_id: int, for_all_subjects: bool = False) -> Dict[str, Any]:
        """
        Get summary of subjects and points.
        GET https://iclass.tku.edu.tw/api/exams/{exam_id}/subjects-summary?forAllSubjects={for_all_subjects}
        """
        flag = "true" if for_all_subjects else "false"
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}/subjects-summary?forAllSubjects={flag}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching subjects summary: {str(e)}"}

    async def check_exam_qualification(self, exam_id: int, check_status: str = "start") -> Dict[str, Any]:
        """
        Check whether the current user is qualified to take the exam.
        GET https://iclass.tku.edu.tw/api/exam/{exam_id}/check-exam-qualification?no-intercept=true&check_status={check_status}
        """
        url = f"https://iclass.tku.edu.tw/api/exam/{exam_id}/check-exam-qualification?no-intercept=true&check_status={check_status}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error checking exam qualification: {str(e)}"}

    async def get_submission_storage(self, exam_id: int) -> Dict[str, Any]:
        """
        Get saved draft/in-progress submission state from storage.
        GET https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions/storage
        Returns 404 (or message) when no draft exists.
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions/storage"
        try:
            response = self.session.get(url)
            if response.status_code == 404:
                return {"has_draft": False, "message": "No draft found"}
            response.raise_for_status()
            res = response.json()
            if isinstance(res, dict):
                res["has_draft"] = True
            return res
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching submission storage: {str(e)}"}

    async def get_exam_submissions(self, exam_id: int) -> Dict[str, Any]:
        """
        Get the list of prior submissions and scores for this exam.
        GET https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching exam submissions: {str(e)}"}

    async def get_submission_detail(self, exam_id: int, submission_id: int) -> Dict[str, Any]:
        """
        Get detailed submission review, scores, and correct answers.
        GET https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions/{submission_id}
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions/{submission_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching submission detail: {str(e)}"}

    async def get_left_time(self, submission_id: int) -> Dict[str, Any]:
        """
        Get remaining time (seconds) for an active exam submission.
        GET https://iclass.tku.edu.tw/api/exams/{submission_id}/left_time
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{submission_id}/left_time"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching left time: {str(e)}"}

    async def read_exam_activity(self, exam_id: int, course_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Mark exam activity as read.
        POST https://iclass.tku.edu.tw/api/course/activities-read/exam/{exam_id}
        """
        url = f"https://iclass.tku.edu.tw/api/course/activities-read/exam/{exam_id}"
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/json;charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        if course_id:
            headers["Referer"] = f"https://iclass.tku.edu.tw/course/{course_id}/learning-activity"
        try:
            response = self.session.post(url, headers=headers, json={})
            if response.status_code in (200, 201):
                try:
                    return response.json() or {"success": True, "status_code": response.status_code}
                except ValueError:
                    return {"success": True, "status_code": response.status_code}
            return {"error": f"Failed with status {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error marking exam activity as read: {str(e)}"}

    # ==========================================
    # Modify / Progress Save APIs
    # ==========================================

    async def save_exam_storage(
        self,
        exam_id: int,
        exam_paper_instance_id: int,
        subjects: List[Dict[str, Any]],
        exam_submission_id: Optional[int] = None,
        progress: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Initialize or save exam draft state in storage.
        POST https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions/storage

        Payload format:
        {
            "exam_paper_instance_id": 8182426,
            "exam_submission_id": null | 11426019,
            "subjects": [
                {"subject_id": 5560556, "subject_updated_at": "...", "answer_option_ids": [17406418]}
            ],
            "progress": {"answered_num": 1, "total_subjects": 10}
        }
        Returns:
            {"id": submission_id, "left_time": 899.82}
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions/storage"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://iclass.tku.edu.tw",
            "Referer": f"https://iclass.tku.edu.tw/exam/{exam_id}/subjects",
        }

        if progress is None:
            answered_num = sum(
                1 for s in subjects
                if s.get("answer_option_ids") or s.get("answer") or s.get("answers")
            )
            progress = {
                "answered_num": answered_num,
                "total_subjects": len(subjects),
            }

        payload = {
            "exam_paper_instance_id": exam_paper_instance_id,
            "exam_submission_id": exam_submission_id,
            "subjects": subjects,
            "progress": progress,
        }

        try:
            response = self.session.post(url, headers=headers, json=payload)
            if response.status_code in (200, 201):
                return response.json()
            return {"error": f"Failed with status {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error saving exam storage: {str(e)}"}

    async def update_exam_answers(
        self,
        submission_id: int,
        exam_paper_instance_id: int,
        subjects_answers: List[Dict[str, Any]],
        progress: Optional[Dict[str, int]] = None,
        play_record: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update answers for one or more questions during the exam.
        PUT https://iclass.tku.edu.tw/api/exams/submissions/{submission_id}/multiple-subjects

        Payload format:
        {
            "exam_paper_instance_id": 8182426,
            "subjects_answers": [
                {
                    "index": 0,
                    "subject_id": 5560556,
                    "answer": {
                        "subject_id": 5560556,
                        "subject_updated_at": "...",
                        "answer_option_ids": [17406418]
                    }
                }
            ],
            "play_record": {},
            "progress": {"answered_num": 1, "total_subjects": 10}
        }
        Returns:
            {"id": submission_id, "left_time": 889.45, "updated_ids": [5560556]}
        """
        url = f"https://iclass.tku.edu.tw/api/exams/submissions/{submission_id}/multiple-subjects"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://iclass.tku.edu.tw",
        }

        if progress is None:
            progress = {
                "answered_num": len(subjects_answers),
                "total_subjects": len(subjects_answers),
            }

        payload = {
            "exam_paper_instance_id": exam_paper_instance_id,
            "subjects_answers": subjects_answers,
            "play_record": play_record if play_record is not None else {},
            "progress": progress,
        }

        try:
            response = self.session.put(url, headers=headers, json=payload)
            if response.status_code in (200, 201):
                return response.json()
            return {"error": f"Failed with status {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error updating exam answers: {str(e)}"}

    # ==========================================
    # Submit API
    # ==========================================

    async def submit_exam(
        self,
        exam_id: int,
        exam_paper_instance_id: int,
        exam_submission_id: int,
        subjects: List[Dict[str, Any]],
        progress: Optional[Dict[str, int]] = None,
        reason: str = "user",
    ) -> Dict[str, Any]:
        """
        Submit the final exam paper.
        POST https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions

        Payload format:
        {
            "exam_paper_instance_id": 8182426,
            "exam_submission_id": 11426019,
            "subjects": [
                {
                    "subject_id": 5560556,
                    "subject_updated_at": "...",
                    "answer_option_ids": [17406418]
                }
            ],
            "progress": {"answered_num": 10, "total_subjects": 10},
            "reason": "user"
        }
        Returns:
            {"allow_retake_exam": true, "check_submit_ip_passed": true, "submission_id": 11426019}
        """
        url = f"https://iclass.tku.edu.tw/api/exams/{exam_id}/submissions"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://iclass.tku.edu.tw",
            "Referer": f"https://iclass.tku.edu.tw/exam/{exam_id}/subjects",
        }

        if progress is None:
            answered_num = sum(
                1 for s in subjects
                if s.get("answer_option_ids") or s.get("answer") or s.get("answers")
            )
            progress = {
                "answered_num": answered_num,
                "total_subjects": len(subjects),
            }

        payload = {
            "exam_paper_instance_id": exam_paper_instance_id,
            "exam_submission_id": exam_submission_id,
            "subjects": subjects,
            "progress": progress,
            "reason": reason,
        }

        try:
            response = self.session.post(url, headers=headers, json=payload)
            if response.status_code in (200, 201):
                return response.json()
            return {"error": f"Failed with status {response.status_code}", "details": response.text}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error submitting exam: {str(e)}"}
    