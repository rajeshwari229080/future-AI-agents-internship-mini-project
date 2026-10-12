from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, func
from app.database import Base

class Student(Base):
    """
    SQLAlchemy ORM model for student records.
    Persistent in SQLite with strict types and indexing.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    phone = Column(String(30), nullable=True, index=True)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(500), nullable=True)
    enrollment_date = Column(Date, nullable=True, index=True)
    
    # Metadata for audit tracking
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        """Converts model instance to a dictionary with ISO-formatted dates."""
        return {
            "id": self.id,
            "name": self.name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "email": self.email,
            "phone": self.phone,
            "course": self.course,
            "address": self.address,
            "enrollment_date": self.enrollment_date.isoformat() if self.enrollment_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Student id={self.id} name='{self.name}' course='{self.course}'>"
