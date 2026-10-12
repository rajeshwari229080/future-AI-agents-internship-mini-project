from datetime import date
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentPatch

class DuplicateEmailError(ValueError):
    """Raised when an email address is already assigned to another student."""
    pass

class InvalidContactError(ValueError):
    """Raised when an update removes all contact methods."""
    pass


def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Retrieves a student by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_email(db: Session, email: str, exclude_id: Optional[int] = None) -> Optional[Student]:
    """Retrieves a student by email address, optionally excluding a specific student ID."""
    if not email:
        return None
    query = db.query(Student).filter(func.lower(Student.email) == email.lower().strip())
    if exclude_id is not None:
        query = query.filter(Student.id != exclude_id)
    return query.first()


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    course: Optional[str] = None,
    enrollment_date: Optional[date] = None,
    date_of_birth: Optional[date] = None,
) -> Tuple[List[Student], int]:
    """
    Retrieves a paginated list of students with optional search and filters.
    Returns (items, total_count).
    """
    query = db.query(Student)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(Student.name.ilike(search_term))

    if course and course.strip() and course.strip().lower() != "all":
        query = query.filter(Student.course.ilike(course.strip()))

    if enrollment_date:
        query = query.filter(Student.enrollment_date == enrollment_date)

    if date_of_birth:
        query = query.filter(Student.date_of_birth == date_of_birth)

    total_count = query.count()
    items = query.order_by(desc(Student.id)).offset(skip).limit(limit).all()

    return items, total_count


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Inserts a new student record after validating unique constraints."""
    if student_in.email:
        existing = get_student_by_email(db, student_in.email)
        if existing:
            raise DuplicateEmailError(f"A student with email '{student_in.email}' already exists.")

    student = Student(
        name=student_in.name,
        date_of_birth=student_in.date_of_birth,
        email=student_in.email,
        phone=student_in.phone,
        course=student_in.course,
        address=student_in.address,
        enrollment_date=student_in.enrollment_date,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(db: Session, student: Student, student_in: StudentUpdate) -> Student:
    """
    Full replacement update (PUT semantics).
    Preserves original primary key id while updating all provided attributes.
    """
    if student_in.email:
        existing = get_student_by_email(db, student_in.email, exclude_id=student.id)
        if existing:
            raise DuplicateEmailError(f"A student with email '{student_in.email}' already exists.")

    student.name = student_in.name
    student.date_of_birth = student_in.date_of_birth
    student.email = student_in.email
    student.phone = student_in.phone
    student.course = student_in.course
    student.address = student_in.address
    student.enrollment_date = student_in.enrollment_date

    db.commit()
    db.refresh(student)
    return student


def patch_student(db: Session, student: Student, student_in: StudentPatch) -> Student:
    """
    Partial update (PATCH semantics).
    Applies only fields provided in the payload while preserving omitted fields.
    Validates that the resulting student still retains at least one contact method.
    """
    update_data = student_in.model_dump(exclude_unset=True)

    # Check resulting contact information
    target_email = update_data.get("email", student.email)
    target_phone = update_data.get("phone", student.phone)

    has_email = bool(target_email and str(target_email).strip())
    has_phone = bool(target_phone and str(target_phone).strip())

    if not has_email and not has_phone:
        raise InvalidContactError("Update rejected: At least one contact method (email or phone) must remain.")

    # Check email uniqueness if email is modified
    if "email" in update_data and target_email:
        existing = get_student_by_email(db, target_email, exclude_id=student.id)
        if existing:
            raise DuplicateEmailError(f"A student with email '{target_email}' already exists.")

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student: Student) -> None:
    """Deletes a student record permanently from SQLite."""
    db.delete(student)
    db.commit()


def get_student_stats(db: Session) -> Dict[str, Any]:
    """Calculates live statistical aggregates for the administration dashboard."""
    total_students = db.query(func.count(Student.id)).scalar() or 0

    # Group by course (treat NULL as 'Unassigned')
    course_query = (
        db.query(
            func.coalesce(Student.course, "Unassigned").label("course_name"),
            func.count(Student.id).label("student_count")
        )
        .group_by("course_name")
        .order_by(desc("student_count"))
        .all()
    )

    courses_breakdown = [
        {"course": row[0], "count": row[1]}
        for row in course_query
    ]
    total_courses = len([c for c in courses_breakdown if c["course"] != "Unassigned"])

    recent_students = (
        db.query(Student)
        .order_by(desc(Student.id))
        .limit(5)
        .all()
    )

    return {
        "total_students": total_students,
        "total_courses": total_courses,
        "courses_breakdown": courses_breakdown,
        "recent_students": recent_students,
    }


def get_distinct_courses(db: Session) -> List[str]:
    """Retrieves all distinct non-empty course names for filtering dropdowns."""
    courses = (
        db.query(Student.course)
        .filter(Student.course.isnot(None), Student.course != "")
        .distinct()
        .order_by(Student.course)
        .all()
    )
    return [c[0] for c in courses if c[0]]


def get_grounded_records_for_ai(db: Session, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Safely retrieves a bounded list of student records for AI context.
    Omits sensitive contact details (phone, email, full address) to protect privacy.
    """
    students = db.query(Student).order_by(desc(Student.id)).limit(limit).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "date_of_birth": s.date_of_birth.isoformat() if s.date_of_birth else None,
            "course": s.course or "Unassigned",
            "enrollment_date": s.enrollment_date.isoformat() if s.enrollment_date else None,
        }
        for s in students
    ]
