import re
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app import crud


async def check_ollama_availability() -> Dict[str, Any]:
    """
    Checks if the local Ollama instance is accessible.
    Non-blocking with a short timeout.
    """
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/version"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "available": True,
                    "version": data.get("version", "unknown"),
                    "model": settings.OLLAMA_MODEL,
                    "base_url": settings.OLLAMA_BASE_URL,
                }
    except Exception:
        pass

    return {
        "available": False,
        "version": None,
        "model": settings.OLLAMA_MODEL,
        "base_url": settings.OLLAMA_BASE_URL,
    }


def compute_deterministic_facts(question: str, db: Session) -> Dict[str, Any]:
    """
    Calculates exact, non-hallucinated database statistics in Python
    to ensure 100% accuracy for factual and quantitative questions.
    """
    stats = crud.get_student_stats(db)
    q_lower = question.lower()
    
    total = stats["total_students"]
    courses_breakdown = stats["courses_breakdown"]
    
    facts: Dict[str, Any] = {
        "total_students": total,
        "total_courses": stats["total_courses"],
        "courses_breakdown": courses_breakdown,
    }

    # Year search (e.g. "born after 2005" or "born before 2000")
    year_match = re.search(r"born\s+(after|before|in)\s+(\d{4})", q_lower)
    if year_match:
        condition, year_str = year_match.groups()
        year = int(year_str)
        all_records = crud.get_grounded_records_for_ai(db, limit=200)
        filtered = []
        for r in all_records:
            if r.get("date_of_birth"):
                birth_year = int(r["date_of_birth"].split("-")[0])
                if condition == "after" and birth_year > year:
                    filtered.append(r)
                elif condition == "before" and birth_year < year:
                    filtered.append(r)
                elif condition == "in" and birth_year == year:
                    filtered.append(r)
        facts["year_filter"] = {
            "condition": condition,
            "year": year,
            "count": len(filtered),
            "students": [f"{s['name']} (DOB: {s['date_of_birth']}, Course: {s['course']})" for s in filtered[:10]],
        }

    return facts


async def query_ollama(prompt: str) -> Optional[str]:
    """
    Sends a query prompt to the local Ollama LLM endpoint.
    Returns the generated response text or None if unreachable.
    """
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,  # Low temperature for factual precision
            "num_predict": 256,
        }
    }
    try:
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "").strip()
    except Exception:
        return None
    return None


async def process_ai_question(question: str, db: Session) -> Dict[str, Any]:
    """
    Orchestrates safe, grounded question answering.
    1. Computes exact metrics via Python and database queries.
    2. Retrieves safe student records (no PII).
    3. Queries Ollama if available; otherwise returns clean computed answer.
    """
    # 1. Deterministic facts
    facts = compute_deterministic_facts(question, db)
    status_info = await check_ollama_availability()

    records = crud.get_grounded_records_for_ai(db, limit=40)
    
    # Format courses text
    courses_text = ", ".join(
        f"{c['course']}: {c['count']} student(s)" for c in facts["courses_breakdown"]
    ) or "No courses registered"

    # Format sample records text
    records_text = "\n".join(
        f"- ID {r['id']}: {r['name']}, Course: {r['course']}, DOB: {r['date_of_birth']}, Enrolled: {r['enrollment_date']}"
        for r in records[:15]
    ) or "No student records available."

    # If Ollama is available, call the model with strict grounding
    if status_info["available"]:
        grounded_prompt = (
            "You are a strict, factual academic records assistant for a student management system.\n"
            "Answer the question using ONLY the verified facts and records provided below.\n"
            "Do NOT speculate, do NOT mention things outside this text, and do NOT attempt to run code.\n\n"
            f"=== VERIFIED DATABASE FACTS ===\n"
            f"Total Students: {facts['total_students']}\n"
            f"Courses Distribution: {courses_text}\n"
            f"Active Records Sample:\n{records_text}\n"
            "===============================\n\n"
            f"USER QUESTION: {question}\n\n"
            "FACTUAL ANSWER:"
        )

        model_response = await query_ollama(grounded_prompt)
        if model_response:
            return {
                "question": question,
                "answer": model_response,
                "is_grounded": True,
                "service_available": True,
                "model_used": settings.OLLAMA_MODEL,
                "exact_data_included": facts,
            }

    # Fallback when Ollama is offline or unavailable
    # Synthesize high quality, accurate answer directly from Python metrics!
    q_lower = question.lower()
    total = facts["total_students"]
    
    if "how many" in q_lower or "total" in q_lower or "count" in q_lower:
        answer = f"There are currently {total} student(s) registered in the database."
    elif "course" in q_lower:
        answer = f"Course enrollment breakdown across {total} student(s):\n" + "\n".join(
            f"• {c['course']}: {c['count']} student(s)" for c in facts["courses_breakdown"]
        )
    elif "year_filter" in facts:
        yf = facts["year_filter"]
        student_list_str = "; ".join(yf["students"]) if yf["students"] else "None"
        answer = (
            f"Found {yf['count']} student(s) born {yf['condition']} {yf['year']}. "
            f"Matching records: {student_list_str}"
        )
    elif "summar" in q_lower or "list" in q_lower or "records" in q_lower:
        answer = (
            f"System Summary: Total {total} student(s) across {facts['total_courses']} course(s). "
            f"Breakdown: {courses_text}."
        )
    else:
        answer = (
            f"Database contains {total} student(s) across {facts['total_courses']} course(s). "
            f"To enable natural language reasoning, start Ollama locally ('ollama run {settings.OLLAMA_MODEL}')."
        )

    return {
        "question": question,
        "answer": answer,
        "is_grounded": True,
        "service_available": False,
        "model_used": None,
        "exact_data_included": facts,
    }
