from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import require_teacher

router = APIRouter(prefix="/api/teacher", tags=["Teacher Portal"])

def calculate_grade(total_score: float) -> str:
    if total_score >= 90:
        return "A+"
    elif total_score >= 80:
        return "A"
    elif total_score >= 70:
        return "B+"
    elif total_score >= 60:
        return "B"
    elif total_score >= 50:
        return "C"
    elif total_score >= 40:
        return "D"
    else:
        return "F"

@router.get("/students", response_model=List[schemas.StudentProfileSummary])
def get_all_students(current_user: models.User = Depends(require_teacher), db: Session = Depends(get_db)):
    students = db.query(models.StudentProfile).all()
    results = []
    for sp in students:
        # compute overall attendance
        att_records = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == sp.id).all()
        overall_att = round(sum(r.percentage for r in att_records) / len(att_records), 1) if att_records else 0.0

        results.append(schemas.StudentProfileSummary(
            id=sp.id,
            user_id=sp.user.id,
            full_name=sp.user.full_name,
            email=sp.user.email,
            roll_number=sp.roll_number,
            department=sp.department,
            semester=sp.semester,
            academic_standing=sp.academic_standing,
            gpa=sp.gpa,
            overall_attendance=overall_att
        ))
    return results

@router.get("/students/{student_id}", response_model=schemas.StudentDetailResponse)
def get_student_detail(student_id: int, current_user: models.User = Depends(require_teacher), db: Session = Depends(get_db)):
    sp = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not sp:
        raise HTTPException(status_code=404, detail="Student not found")

    att_records = db.query(models.AttendanceRecord).filter(models.AttendanceRecord.student_id == sp.id).all()
    overall_att = round(sum(r.percentage for r in att_records) / len(att_records), 1) if att_records else 0.0

    profile_summary = schemas.StudentProfileSummary(
        id=sp.id,
        user_id=sp.user.id,
        full_name=sp.user.full_name,
        email=sp.user.email,
        roll_number=sp.roll_number,
        department=sp.department,
        semester=sp.semester,
        academic_standing=sp.academic_standing,
        gpa=sp.gpa,
        overall_attendance=overall_att
    )

    attendance_list = [
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
        for r in att_records
    ]

    marks_records = db.query(models.MarkRecord).filter(models.MarkRecord.student_id == sp.id).all()
    marks_list = [
        schemas.MarkRecordResponse(
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
        )
        for m in marks_records
    ]

    feedbacks = db.query(models.TeacherFeedback).filter(
        models.TeacherFeedback.student_id == sp.id
    ).order_by(models.TeacherFeedback.created_at.desc()).all()
    feedback_list = [schemas.FeedbackResponse.model_validate(f) for f in feedbacks]

    return schemas.StudentDetailResponse(
        profile=profile_summary,
        attendance=attendance_list,
        marks=marks_list,
        feedbacks=feedback_list
    )

@router.put("/students/{student_id}/attendance/{subject_id}", response_model=schemas.AttendanceRecordResponse)
def update_attendance(
    student_id: int,
    subject_id: int,
    payload: schemas.AttendanceUpdateRequest,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    if payload.total_classes <= 0:
        raise HTTPException(status_code=400, detail="Total classes must be greater than 0")
    if payload.attended_classes > payload.total_classes:
        raise HTTPException(status_code=400, detail="Attended classes cannot exceed total classes")

    record = db.query(models.AttendanceRecord).filter(
        models.AttendanceRecord.student_id == student_id,
        models.AttendanceRecord.subject_id == subject_id
    ).first()

    if not record:
        record = models.AttendanceRecord(
            student_id=student_id,
            subject_id=subject_id,
            total_classes=payload.total_classes,
            attended_classes=payload.attended_classes,
            percentage=round((payload.attended_classes / payload.total_classes) * 100, 1)
        )
        db.add(record)
    else:
        record.total_classes = payload.total_classes
        record.attended_classes = payload.attended_classes
        record.percentage = round((payload.attended_classes / payload.total_classes) * 100, 1)
        record.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(record)

    return schemas.AttendanceRecordResponse(
        id=record.id,
        student_id=record.student_id,
        subject_id=record.subject_id,
        subject_code=record.subject.code,
        subject_name=record.subject.name,
        instructor_name=record.subject.instructor_name,
        total_classes=record.total_classes,
        attended_classes=record.attended_classes,
        percentage=round(record.percentage, 1),
        last_updated=record.last_updated
    )

@router.put("/students/{student_id}/marks/{subject_id}", response_model=schemas.MarkRecordResponse)
def update_marks(
    student_id: int,
    subject_id: int,
    payload: schemas.MarkUpdateRequest,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    record = db.query(models.MarkRecord).filter(
        models.MarkRecord.student_id == student_id,
        models.MarkRecord.subject_id == subject_id
    ).first()

    total = round(payload.midterm_score + payload.assignment_score + payload.lab_score + payload.final_score, 1)
    grade = calculate_grade(total)

    if not record:
        record = models.MarkRecord(
            student_id=student_id,
            subject_id=subject_id,
            midterm_score=payload.midterm_score,
            assignment_score=payload.assignment_score,
            lab_score=payload.lab_score,
            final_score=payload.final_score,
            total_score=total,
            grade=grade
        )
        db.add(record)
    else:
        record.midterm_score = payload.midterm_score
        record.assignment_score = payload.assignment_score
        record.lab_score = payload.lab_score
        record.final_score = payload.final_score
        record.total_score = total
        record.grade = grade

    # Update student's overall GPA automatically
    db.commit()
    db.refresh(record)

    # Recalculate GPA for the student profile
    all_marks = db.query(models.MarkRecord).filter(models.MarkRecord.student_id == student_id).all()
    if all_marks:
        avg_total = sum(m.total_score for m in all_marks) / len(all_marks)
        calculated_gpa = round((avg_total / 10.0), 2)
        student_profile = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
        if student_profile:
            student_profile.gpa = calculated_gpa
            if calculated_gpa >= 9.0:
                student_profile.academic_standing = "Dean's Honor List"
            elif calculated_gpa >= 7.5:
                student_profile.academic_standing = "Good Standing"
            else:
                student_profile.academic_standing = "Needs Improvement"
            db.commit()

    return schemas.MarkRecordResponse(
        id=record.id,
        student_id=record.student_id,
        subject_id=record.subject_id,
        subject_code=record.subject.code,
        subject_name=record.subject.name,
        midterm_score=record.midterm_score,
        assignment_score=record.assignment_score,
        lab_score=record.lab_score,
        final_score=record.final_score,
        total_score=record.total_score,
        grade=record.grade
    )

@router.post("/students/{student_id}/feedback", response_model=schemas.FeedbackResponse)
def add_feedback(
    student_id: int,
    payload: schemas.FeedbackCreateRequest,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    student = db.query(models.StudentProfile).filter(models.StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    feedback = models.TeacherFeedback(
        student_id=student_id,
        teacher_name=current_user.full_name,
        subject=payload.subject,
        category=payload.category,
        feedback_text=payload.feedback_text,
        behavior_tag=payload.behavior_tag,
        created_at=datetime.utcnow()
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return schemas.FeedbackResponse.model_validate(feedback)

@router.delete("/feedbacks/{feedback_id}")
def delete_feedback(
    feedback_id: int,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    fb = db.query(models.TeacherFeedback).filter(models.TeacherFeedback.id == feedback_id).first()
    if not fb:
        raise HTTPException(status_code=404, detail="Feedback not found")
    db.delete(fb)
    db.commit()
    return {"message": "Feedback deleted successfully", "id": feedback_id}

