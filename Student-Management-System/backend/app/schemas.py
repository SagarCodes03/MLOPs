from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    username: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

# Subject Schemas
class SubjectResponse(BaseModel):
    id: int
    code: str
    name: str
    credits: int
    instructor_name: str

    class Config:
        from_attributes = True

# Attendance Schemas
class AttendanceRecordResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    subject_code: str
    subject_name: str
    instructor_name: str
    total_classes: int
    attended_classes: int
    percentage: float
    last_updated: datetime

    class Config:
        from_attributes = True

class AttendanceUpdateRequest(BaseModel):
    total_classes: int
    attended_classes: int

# Marks Schemas
class MarkRecordResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    subject_code: str
    subject_name: str
    midterm_score: float
    assignment_score: float
    lab_score: float
    final_score: float
    total_score: float
    grade: str

    class Config:
        from_attributes = True

class MarkUpdateRequest(BaseModel):
    midterm_score: float
    assignment_score: float
    lab_score: float
    final_score: float

# Feedback & Behavior Schemas
class FeedbackCreateRequest(BaseModel):
    subject: str
    category: str = "Academic Suggestion"  # Academic Suggestion, Behavior & Conduct, Lab Performance
    feedback_text: str
    behavior_tag: str = "Good Participation"

class FeedbackResponse(BaseModel):
    id: int
    student_id: int
    teacher_name: str
    subject: str
    category: str
    feedback_text: str
    behavior_tag: str
    created_at: datetime

    class Config:
        from_attributes = True

# Student Profile & Roster
class StudentProfileSummary(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    roll_number: str
    department: str
    semester: int
    academic_standing: str
    gpa: float
    overall_attendance: float

class StudentDetailResponse(BaseModel):
    profile: StudentProfileSummary
    attendance: List[AttendanceRecordResponse]
    marks: List[MarkRecordResponse]
    feedbacks: List[FeedbackResponse]

class StudentDashboardResponse(BaseModel):
    profile: StudentProfileSummary
    attendance: List[AttendanceRecordResponse]
    overall_attendance: float
    marks: List[MarkRecordResponse]
    feedbacks: List[FeedbackResponse]
    recent_notes_count: int

# Subject Notes Schemas
class SubjectNoteCreate(BaseModel):
    subject_name: str  # "MLOps" or "Deep Learning"
    title: str
    unit: str
    summary: str
    content_markdown: str
    resource_url: Optional[str] = None
    tags: Optional[str] = ""

class SubjectNoteUpdate(BaseModel):
    subject_name: Optional[str] = None
    title: Optional[str] = None
    unit: Optional[str] = None
    summary: Optional[str] = None
    content_markdown: Optional[str] = None
    resource_url: Optional[str] = None
    tags: Optional[str] = None

class SubjectNoteResponse(BaseModel):
    id: int
    subject_name: str
    title: str
    unit: str
    summary: str
    content_markdown: str
    resource_url: Optional[str] = None
    tags: str
    author_name: str
    created_at: datetime

    class Config:
        from_attributes = True

