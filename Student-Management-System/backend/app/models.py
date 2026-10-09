from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # "student" or "teacher"
    avatar_url = Column(String(255), nullable=True)

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    department = Column(String(100), default="Artificial Intelligence & Machine Learning")
    semester = Column(Integer, default=6)
    academic_standing = Column(String(50), default="Good Standing")
    gpa = Column(Float, default=8.5)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")
    marks_records = relationship("MarkRecord", back_populates="student", cascade="all, delete-orphan")
    feedbacks = relationship("TeacherFeedback", back_populates="student", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    credits = Column(Integer, default=4)
    instructor_name = Column(String(100), nullable=False)

    attendance_records = relationship("AttendanceRecord", back_populates="subject")
    marks_records = relationship("MarkRecord", back_populates="subject")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    total_classes = Column(Integer, default=40)
    attended_classes = Column(Integer, default=34)
    percentage = Column(Float, default=85.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="attendance_records")
    subject = relationship("Subject", back_populates="attendance_records")


class MarkRecord(Base):
    __tablename__ = "marks_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    midterm_score = Column(Float, default=25.0)       # out of 30
    assignment_score = Column(Float, default=18.0)    # out of 20
    lab_score = Column(Float, default=19.0)           # out of 20
    final_score = Column(Float, default=26.0)         # out of 30
    total_score = Column(Float, default=88.0)         # out of 100
    grade = Column(String(5), default="A")

    student = relationship("StudentProfile", back_populates="marks_records")
    subject = relationship("Subject", back_populates="marks_records")


class TeacherFeedback(Base):
    __tablename__ = "teacher_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    teacher_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    category = Column(String(50), default="Academic Suggestion")  # "Academic Suggestion", "Behavior & Conduct", "Lab Performance"
    feedback_text = Column(Text, nullable=False)
    behavior_tag = Column(String(50), default="Proactive in Labs")  # e.g., "Excellent Participation", "Needs Consistency", "Strong Analytical Skills"
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("StudentProfile", back_populates="feedbacks")


class SubjectNote(Base):
    __tablename__ = "subject_notes"

    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), nullable=False, index=True)  # "MLOps" or "Deep Learning"
    title = Column(String(200), nullable=False)
    unit = Column(String(100), default="Unit 1")
    summary = Column(Text, nullable=False)
    content_markdown = Column(Text, nullable=False)
    resource_url = Column(String(255), nullable=True)
    tags = Column(String(200), default="")
    author_name = Column(String(100), default="Faculty")
    created_at = Column(DateTime, default=datetime.utcnow)

