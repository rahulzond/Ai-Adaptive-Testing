"""
Session Routes:
  POST /start-session        — Create a new test session
  POST /generate-study-plan/{session_id} — Generate AI study plan after test
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.database import get_sessions_collection
from app.adaptive_engine import select_next_question, compute_topics_missed
from app.ai_service import generate_study_plan
from app.models import StartSessionResponse, StudyPlanResponse

router = APIRouter()


@router.post("/start-session", response_model=StartSessionResponse)
def start_session():
    """Create a new adaptive test session and return the first question."""
    session_id = str(uuid.uuid4())
    sessions_col = get_sessions_collection()

    # Select first question at ability = 0.5
    first_question = select_next_question(current_ability=0.5, answered_ids=[])
    if not first_question:
        raise HTTPException(status_code=500, detail="No questions available in the database.")

    session_doc = {
        "_id": session_id,
        "current_ability": 0.5,
        "questions_answered": 0,
        "question_history": [],
        "topics_missed": [],
        "difficulty_progression": [0.5],
        "created_at": datetime.utcnow(),
    }
    sessions_col.insert_one(session_doc)

    return StartSessionResponse(session_id=session_id, first_question=first_question)


@router.post("/generate-study-plan/{session_id}", response_model=StudyPlanResponse)
def generate_plan(session_id: str):
    """Generate a personalized AI study plan for a completed session."""
    sessions_col = get_sessions_collection()
    session = sessions_col.find_one({"_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    history = session.get("question_history", [])
    correct_count = sum(1 for h in history if h.get("correct"))
    total = len(history)

    if total == 0:
        raise HTTPException(status_code=400, detail="No questions have been answered yet.")

    try:
        plan = generate_study_plan(
            final_ability=session["current_ability"],
            topics_missed=session.get("topics_missed", []),
            correct_count=correct_count,
            total_questions=total,
            question_history=history,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return StudyPlanResponse(study_plan=plan)
