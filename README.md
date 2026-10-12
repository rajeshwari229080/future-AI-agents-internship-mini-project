# Student Record Management System

Production-grade, full-stack **Student Record Management System** developed for the **EWB Edu Tech Pvt. Ltd.** internship assignment. Built with **FastAPI**, **SQLAlchemy ORM**, **SQLite**, **Pydantic v2**, a modern responsive **Administration Dashboard**, and an optional grounded local **Ollama AI Assistant**.

---

## Table of Contents

1. [Project Title & Overview](#1-project-title--overview)
2. [Project Objective](#2-project-objective)
3. [Key Features](#3-key-features)
4. [Technology Stack](#4-technology-stack)
5. [Architecture & Request Flow](#5-architecture--request-flow)
6. [Project Structure](#6-project-structure)
7. [Prerequisites](#7-prerequisites)
8. [Windows Installation Instructions](#8-windows-installation-instructions)
9. [Application Startup Instructions](#9-application-startup-instructions)
10. [Local Database Behavior & Location](#10-local-database-behavior--location)
11. [CRUD Concept Explanation](#11-understanding-crud-operations)
12. [API Endpoint Reference](#12-api-endpoint-reference)
13. [Example JSON Requests & Responses](#13-example-json-requests--responses)
14. [Interactive API Testing (/docs)](#14-interactive-api-testing-using-docs)
15. [Automated Testing Suite (pytest)](#15-automated-testing-instructions)
16. [Sample Data Seeding Instructions](#16-sample-data-instructions)
17. [Optional Local AI Assistant (Ollama) Setup](#17-optional-local-ai-assistant-using-ollama)
18. [Troubleshooting](#18-troubleshooting)
19. [Security and Privacy Controls](#19-security-and-privacy-notes)
20. [GitHub Submission Checklist & Git Commands](#20-github-submission-checklist--git-commands)

---

## 1. Project Title & Overview

**Student Record Management System**  
A reliable, scalable academic administration web application providing end-to-end management of student lifecycle records. Features strict data validation, relational persistence in SQLite, an interactive administrative frontend, and safe natural-language querying via local LLMs.

---

## 2. Project Objective

To build an industry-standard student record management solution that:
- Implements robust Create, Read, Update, and Delete (CRUD) operations.
- Persists all data reliably in a local SQLite database across restarts.
- Enforces strict data sanitization and schema validation using Pydantic and SQLAlchemy.
- Provides an intuitive, responsive administrative web interface adhering to academic administration standards.
- Integrates an optional local AI assistant using Ollama with strict context grounding and zero arbitrary code/SQL execution risk.

---

## 3. Key Features

- **Full Lifecycle Student CRUD**:
  - Register students with unique IDs, names, dates of birth, contact information, courses, addresses, and enrollment dates.
  - Paginated browsing with customizable limits (`limit=10, 25, 50`).
  - Real-time case-insensitive student name search (debounced).
  - Dynamic course filtering.
  - Complete replacement update (`PUT`) and selective partial update (`PATCH`).
  - Safe deletion with two-step confirmation modals.
- **Strict Data Validation & Rules**:
  - Name is mandatory, trimmed, and non-empty.
  - At least one contact method (email or phone) is strictly required upon creation and updates.
  - Real-time validation of email formats and minimum phone digit lengths.
  - Date of birth cannot be in the future.
  - Documented email uniqueness policy to prevent duplicate student profiles.
- **Live Statistical Dashboard**:
  - Total registered students count.
  - Active course counts.
  - Dynamic distribution breakdown tags.
  - Recent student registrations.
- **Optional Grounded AI Assistant (Ollama)**:
  - Natural language querying (e.g. *"How many students are enrolled?"*, *"Which courses have the most students?"*, *"Show students born after 2005"*).
  - 100% deterministic calculation of counts and summaries directly in Python/SQL to prevent LLM hallucinations.
  - Graceful degradation: If Ollama is offline or not installed, the application calculates and displays exact answers directly without interruption.
  - Strict privacy: Contact numbers and private addresses are excluded from AI prompts.

---

## 4. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | FastAPI (Python 3.11+) | Asynchronous REST API, routing, request validation |
| **ORM / Data Layer** | SQLAlchemy 2.0 | Parameterized database queries, relational models, transactional integrity |
| **Validation Layer** | Pydantic v2 & `email-validator` | Request parsing, strict sanitization, contact rule enforcement |
| **Database** | SQLite 3 | Project-relative persistent relational storage |
| **Frontend UI** | HTML5, Vanilla CSS3, Modern JS | Clean academic dashboard, modals, toast alerts, debounced search |
| **Templating** | Jinja2 | Dashboard rendering from FastAPI |
| **Local AI (Optional)** | Ollama (`llama3.2:1b`) | Grounded natural language query engine |
| **Testing** | Pytest & `httpx` (TestClient) | Automated end-to-end CRUD, edge case, and AI mock testing |
| **Server** | Uvicorn | ASGI production-grade HTTP application server |

---

## 5. Architecture & Request Flow

```
                      +-----------------------------------+
                      |       Web Browser (Frontend)      |
                      |   HTML5 / Vanilla CSS / ES6 JS    |
                      +-----------------+-----------------+
                                        | HTTP (Fetch JSON)
                                        v
                      +-----------------------------------+
                      |        FastAPI Application        |
                      |    (Security Headers, CORS, DI)   |
                      +--------+-----------------+--------+
                               |                 |
                /students CRUD |                 | /ai/ask (Optional)
                               v                 v
                      +----------------+   +----------------------+
                      |  Pydantic v2   |   |    Ollama Service    |
                      | Validation &   |   |   (Safe Grounding    |
                      | Business Logic |   | + Python Analytics)  |
                      +--------+-------+   +----------+-----------+
                               |                      |
                               v                      | Local HTTP (11434)
                      +----------------+              v
                      | SQLAlchemy ORM |    +-------------------+
                      +--------+-------+    |  Local Ollama LLM |
                               |            |   (llama3.2:1b)   |
                               v            +-------------------+
                      +----------------+
                      | SQLite Storage |
                      | (students.db)  |
                      +----------------+
```

---

## 6. Project Structure

```
student-record-management/
├── app/
│   ├── __init__.py               # Application package definition
│   ├── config.py                 # Pydantic BaseSettings, project-relative paths
│   ├── database.py             # SQLAlchemy engine, session maker, get_db dependency
│   ├── models.py                 # SQLAlchemy Student ORM table model
│   ├── schemas.py                # Pydantic schemas, field validators, contact logic
│   ├── crud.py                   # Parameterized database queries, transactional updates
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py           # REST API endpoints for /students and /students/stats
│   │   └── ai.py                 # Endpoints for /ai/ask and /ai/status
│   ├── services/
│   │   ├── __init__.py
│   │   └── ollama_service.py     # Safe Ollama integration, grounding, fallback stats
│   ├── templates/
│   │   └── index.html            # Administrative dashboard single-page HTML
│   └── static/
│       ├── css/
│       │   └── style.css         # Academic administration styling and design tokens
│       └── js/
│           └── app.js            # Table rendering, modals, AJAX CRUD, toast notifications
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Temporary test SQLite fixtures & TestClient setup
│   ├── test_students.py          # 20 automated tests for CRUD, validation, and persistence
│   └── test_ai.py                # 5 automated tests for AI validation and mocked Ollama
├── seed_data.py                  # CLI script to populate 12 fictional student records
├── run.py                        # Application entry point script
├── requirements.txt              # Production and testing Python dependencies
├── .env.example                  # Environment configuration template
├── .gitignore                    # Excludes *.db, .venv, cache, and secrets
└── README.md                     # Comprehensive documentation
```

---

## 7. Prerequisites

- **Python 3.10+** (Tested on Python 3.11.9).
- **Git** installed on Windows.
- **PowerShell** or Command Prompt.
- *(Optional)*: [Ollama](https://ollama.com/) for local AI capabilities.

---

## 8. Windows Installation Instructions

1. **Open PowerShell** and navigate to your project directory:
   ```powershell
   cd "d:\current project\future AI agent\rw"
   ```

2. **Create a virtual environment**:
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   *(If script execution is restricted, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

4. **Install all required dependencies**:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

---

## 9. Application Startup Instructions

### Option A: Using the Launcher Script (Recommended)
```powershell
python run.py
```

### Option B: Using Uvicorn Directly
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started:
- **Web Dashboard**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in any web browser.
- **Swagger Documentation**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- **ReDoc Documentation**: Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

---

## 10. Local Database Behavior & Location

- **Engine**: SQLite 3 using SQLAlchemy ORM with foreign keys enabled.
- **File Location**: Relative to the project root at `./students.db`.
- **Automatic Initialization**: Database tables (`students`) are automatically created on startup via FastAPI's `lifespan` handler.
- **Persistence Guarantee**: All data added, edited, or deleted is permanently written to disk. Restarting the server preserves all student records intact.
- **Version Control Safety**: SQLite files (`*.db`, `*.sqlite`, `*.sqlite3`) are explicitly ignored by `.gitignore` to prevent committing local data.

---

## 11. Understanding CRUD Operations

| Operation | HTTP Verb | Endpoint | Description |
|---|---|---|---|
| **Create** | `POST` | `/students` | Validates student payload, ensures contact method rules and email uniqueness, and inserts a new student record into SQLite. Returns HTTP `201 Created`. |
| **Read (List)** | `GET` | `/students` | Queries records with pagination (`skip`, `limit`), name search, and course filtering. Returns paginated results with `total` count. |
| **Read (Single)**| `GET` | `/students/{id}` | Fetches a specific student by primary key ID. Returns HTTP `200 OK` or `404 Not Found`. |
| **Update (Full)**| `PUT` | `/students/{id}` | Replaces the complete student record while preserving the original ID. Validates all required fields. |
| **Update (Partial)**| `PATCH` | `/students/{id}` | Updates only provided fields, leaving omitted fields unchanged. Validates that at least one contact method remains. |
| **Delete** | `DELETE`| `/students/{id}` | Permanently removes the student record from SQLite. Returns HTTP `204 No Content`. |

---

## 12. API Endpoint Reference

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/students` | Create a new student record | `201 Created` |
| `GET` | `/students` | List students with search, filters, and pagination | `200 OK` |
| `GET` | `/students/stats/summary` | Retrieve live aggregate statistics and course distribution | `200 OK` |
| `GET` | `/students/courses` | List distinct active course names for filter dropdowns | `200 OK` |
| `GET` | `/students/{student_id}` | Retrieve a single student by ID | `200 OK` / `404` |
| `PUT` | `/students/{student_id}` | Full replacement update of a student record | `200 OK` / `404` / `400` |
| `PATCH` | `/students/{student_id}` | Partial update of student fields | `200 OK` / `404` / `422` |
| `DELETE` | `/students/{student_id}` | Permanently delete a student record | `204 No Content` / `404` |
| `POST` | `/ai/ask` | Ask grounded natural-language questions about students | `200 OK` |
| `GET` | `/ai/status` | Check local Ollama daemon connectivity | `200 OK` |
| `GET` | `/health` | Health check endpoint | `200 OK` |

---

## 13. Example JSON Requests & Responses

### 1. Create Student (`POST /students`)
**Request Body**:
```json
{
  "name": "Eleanor Vance",
  "date_of_birth": "2003-04-15",
  "email": "eleanor.vance@example.edu",
  "phone": "+1-555-0101",
  "course": "Computer Science",
  "address": "404 Logic Gate Way, Silicon Valley, CA",
  "enrollment_date": "2022-09-01"
}
```
**Response (`201 Created`)**:
```json
{
  "id": 1,
  "name": "Eleanor Vance",
  "date_of_birth": "2003-04-15",
  "email": "eleanor.vance@example.edu",
  "phone": "+1-555-0101",
  "course": "Computer Science",
  "address": "404 Logic Gate Way, Silicon Valley, CA",
  "enrollment_date": "2022-09-01",
  "created_at": "2026-10-12T08:31:27.123456",
  "updated_at": "2026-10-12T08:31:27.123456"
}
```

### 2. List Students (`GET /students?skip=0&limit=10&search=eleanor`)
**Response (`200 OK`)**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "Eleanor Vance",
      "date_of_birth": "2003-04-15",
      "email": "eleanor.vance@example.edu",
      "phone": "+1-555-0101",
      "course": "Computer Science",
      "address": "404 Logic Gate Way, Silicon Valley, CA",
      "enrollment_date": "2022-09-01",
      "created_at": "2026-10-12T08:31:27.123456",
      "updated_at": "2026-10-12T08:31:27.123456"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### 3. Partial Update (`PATCH /students/1`)
**Request Body**:
```json
{
  "course": "Artificial Intelligence"
}
```
**Response (`200 OK`)**:
```json
{
  "id": 1,
  "name": "Eleanor Vance",
  "date_of_birth": "2003-04-15",
  "email": "eleanor.vance@example.edu",
  "phone": "+1-555-0101",
  "course": "Artificial Intelligence",
  "address": "404 Logic Gate Way, Silicon Valley, CA",
  "enrollment_date": "2022-09-01",
  "created_at": "2026-10-12T08:31:27.123456",
  "updated_at": "2026-10-12T08:35:12.789101"
}
```

### 4. Ask AI Assistant (`POST /ai/ask`)
**Request Body**:
```json
{
  "question": "How many students are registered?"
}
```
**Response (`200 OK`)**:
```json
{
  "question": "How many students are registered?",
  "answer": "There are currently 12 student(s) registered in the database.",
  "is_grounded": true,
  "service_available": false,
  "model_used": null,
  "exact_data_included": {
    "total_students": 12,
    "total_courses": 5,
    "courses_breakdown": [
      {"course": "Computer Science", "count": 2},
      {"course": "Data Science", "count": 2},
      {"course": "Mechanical Engineering", "count": 2},
      {"course": "Information Technology", "count": 2},
      {"course": "Cybersecurity", "count": 2},
      {"course": "Artificial Intelligence", "count": 2}
    ]
  }
}
```

---

## 14. Interactive API Testing Using `/docs`

FastAPI provides an automated interactive Swagger UI:
1. Start the server and navigate to `http://127.0.0.1:8000/docs`.
2. Expand any endpoint (e.g. `POST /students`).
3. Click **"Try it out"**.
4. Paste the sample JSON payload and click **"Execute"**.
5. Inspect the response body, response headers, and HTTP status code.

---

## 15. Automated Testing Instructions

The repository includes a comprehensive automated test suite powered by `pytest` and FastAPI's `TestClient`.

### Run All Tests:
```powershell
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- **25 automated tests**, covering:
  - Valid student creation (`201 Created`).
  - Single contact support (email-only or phone-only).
  - Validation rejections: missing/blank name, malformed email, future date of birth, neither email nor phone provided (`422 Unprocessable Content`).
  - Email uniqueness collision rejection (`400 Bad Request`).
  - Paginated browsing and boundary checking.
  - Case-insensitive partial name search.
  - Course filtering.
  - Single student retrieval and `404 Not Found` handling.
  - Complete replacement (`PUT`) preserving IDs.
  - Selective partial updates (`PATCH`) and contact preservation rules.
  - Deletion verification (`204 No Content`) and post-deletion retrieval verification (`404`).
  - SQLite persistence across engine reconnections and separate sessions.
  - AI status, input validation, offline metric calculation, and mocked Ollama responses.

---

## 16. Sample Data Instructions

To populate the local SQLite database with realistic, fictional student demonstration records:

```powershell
python seed_data.py
```

This populates 12 fictional records across diverse courses (*Computer Science*, *Data Science*, *Cybersecurity*, *Mechanical Engineering*, *Artificial Intelligence*).

---

## 17. Optional Local AI Assistant Using Ollama

The AI Assistant is an optional extension. **The core student management system runs completely independently of Ollama.**

### Setup Ollama (Optional):
1. Download and install Ollama from [ollama.com](https://ollama.com/).
2. Pull the lightweight local model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Start the Ollama daemon:
   ```bash
   ollama serve
   ```
4. Verify Ollama is reachable at `http://localhost:11434`.

### AI Assistant Safety Rules:
1. **Zero SQL Injection / Code Execution**: The LLM is never given direct database or system access.
2. **Context Grounding**: The LLM receives only safe, pre-formatted read-only facts.
3. **Privacy First**: Sensitive contact information (phones, personal addresses) is omitted from AI prompts.
4. **Deterministic Accuracy**: Mathematical totals, course counts, and filtering are computed directly in Python/SQL.
5. **Offline Fallback**: When Ollama is offline, the endpoint seamlessly serves calculated database metrics without errors.

---

## 18. Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `Port 8000 already in use` | Another process is occupying port 8000. | Start on a different port: `python -m uvicorn app.main:app --port 8080` |
| `ModuleNotFoundError: No module named 'fastapi'` | Virtual environment not activated. | Run `.venv\Scripts\Activate.ps1` and verify `pip list`. |
| `AI Assistant shows "Offline"` | Local Ollama is not installed or not running. | Normal behavior! The application operates in Direct Metrics Mode. To enable AI, run `ollama serve`. |
| `At least one contact method required` | Student was submitted without both email and phone. | Enter at least a valid email or a phone number. |

---

## 19. Security and Privacy Notes

- **Input Sanitization**: Whitespace is trimmed; strict lengths are enforced on all fields.
- **SQL Injection Prevention**: All queries use SQLAlchemy ORM parameterized statements.
- **XSS & HTML Injection Protection**: The frontend uses safe DOM APIs (`textContent`, sanitization routines) preventing HTML injection.
- **Security Headers**: Standard defense-in-depth headers applied (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1`).
- **Privacy Assurance**: Sample data contains only fictional demonstration records. Real personal data must never be loaded into public repositories.
- **Production Note**: If deploying to a public environment, introduce JWT/OAuth2 authentication and HTTPS reverse proxy termination.

---

## 20. GitHub Submission Checklist & Git Commands

### Pre-Submission Checklist:
- [x] All 25 automated tests pass (`python -m pytest tests/ -v`).
- [x] SQLite database files (`*.db`) and `.env` excluded via `.gitignore`.
- [x] Web dashboard verified with full CRUD functionality.
- [x] Interactive Swagger UI available at `/docs`.
- [x] Dependencies documented in `requirements.txt`.
- [x] Ollama optional extension tested and documented.

### Git Submission Commands:
To initialize git, link your repository, and push the project to GitHub:

```bash
git init
git add .
git commit -m "feat: complete student record management system with CRUD, UI, and AI assistant"
git remote add origin https://github.com/rajeshwari229080/future-AI-agents-internship-mini-project.git
git branch -M main
git push -u origin main
```

---

## 21. License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete details.
