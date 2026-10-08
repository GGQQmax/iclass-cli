#!/usr/bin/env python3
"""
iClass / TronClass MCP Server
Provides Model Context Protocol tools for interacting with TKU iClass (TronClass).
"""

import os
import sys
from typing import Any, Dict, List, Optional

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer
    except ImportError:
        sys.stderr.write("Error: 'mcp' package is required. Install it via 'pip install mcp'.\n")
        sys.exit(1)

from api.auth_module import Authenticator
from api.iclass_api import TronClassAPI

mcp = MCPServer(
    name="iclass-mcp",
    description="MCP Server for Tamkang University iClass (TronClass) learning platform.",
)

_api_instance: Optional[TronClassAPI] = None


def get_api() -> TronClassAPI:
    """
    Lazy initialization of TronClassAPI session.
    """
    global _api_instance
    if _api_instance is None:
        auth = Authenticator()
        session = auth.perform_auth()
        _api_instance = TronClassAPI(session)
    return _api_instance


@mcp.tool(description="Get the list of pending todos (homework, quizzes, exams) for the logged-in user.")
async def get_todos() -> Any:
    """Fetch pending todos."""
    try:
        api = get_api()
        return await api.get_todos()
    except Exception as e:
        return {"error": f"Failed to get todos: {str(e)}"}


@mcp.tool(description="Get the list of ongoing enrolled courses for the logged-in user.")
async def get_courses() -> Any:
    """Fetch ongoing courses."""
    try:
        api = get_api()
        return await api.get_courses()
    except Exception as e:
        return {"error": f"Failed to get courses: {str(e)}"}


@mcp.tool(description="Get bulletins / announcements for courses or organization.")
async def get_bulletins(
    org_mode: bool = False,
    page: int = 1,
    size: int = 10,
    course_ids: Optional[List[int]] = None,
) -> Any:
    """
    Fetch course or organization bulletins.

    :param org_mode: Whether to fetch organization-level bulletins instead of course bulletins.
    :param page: Page number (default: 1).
    :param size: Number of items per page (default: 10).
    :param course_ids: Optional list of course IDs to filter by.
    """
    try:
        api = get_api()
        return await api.get_bulletins(
            org_mode=org_mode,
            page=page,
            size=size,
            course_ids=course_ids or [],
        )
    except Exception as e:
        return {"error": f"Failed to get bulletins: {str(e)}"}


@mcp.tool(description="Get activities and syllabus structure for a given course ID.")
async def get_course_activities(course_id: int) -> Any:
    """
    Fetch learning activities for a course.

    :param course_id: Course ID.
    """
    try:
        api = get_api()
        return await api.get_activities(course_id)
    except Exception as e:
        return {"error": f"Failed to get course activities: {str(e)}"}


@mcp.tool(description="Get details for a specific activity ID.")
async def get_activity_detail(activity_id: int) -> Any:
    """
    Fetch details for an activity.

    :param activity_id: Activity ID.
    """
    try:
        api = get_api()
        return await api.get_activitie(activity_id)
    except Exception as e:
        return {"error": f"Failed to get activity detail: {str(e)}"}


@mcp.tool(description="Mark a course learning activity / upload as read.")
async def read_activity(
    activity_id: int,
    upload_id: Optional[int] = None,
    course_id: Optional[int] = None,
) -> Any:
    """
    Mark an activity as read.

    :param activity_id: Activity ID to mark as read.
    :param upload_id: Optional specific upload ID in the activity.
    :param course_id: Optional course ID for referrer header.
    """
    try:
        api = get_api()
        return await api.read_activity(
            activity_id=activity_id,
            upload_id=upload_id,
            course_id=course_id,
        )
    except Exception as e:
        return {"error": f"Failed to mark activity as read: {str(e)}"}


@mcp.tool(description="Get enrolled students and members for a course.")
async def get_enrollments(course_id: int) -> Any:
    """
    Fetch course enrollments.

    :param course_id: Course ID.
    """
    try:
        api = get_api()
        return await api.get_enrollments(course_id)
    except Exception as e:
        return {"error": f"Failed to get enrollments: {str(e)}"}


@mcp.tool(description="Get discussion forum categories for a specific course.")
async def get_topic_categories(course_id: int) -> Any:
    """
    Fetch topic categories for a course forum.

    :param course_id: Course ID.
    """
    try:
        api = get_api()
        return await api.get_topic_categories(course_id)
    except Exception as e:
        return {"error": f"Failed to get topic categories: {str(e)}"}


@mcp.tool(description="Get details and replies for a specific discussion topic.")
async def get_topic(topic_id: int, course_id: Optional[int] = None) -> Any:
    """
    Fetch topic thread.

    :param topic_id: Topic ID.
    :param course_id: Optional course ID.
    """
    try:
        api = get_api()
        return await api.get_topic(topic_id, course_id=course_id)
    except Exception as e:
        return {"error": f"Failed to get topic: {str(e)}"}


@mcp.tool(description="Reply to a discussion topic.")
async def reply_topic(
    topic_id: int,
    content: str,
    uploads: Optional[List[int]] = None,
    course_id: Optional[int] = None,
) -> Any:
    """
    Reply to a topic.

    :param topic_id: Topic ID to reply to.
    :param content: Reply content (can include HTML tags).
    :param uploads: Optional list of upload IDs attached to the reply.
    :param course_id: Optional course ID.
    """
    try:
        api = get_api()
        return await api.reply_topic(
            topic_id=topic_id,
            content=content,
            uploads=uploads or [],
            course_id=course_id,
        )
    except Exception as e:
        return {"error": f"Failed to reply to topic: {str(e)}"}


