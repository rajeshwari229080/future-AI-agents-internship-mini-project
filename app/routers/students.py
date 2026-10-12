from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentPatch,
    StudentResponse,
    StudentListResponse,
    StudentStatsResponse,
)
from app import crud

router = APIRouter(prefix="/students", tags=["Students"])


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create student record",
    description="Validates and registers a new student into the persistent SQLite database.",
)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db)
):
    try:
        return crud.create_student(db=db, student_in=student_in)
    except crud.DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.get(
    "/stats/summary",
    response_model=StudentStatsResponse,
    summary="Retrieve student statistics",
    description="Returns aggregate database metrics including total counts, course distribution, and recent students.",
)
def get_stats_summary(db: Session = Depends(get_db)):
    return crud.get_student_stats(db=db)


@router.get(
    "/courses",
    response_model=List[str],
    summary="List available courses",
    description="Returns a distinct list of all enrolled course names for UI filtering.",
)
def list_courses(db: Session = Depends(get_db)):
    return crud.get_distinct_courses(db=db)


@router.get(
    "",
    response_model=StudentListResponse,
    summary="List and filter students",
    description="Supports pagination, case-insensitive partial name search, and filtering by course and dates.",
)
def list_students(
    skip: int = Query(0, ge=0, description="Offset number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Case-insensitive partial student name search"),
    course: Optional[str] = Query(None, description="Filter by exact course name"),
    enrollment_date: Optional[date] = Query(None, description="Filter by enrollment date"),
    date_of_birth: Optional[date] = Query(None, description="Filter by date of birth"),
    db: Session = Depends(get_db),
):
    items, total = crud.get_students(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        course=course,
        enrollment_date=enrollment_date,
        date_of_birth=date_of_birth,
    )
    return StudentListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Retrieve a student by ID",
    description="Fetches a single student record. Returns 404 if not found.",
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update a student (Full replacement)",
    description="Replaces all student attributes while retaining the primary key ID.",
)
def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    try:
        return crud.update_student(db=db, student=student, student_in=student_in)
    except crud.DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Partially update a student",
    description="Updates only the fields provided. Unspecified fields remain untouched.",
)
def patch_student(
    student_id: int,
    student_in: StudentPatch,
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    try:
        return crud.patch_student(db=db, student=student, student_in=student_in)
    except crud.DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    except crud.InvalidContactError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc)
        )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student",
    description="Permanently deletes the student record from SQLite.",
)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = crud.get_student(db=db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    crud.delete_student(db=db, student=student)
    return None
