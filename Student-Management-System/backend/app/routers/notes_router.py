from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.app.database import get_db
from backend.app import models, schemas
from backend.app.auth import get_current_user, require_teacher

router = APIRouter(prefix="/api/notes", tags=["Subject Notes"])

@router.get("", response_model=List[schemas.SubjectNoteResponse])
def get_notes(
    subject: Optional[str] = Query(None, description="Filter by subject, e.g. MLOps, Deep Learning"),
    search: Optional[str] = Query(None, description="Search keyword in title, summary, or tags"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.SubjectNote)
    if subject and subject.strip():
        query = query.filter(models.SubjectNote.subject_name.ilike(f"%{subject.strip()}%"))
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (models.SubjectNote.title.ilike(term)) |
            (models.SubjectNote.summary.ilike(term)) |
            (models.SubjectNote.tags.ilike(term)) |
            (models.SubjectNote.content_markdown.ilike(term))
        )
    return query.order_by(models.SubjectNote.created_at.desc()).all()

@router.get("/{note_id}", response_model=schemas.SubjectNoteResponse)
def get_note_by_id(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(models.SubjectNote).filter(models.SubjectNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Subject note not found")
    return note

@router.post("", response_model=schemas.SubjectNoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: schemas.SubjectNoteCreate,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    note = models.SubjectNote(
        subject_name=payload.subject_name,
        title=payload.title,
        unit=payload.unit,
        summary=payload.summary,
        content_markdown=payload.content_markdown,
        resource_url=payload.resource_url,
        tags=payload.tags or "",
        author_name=current_user.full_name,
        created_at=datetime.utcnow()
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.put("/{note_id}", response_model=schemas.SubjectNoteResponse)
def update_note(
    note_id: int,
    payload: schemas.SubjectNoteUpdate,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    note = db.query(models.SubjectNote).filter(models.SubjectNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Subject note not found")

    if payload.subject_name is not None:
        note.subject_name = payload.subject_name
    if payload.title is not None:
        note.title = payload.title
    if payload.unit is not None:
        note.unit = payload.unit
    if payload.summary is not None:
        note.summary = payload.summary
    if payload.content_markdown is not None:
        note.content_markdown = payload.content_markdown
    if payload.resource_url is not None:
        note.resource_url = payload.resource_url
    if payload.tags is not None:
        note.tags = payload.tags

    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    current_user: models.User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    note = db.query(models.SubjectNote).filter(models.SubjectNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Subject note not found")
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully", "id": note_id}

