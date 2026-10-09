from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import require_student

router = APIRouter(prefix="/api/student", tags=["Student Portal"])

def _get_student_profile(user: models.User, db: Session) -> models.StudentProfile:
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile

@router.get("/dashboard", response_model=schemas.StudentDashboardResponse)
def get_dashboard(current_user: models.User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_student_profile(current_user, db)

    # Attendance
    attendance_records = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.student_id == profile.id
    ).all()
    attendance_list = []
    total_pct = 0.0
    for att in attendance_records:
        attendance_list.append(schemas.AttendanceRecordResponse(
            id=att.id,
            student_id=att.student_id,
            subject_id=att.subject_id,
            subject_code=att.subject.code,
            subject_name=att.subject.name,
            instructor_name=att.subject.instructor_name,
            total_classes=att.total_classes,
            attended_classes=att.attended_classes,
            percentage=round(att.percentage, 1),
            last_updated=att.last_updated
        ))
        total_pct += att.percentage

    overall_attendance = round(total_pct / len(attendance_records), 1) if attendance_records else 0.0

    # Marks
    marks_records = db.query(models.MarkRecord).filter(
        models.MarkRecord.student_id == profile.id
    ).all()
    marks_list = []
    for m in marks_records:
        marks_list.append(schemas.MarkRecordResponse(
            id=m.id,
            student_id=m.student_id,
            subject_id=m.subject_id,
            subject_code=m.subject.code,
            subject_name=m.subject.name,
            midterm_score=m.midterm_score,
            assignment_score=m.assignment_score,
            lab_score=m.lab_score,
            final_score=m.final_score,
            total_score=m.total_score,
            grade=m.grade
        ))

    # Feedbacks
    feedbacks = db.query(models.TeacherFeedback).filter(
        models.TeacherFeedback.student_id == profile.id
    ).order_by(models.TeacherFeedback.created_at.desc()).all()
    feedback_list = [schemas.FeedbackResponse.model_validate(f) for f in feedbacks]

    # Notes count
    notes_count = db.query(models.SubjectNote).count()

    profile_summary = schemas.StudentProfileSummary(
        id=profile.id,
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        roll_number=profile.roll_number,
        department=profile.department,
        semester=profile.semester,
        academic_standing=profile.academic_standing,
        gpa=profile.gpa,
        overall_attendance=overall_attendance
    )

    return schemas.StudentDashboardResponse(
        profile=profile_summary,
        attendance=attendance_list,
        overall_attendance=overall_attendance,
        marks=marks_list,
        feedbacks=feedback_list,
        recent_notes_count=notes_count
    )

@router.get("/attendance", response_model=List[schemas.AttendanceRecordResponse])
def get_attendance(current_user: models.User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_student_profile(current_user, db)
    records = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == profile.id).all()
    return [
        schemas.AttendanceRecordResponse(
            id=r.id,
            student_id=r.student_id,
            subject_id=r.subject_id,
            subject_code=r.subject.code,
            subject_name=r.subject.name,
            instructor_name=r.subject.instructor_name,
            total_classes=r.total_classes,
            attended_classes=r.attended_classes,
            percentage=round(r.percentage, 1),
            last_updated=r.last_updated
        )
        for r in records
    ]

@router.get("/marks", response_model=List[schemas.MarkRecordResponse])
def get_marks(current_user: models.User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_student_profile(current_user, db)
    records = db.query(models.MarkRecord).filter(models.MarkRecord.student_id == profile.id).all()
    return [
        schemas.MarkRecordResponse(
            id=r.id,
            student_id=r.student_id,
            subject_id=r.subject_id,
            subject_code=r.subject.code,
            subject_name=r.subject.name,
            midterm_score=r.midterm_score,
            assignment_score=r.assignment_score,
            lab_score=r.lab_score,
            final_score=r.final_score,
            total_score=r.total_score,
            grade=r.grade
        )
        for r in records
    ]

@router.get("/feedback", response_model=List[schemas.FeedbackResponse])
def get_feedbacks(current_user: models.User = Depends(require_student), db: Session = Depends(get_db)):
    profile = _get_student_profile(current_user, db)
    records = db.query(models.TeacherFeedback).filter(models.TeacherFeedback.student_id == profile.id).order_by(models.TeacherFeedback.created_at.desc()).all()
    return [schemas.FeedbackResponse.model_validate(r) for r in records]

