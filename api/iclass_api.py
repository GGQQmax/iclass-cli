try:
    from iclass_api_detail.iclass_api_topic import TronClassTopicAPI
    from iclass_api_detail.iclass_api_activitie import TronClassActivityAPI
    from iclass_api_detail.iclass_api_files import TronClassFilesAPI
    from iclass_api_detail.iclass_api_course import TronClassCourseAPI
    from iclass_api_detail.iclass_api_exam import TronClassExamAPI
except ImportError:
    from api.iclass_api_detail.iclass_api_topic import TronClassTopicAPI
    from api.iclass_api_detail.iclass_api_activitie import TronClassActivityAPI
    from api.iclass_api_detail.iclass_api_files import TronClassFilesAPI
    from api.iclass_api_detail.iclass_api_course import TronClassCourseAPI
    from api.iclass_api_detail.iclass_api_exam import TronClassExamAPI


class TronClassAPI:
    def __init__(self, session):
        self.session = session
        self.activity_api = TronClassActivityAPI(session)
        self.files_api = TronClassFilesAPI(session)
        self.topic_api = TronClassTopicAPI(session)
        self.course_api = TronClassCourseAPI(session)
        self.exam_api = TronClassExamAPI(session)

    async def get_todos(self):
        self.course_api = TronClassCourseAPI(self.session)
        return await self.course_api.get_todos()

    async def get_bulletins(self,org_mode:bool=False,start_date=None,end_date=None,page:int=1,size:int=10,course_ids:list=[]):
        self.course_api = TronClassCourseAPI(self.session)
        return await self.course_api.get_bulletins(org_mode,start_date,end_date,page,size,course_ids)
    
    async def download(self, reference_id):
        return await self.files_api.download(reference_id)

    async def myfiledownload(self, file_id):
        return await self.files_api.myfiledownload(file_id)

    async def get_courses(self):
        self.course_api = TronClassCourseAPI(self.session)
        return await self.course_api.get_courses()

    async def get_enrollments(self,course_id,data:dict=None):
        self.course_api = TronClassCourseAPI(self.session)
        return await self.course_api.get_enrollments(course_id,data)
    
    async def get_activities(self,course_id):
        self.activity_api = TronClassActivityAPI(self.session)
        return await self.activity_api.get_activities(course_id)

    async def get_activitie(self,activities_id):
        self.activity_api = TronClassActivityAPI(self.session)
        return await self.activity_api.get_activitie(activities_id)

    async def submit_homework(self, activity_id:int, upload_ids:list):
        self.activity_api = TronClassActivityAPI(self.session)
        return await self.activity_api.submit_homework(activity_id, upload_ids)

    async def get_my_files(self,numberOfRequest,page):
        self.files_api = TronClassFilesAPI(self.session)
        return await self.files_api.get_my_files(numberOfRequest,page)

    async def upload_file(self,file_path:str):
        self.files_api = TronClassFilesAPI(self.session)
        return await self.files_api.upload_file(file_path)
    
    async def deleteUpload(self, upload_ids: list):
        self.files_api = TronClassFilesAPI(self.session)
        return await self.files_api.deleteUpload(upload_ids)

    async def read_activity(self, activity_id: int, course_id: int = None):
        self.activity_api = TronClassActivityAPI(self.session)
        return await self.activity_api.read_activity(activity_id, course_id)
    
    async def get_topic_categories(self, course_id: int):
        self.topic_api = TronClassTopicAPI(self.session)
        return await self.topic_api.get_topic_categories(course_id)

    async def get_topic(self, topic_id: int, course_id: int = None):
        self.topic_api = TronClassTopicAPI(self.session)
        return await self.topic_api.get_topic(topic_id, course_id)

    async def reply_topic(self, topic_id: int, content: str, uploads: list = None, course_id: int = None):
        self.topic_api = TronClassTopicAPI(self.session)
        return await self.topic_api.reply_topic(topic_id, content, uploads, course_id)

    async def create_topic(self, category_id: int, title: str, content: str, uploads: list = None, course_id: int = None):
        self.topic_api = TronClassTopicAPI(self.session)
        return await self.topic_api.create_topic(category_id, title, content, uploads, course_id)

    async def like_topic(self, topic_id: int, course_id: int = None):
        self.topic_api = TronClassTopicAPI(self.session)
        return await self.topic_api.like_topic(topic_id, course_id)

    async def send_likes_all_topics(self, course_id: int, topic_categories_id: int):
        self.topic_api = TronClassTopicAPI(self.session)
        return await self.topic_api.send_likes_all_topics(course_id, topic_categories_id)

    async def read_all_activities(self, course_id: int):
        self.activity_api = TronClassActivityAPI(self.session)
        return await self.activity_api.read_all_activities(course_id)

    # ==========================================
    # Exam API interface methods
    # ==========================================

    async def get_course_exams(self, course_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_course_exams(course_id)

    async def get_exam(self, exam_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_exam(exam_id)

    async def get_exam_questions(self, exam_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_exam_questions(exam_id)

    async def get_exam_distribute(self, exam_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_exam_distribute(exam_id)

    async def get_exam_subjects_summary(self, exam_id: int, for_all_subjects: bool = False):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_exam_subjects_summary(exam_id, for_all_subjects)

    async def check_exam_qualification(self, exam_id: int, check_status: str = "start"):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.check_exam_qualification(exam_id, check_status)

    async def get_submission_storage(self, exam_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_submission_storage(exam_id)

    async def get_exam_submissions(self, exam_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_exam_submissions(exam_id)

    async def get_submission_detail(self, exam_id: int, submission_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_submission_detail(exam_id, submission_id)

    async def get_exam_left_time(self, submission_id: int):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.get_left_time(submission_id)

    async def read_exam_activity(self, exam_id: int, course_id: int = None):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.read_exam_activity(exam_id, course_id)

    async def save_exam_storage(self, exam_id: int, exam_paper_instance_id: int, subjects: list, exam_submission_id: int = None, progress: dict = None):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.save_exam_storage(exam_id, exam_paper_instance_id, subjects, exam_submission_id, progress)

    async def update_exam_answers(self, submission_id: int, exam_paper_instance_id: int, subjects_answers: list, progress: dict = None, play_record: dict = None):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.update_exam_answers(submission_id, exam_paper_instance_id, subjects_answers, progress, play_record)

    async def submit_exam(self, exam_id: int, exam_paper_instance_id: int, exam_submission_id: int, subjects: list, progress: dict = None, reason: str = "user"):
        self.exam_api = TronClassExamAPI(self.session)
        return await self.exam_api.submit_exam(exam_id, exam_paper_instance_id, exam_submission_id, subjects, progress, reason)