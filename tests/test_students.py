from datetime import date, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Student
from app.database import Base

def test_create_valid_student(client):
    """Verify that a valid student record is created with HTTP 201."""
    payload = {
        "name": "Alan Turing",
        "date_of_birth": "2000-06-23",
        "email": "alan.turing@example.edu",
        "phone": "+1-555-1234567",
        "course": "Computer Science",
        "address": "Bletchley Park",
        "enrollment_date": "2020-09-01",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "Alan Turing"
    assert data["email"] == "alan.turing@example.edu"
    assert data["date_of_birth"] == "2000-06-23"
    assert data["course"] == "Computer Science"


def test_create_student_with_only_email(client):
    """Verify student creation succeeds when only email is provided."""
    payload = {
        "name": "Ada Lovelace",
        "date_of_birth": "2001-12-10",
        "email": "ada.lovelace@example.edu",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ada Lovelace"
    assert data["email"] == "ada.lovelace@example.edu"
    assert data["phone"] is None


def test_create_student_with_only_phone(client):
    """Verify student creation succeeds when only phone is provided."""
    payload = {
        "name": "Grace Hopper",
        "date_of_birth": "2002-12-09",
        "phone": "+1-555-9876543",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Grace Hopper"
    assert data["phone"] == "+1-555-9876543"
    assert data["email"] is None


def test_reject_missing_name(client):
    """Verify validation error when name is missing or empty."""
    payload = {
        "name": "   ",
        "date_of_birth": "2002-01-01",
        "email": "test@example.edu",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_reject_invalid_email(client):
    """Verify validation error when email format is invalid."""
    payload = {
        "name": "John Doe",
        "date_of_birth": "2002-01-01",
        "email": "not-an-email",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_reject_future_date_of_birth(client):
    """Verify validation error when date of birth is in the future."""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    payload = {
        "name": "Future Student",
        "date_of_birth": tomorrow,
        "email": "future@example.edu",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_reject_missing_both_email_and_phone(client):
    """Verify rejection when neither email nor phone is provided."""
    payload = {
        "name": "No Contact Student",
        "date_of_birth": "2000-01-01",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422


def test_reject_duplicate_email(client):
    """Verify rejection when registering duplicate email address."""
    payload1 = {
        "name": "Student One",
        "date_of_birth": "2001-01-01",
        "email": "duplicate@example.edu",
    }
    res1 = client.post("/students", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "name": "Student Two",
        "date_of_birth": "2002-02-02",
        "email": "duplicate@example.edu",
    }
    res2 = client.post("/students", json=payload2)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_list_students_and_pagination(client):
    """Verify listing students and pagination boundary limits."""
    # Create 5 students
    for i in range(5):
        client.post("/students", json={
            "name": f"Student {i}",
            "date_of_birth": "2002-01-01",
            "email": f"student{i}@example.edu",
        })

    # Test limit=2, skip=0
    res = client.get("/students?skip=0&limit=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["skip"] == 0
    assert data["limit"] == 2

    # Test skip=4
    res_page = client.get("/students?skip=4&limit=2")
    assert res_page.status_code == 200
    assert len(res_page.json()["items"]) == 1


def test_search_by_name_case_insensitive(client):
    """Verify case-insensitive partial name search."""
    client.post("/students", json={"name": "Alice Wonder", "date_of_birth": "2001-05-10", "email": "alice@example.edu"})
    client.post("/students", json={"name": "Bob Builder", "date_of_birth": "2002-06-15", "email": "bob@example.edu"})

    res = client.get("/students?search=wOnDeR")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Alice Wonder"


def test_filter_by_course(client):
    """Verify filtering students by course."""
    client.post("/students", json={"name": "Student A", "date_of_birth": "2001-01-01", "email": "a@example.edu", "course": "Physics"})
    client.post("/students", json={"name": "Student B", "date_of_birth": "2001-01-01", "email": "b@example.edu", "course": "Chemistry"})

    res = client.get("/students?course=Physics")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["course"] == "Physics"


def test_get_student_by_id(client):
    """Verify retrieving a student by ID."""
    created = client.post("/students", json={
        "name": "Target Student",
        "date_of_birth": "2003-03-03",
        "email": "target@example.edu",
    }).json()

    res = client.get(f"/students/{created['id']}")
    assert res.status_code == 200
    assert res.json()["name"] == "Target Student"


def test_get_nonexistent_student_returns_404(client):
    """Verify 404 for a missing student record."""
    res = client.get("/students/999999")
    assert res.status_code == 404


def test_update_student_put(client):
    """Verify full replacement (PUT) updates record while preserving ID."""
    created = client.post("/students", json={
        "name": "Old Name",
        "date_of_birth": "2000-01-01",
        "email": "old@example.edu",
        "course": "Math",
    }).json()

    put_payload = {
        "name": "New Name",
        "date_of_birth": "2000-01-01",
        "email": "new@example.edu",
        "phone": "+1-555-4321000",
        "course": "Applied Mathematics",
        "address": "New Hall",
        "enrollment_date": "2021-09-01",
    }
    res = client.put(f"/students/{created['id']}", json=put_payload)
    assert res.status_code == 200
    updated = res.json()
    assert updated["id"] == created["id"]
    assert updated["name"] == "New Name"
    assert updated["email"] == "new@example.edu"
    assert updated["course"] == "Applied Mathematics"


def test_patch_student_partial_update(client):
    """Verify partial update (PATCH) modifies only specified fields."""
    created = client.post("/students", json={
        "name": "Partial Name",
        "date_of_birth": "2002-04-12",
        "email": "partial@example.edu",
        "course": "History",
    }).json()

    # Modify only the course
    res = client.patch(f"/students/{created['id']}", json={"course": "Ancient History"})
    assert res.status_code == 200
    patched = res.json()
    assert patched["course"] == "Ancient History"
    # Verify omitted fields remain unchanged
    assert patched["name"] == "Partial Name"
    assert patched["email"] == "partial@example.edu"
    assert patched["date_of_birth"] == "2002-04-12"


def test_patch_student_rejects_removing_all_contacts(client):
    """Verify that PATCH rejects an update that removes all contact options."""
    created = client.post("/students", json={
        "name": "Contact Test",
        "date_of_birth": "2001-01-01",
        "email": "contact@example.edu",
        "phone": None,
    }).json()

    # Attempting to set email to None when phone is already None
    res = client.patch(f"/students/{created['id']}", json={"email": None})
    assert res.status_code == 422


def test_delete_student_and_subsequent_get(client):
    """Verify DELETE removes record with 204 and subsequent GET returns 404."""
    created = client.post("/students", json={
        "name": "To Delete",
        "date_of_birth": "2001-01-01",
        "email": "delete.me@example.edu",
    }).json()

    del_res = client.delete(f"/students/{created['id']}")
    assert del_res.status_code == 204

    get_res = client.get(f"/students/{created['id']}")
    assert get_res.status_code == 404


def test_delete_nonexistent_student_returns_404(client):
    """Verify DELETE on nonexistent record returns 404."""
    res = client.delete("/students/999999")
    assert res.status_code == 404


def test_get_stats_summary(client):
    """Verify statistics summary calculation."""
    client.post("/students", json={"name": "S1", "date_of_birth": "2001-01-01", "email": "s1@example.edu", "course": "AI"})
    client.post("/students", json={"name": "S2", "date_of_birth": "2001-01-01", "email": "s2@example.edu", "course": "AI"})
    client.post("/students", json={"name": "S3", "date_of_birth": "2001-01-01", "email": "s3@example.edu", "course": "Bio"})

    res = client.get("/students/stats/summary")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_students"] == 3
    assert stats["total_courses"] == 2


def test_database_persistence_across_reconnection(test_db_file):
    """
    Verifies that records written to SQLite persist across distinct engine
    instances and database reconnections.
    """
    normalized_path = str(test_db_file).replace("\\", "/")
    db_url = f"sqlite:///{normalized_path}"
    
    # Session 1: Write record
    engine1 = create_engine(db_url)
    Session1 = sessionmaker(bind=engine1)
    s1 = Session1()
    student = Student(
        name="Persistent Student",
        date_of_birth=date(2000, 1, 1),
        email="persist@example.edu",
        course="Data Architecture"
    )
    s1.add(student)
    s1.commit()
    assigned_id = student.id
    s1.close()
    engine1.dispose()

    # Session 2: Fresh engine reconnecting to same SQLite file
    engine2 = create_engine(db_url)
    Session2 = sessionmaker(bind=engine2)
    s2 = Session2()
    fetched = s2.query(Student).filter(Student.id == assigned_id).first()
    assert fetched is not None
    assert fetched.name == "Persistent Student"
    assert fetched.email == "persist@example.edu"
    s2.close()
    engine2.dispose()
