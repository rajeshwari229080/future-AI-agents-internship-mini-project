"""
Seed Data Script for Student Record Management System.
Populates the persistent SQLite database with realistic, fictional student demonstration records.
"""

from datetime import date
from app.database import SessionLocal, init_db
from app.models import Student

DEMO_STUDENTS = [
    {
        "name": "Eleanor Vance",
        "date_of_birth": date(2003, 4, 15),
        "email": "eleanor.vance@example.edu",
        "phone": "+1-555-0101",
        "course": "Computer Science",
        "address": "404 Logic Gate Way, Silicon Valley, CA",
        "enrollment_date": date(2022, 9, 1),
    },
    {
        "name": "Marcus Aurelius Thorne",
        "date_of_birth": date(2002, 11, 28),
        "email": "marcus.thorne@example.edu",
        "phone": "+1-555-0102",
        "course": "Mechanical Engineering",
        "address": "742 Evergreen Terrace, Springfield, OR",
        "enrollment_date": date(2021, 9, 1),
    },
    {
        "name": "Amina Zahra Al-Mansoor",
        "date_of_birth": date(2004, 2, 10),
        "email": "amina.mansoor@example.edu",
        "phone": "+1-555-0103",
        "course": "Data Science",
        "address": "120 Oasis Boulevard, Phoenix, AZ",
        "enrollment_date": date(2023, 1, 15),
    },
    {
        "name": "Liam Connor O'Sullivan",
        "date_of_birth": date(2001, 7, 19),
        "email": "liam.osullivan@example.edu",
        "phone": "+1-555-0104",
        "course": "Information Technology",
        "address": "55 Clover Lane, Boston, MA",
        "enrollment_date": date(2021, 9, 1),
    },
    {
        "name": "Sophia Mei-Ling Chen",
        "date_of_birth": date(2003, 9, 5),
        "email": "sophia.chen@example.edu",
        "phone": "+1-555-0105",
        "course": "Computer Science",
        "address": "88 Horizon Heights, Seattle, WA",
        "enrollment_date": date(2022, 9, 1),
    },
    {
        "name": "Lucas Gabriel Silva",
        "date_of_birth": date(2002, 5, 23),
        "email": "lucas.silva@example.edu",
        "phone": "+1-555-0106",
        "course": "Artificial Intelligence",
        "address": "310 Palm Avenue, Miami, FL",
        "enrollment_date": date(2022, 1, 10),
    },
    {
        "name": "Priya Ananya Sharma",
        "date_of_birth": date(2004, 8, 14),
        "email": "priya.sharma@example.edu",
        "phone": "+1-555-0107",
        "course": "Cybersecurity",
        "address": "16 Lotus Court, Austin, TX",
        "enrollment_date": date(2023, 9, 1),
    },
    {
        "name": "Julian Montgomery Sterling",
        "date_of_birth": date(2006, 1, 30),
        "email": "julian.sterling@example.edu",
        "phone": "+1-555-0108",
        "course": "Artificial Intelligence",
        "address": "19 Highclere Road, Cambridge, MA",
        "enrollment_date": date(2024, 9, 1),
    },
    {
        "name": "Fatima Zahra Khan",
        "date_of_birth": date(2005, 12, 12),
        "email": "fatima.khan@example.edu",
        "phone": "+1-555-0109",
        "course": "Data Science",
        "address": "24 Crescent Way, Chicago, IL",
        "enrollment_date": date(2024, 1, 15),
    },
    {
        "name": "Benjamin Noah Hayes",
        "date_of_birth": date(2002, 3, 8),
        "email": "benjamin.hayes@example.edu",
        "phone": "+1-555-0110",
        "course": "Mechanical Engineering",
        "address": "902 Pine Ridge Path, Denver, CO",
        "enrollment_date": date(2021, 9, 1),
    },
    {
        "name": "Chloe Isabella Rossi",
        "date_of_birth": date(2006, 6, 21),
        "email": "chloe.rossi@example.edu",
        "phone": "+1-555-0111",
        "course": "Cybersecurity",
        "address": "45 Riviera Drive, San Diego, CA",
        "enrollment_date": date(2024, 9, 1),
    },
    {
        "name": "David Emmanuel Okafor",
        "date_of_birth": date(2003, 10, 11),
        "email": "david.okafor@example.edu",
        "phone": "+1-555-0112",
        "course": "Information Technology",
        "address": "77 Beacon Street, Philadelphia, PA",
        "enrollment_date": date(2022, 9, 1),
    },
]

def seed_database():
    """Initializes tables and seeds initial fictional records if empty."""
    init_db()
    db = SessionLocal()
    try:
        existing_count = db.query(Student).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} records. Skipping seeding.")
            return

        print(f"Seeding database with {len(DEMO_STUDENTS)} fictional student demonstration records...")
        for data in DEMO_STUDENTS:
            student = Student(**data)
            db.add(student)
        db.commit()
        print("Database seeding completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