@mcp.tool(description="Create a new discussion topic in a category.")
async def create_topic(
    category_id: int,
    title: str,
    content: str,
    uploads: Optional[List[int]] = None,
    course_id: Optional[int] = None,
) -> Any:
    """
    Create a new topic.

    :param category_id: Category ID under which to create the topic.
    :param title: Topic title.
    :param content: Topic content (can include HTML tags).
    :param uploads: Optional list of upload IDs.
    :param course_id: Optional course ID.
    """
    try:
        api = get_api()
        return await api.create_topic(
            category_id=category_id,
            title=title,
            content=content,
            uploads=uploads or [],
            course_id=course_id,
        )
    except Exception as e:
        return {"error": f"Failed to create topic: {str(e)}"}


@mcp.tool(description="Like a discussion topic.")
async def like_topic(topic_id: int, course_id: Optional[int] = None) -> Any:
    """
    Like a topic.

    :param topic_id: Topic ID to like.
    :param course_id: Optional course ID.
    """
    try:
        api = get_api()
        return await api.like_topic(topic_id, course_id=course_id)
    except Exception as e:
        return {"error": f"Failed to like topic: {str(e)}"}


@mcp.tool(description="Submit homework for a given activity ID.")
async def submit_homework(activity_id: int, upload_ids: List[int]) -> Any:
    """
    Submit homework.

    :param activity_id: Activity ID.
    :param upload_ids: List of uploaded file IDs to submit.
    """
    try:
        api = get_api()
        return await api.submit_homework(activity_id=activity_id, upload_ids=upload_ids)
    except Exception as e:
        return {"error": f"Failed to submit homework: {str(e)}"}


@mcp.tool(description="List files in personal iClass cloud drive / resources.")
async def get_my_files(page: int = 1, size: int = 20) -> Any:
    """
    Fetch user's uploaded files.

    :param page: Page number (default: 1).
    :param size: Number of items per page (default: 20).
    """
    try:
        api = get_api()
        return await api.get_my_files(numberOfRequest=size, page=page)
    except Exception as e:
        return {"error": f"Failed to get files: {str(e)}"}


@mcp.tool(description="Upload a local file to iClass personal resources and return its upload ID.")
async def upload_file(file_path: str) -> Any:
    """
    Upload a local file.

    :param file_path: Absolute or relative path to the local file.
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        api = get_api()
        upload_id = await api.upload_file(file_path)
        return {"upload_id": upload_id}
    except Exception as e:
        return {"error": f"Failed to upload file: {str(e)}"}


@mcp.tool(description="Download an iClass file by reference ID to ~/Downloads.")
async def download_file_by_reference(reference_id: int) -> Any:
    """
    Download a file by reference ID.

    :param reference_id: File reference ID.
    """
    try:
        api = get_api()
        file_path = await api.download(reference_id)
        return {"downloaded_to": file_path}
    except Exception as e:
        return {"error": f"Failed to download file: {str(e)}"}


@mcp.tool(description="Get exams list for a course.")
async def get_course_exams(course_id: int) -> Any:
    """Fetch exams for a course."""
    try:
        api = get_api()
        return await api.get_course_exams(course_id)
    except Exception as e:
        return {"error": f"Failed to get course exams: {str(e)}"}


@mcp.tool(description="Get metadata and details of an exam by exam ID.")
async def get_exam_detail(exam_id: int) -> Any:
    """Fetch exam details."""
    try:
        api = get_api()
        return await api.get_exam(exam_id)
    except Exception as e:
        return {"error": f"Failed to get exam detail: {str(e)}"}


@mcp.tool(description="Get questions and paper instance for an exam.")
async def get_exam_questions(exam_id: int) -> Any:
    """Fetch exam paper questions."""
    try:
        api = get_api()
        return await api.get_exam_questions(exam_id)
    except Exception as e:
        return {"error": f"Failed to get exam questions: {str(e)}"}


@mcp.tool(description="Get submissions and scores for an exam.")
async def get_exam_submissions(exam_id: int) -> Any:
    """Fetch submissions for an exam."""
    try:
        api = get_api()
        return await api.get_exam_submissions(exam_id)
    except Exception as e:
        return {"error": f"Failed to get exam submissions: {str(e)}"}


@mcp.tool(description="Get submission detail and correct answers review.")
async def get_exam_submission_detail(exam_id: int, submission_id: int) -> Any:
    """Fetch submission review."""
    try:
        api = get_api()
        return await api.get_submission_detail(exam_id, submission_id)
    except Exception as e:
        return {"error": f"Failed to get submission detail: {str(e)}"}


@mcp.tool(description="Save draft exam storage progress.")
async def save_exam_storage(
    exam_id: int,
    exam_paper_instance_id: int,
    subjects: List[Dict[str, Any]],
    exam_submission_id: Optional[int] = None,
) -> Any:
    """Save in-progress exam answers to storage."""
    try:
        api = get_api()
        return await api.save_exam_storage(exam_id, exam_paper_instance_id, subjects, exam_submission_id)
    except Exception as e:
        return {"error": f"Failed to save exam storage: {str(e)}"}


@mcp.tool(description="Submit final exam answers.")
async def submit_exam(
    exam_id: int,
    exam_paper_instance_id: int,
    exam_submission_id: int,
    subjects: List[Dict[str, Any]],
) -> Any:
    """Submit final exam paper."""
    try:
        api = get_api()
        return await api.submit_exam(exam_id, exam_paper_instance_id, exam_submission_id, subjects)
    except Exception as e:
        return {"error": f"Failed to submit exam: {str(e)}"}


def main():
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()