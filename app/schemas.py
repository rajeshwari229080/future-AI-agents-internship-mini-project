from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator, model_validator

class StudentBase(BaseModel):
    """Base schema for student attributes with strict validation and sanitization."""
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student")
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    email: Optional[EmailStr] = Field(None, max_length=255, description="Student email address")
    phone: Optional[str] = Field(None, max_length=30, description="Contact phone number")
    course: Optional[str] = Field(None, max_length=100, description="Enrolled course name")
    address: Optional[str] = Field(None, max_length=500, description="Residential address")
    enrollment_date: Optional[date] = Field(None, description="Date of enrollment (YYYY-MM-DD)")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Name cannot be empty or purely whitespace.")
        return trimmed

    @field_validator("phone")
    @classmethod
    def sanitize_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        # Check that phone contains reasonable characters (digits, +, -, (, ), spaces)
        clean = "".join(c for c in trimmed if c.isdigit() or c in "+-() ")
        if len("".join(filter(str.isdigit, clean))) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")
        return trimmed

    @field_validator("email")
    @classmethod
    def sanitize_email(cls, v: Optional[EmailStr]) -> Optional[str]:
        if v is None:
            return None
        trimmed = str(v).strip().lower()
        return trimmed if trimmed else None

    @field_validator("course", "address")
    @classmethod
    def sanitize_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Date of birth must be in the past.")
        if v.year < 1900:
            raise ValueError("Date of birth cannot be before year 1900.")
        return v

    @field_validator("enrollment_date")
    @classmethod
    def validate_enrollment_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v.year < 1900:
            raise ValueError("Enrollment date cannot be before year 1900.")
        return v

    @model_validator(mode="after")
    def validate_contact_methods(self) -> "StudentBase":
        """Rule 1: At least one contact method (email or phone) must be provided."""
        has_email = bool(self.email and str(self.email).strip())
        has_phone = bool(self.phone and str(self.phone).strip())
        if not has_email and not has_phone:
            raise ValueError("At least one contact method (email or phone) must be provided.")
        return self


class StudentCreate(StudentBase):
    """Payload for creating a new student record."""
    pass


class StudentUpdate(StudentBase):
    """Payload for full replacement (PUT) of a student record."""
    pass


class StudentPatch(BaseModel):
    """Payload for partial updates (PATCH) with optional fields."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=30)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Name cannot be empty or purely whitespace.")
        return trimmed

    @field_validator("phone")
    @classmethod
    def sanitize_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        clean = "".join(filter(str.isdigit, trimmed))
        if len(clean) < 7:
            raise ValueError("Phone number must contain at least 7 digits.")
        return trimmed

    @field_validator("email")
    @classmethod
    def sanitize_email(cls, v: Optional[EmailStr]) -> Optional[str]:
        if v is None:
            return None
        trimmed = str(v).strip().lower()
        return trimmed if trimmed else None

    @field_validator("course", "address")
    @classmethod
    def sanitize_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v is not None:
            if v >= date.today():
                raise ValueError("Date of birth must be in the past.")
            if v.year < 1900:
                raise ValueError("Date of birth cannot be before year 1900.")
        return v

    @field_validator("enrollment_date")
    @classmethod
    def validate_enrollment_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v.year < 1900:
            raise ValueError("Enrollment date cannot be before year 1900.")
        return v


class StudentResponse(BaseModel):
    """Public representation of a student record."""
    id: int
    name: str
    date_of_birth: date
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    """Paginated response containing student records and metadata."""
    items: List[StudentResponse]
    total: int
    skip: int
    limit: int


class CourseStat(BaseModel):
    course: str
    count: int


class StudentStatsResponse(BaseModel):
    """Summary dashboard statistics calculated directly from the database."""
    total_students: int
    total_courses: int
    courses_breakdown: List[CourseStat]
    recent_students: List[StudentResponse]


# Schemas for AI Assistant
class AIQuestionRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=300, description="Natural language question about student records")

    @field_validator("question")
    @classmethod
    def sanitize_question(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Question must be at least 2 characters.")
        return trimmed


class AIAnswerResponse(BaseModel):
    question: str
    answer: str
    is_grounded: bool
    service_available: bool
    model_used: Optional[str] = None
    exact_data_included: Optional[Dict[str, Any]] = None
