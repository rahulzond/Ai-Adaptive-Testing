"""
Question Routes:
  GET  /next-question/{session_id}  — Fetch the next question for a session
  POST /submit-answer               — Submit an answer and get the next question
"""

from fastapi import APIRouter, HTTPException

from app.database import get_sessions_collection
from app.adaptive_engine import (
    check_answer,
    update_ability,
    select_next_question,
    compute_topics_missed,
    MAX_QUESTIONS,
)
from app.models import QuestionOut, SubmitAnswerRequest, SubmitAnswerResponse

router = APIRouter()


def _get_session_or_404(session_id: str) -> dict:
    sessions_col = get_sessions_collection()
    session = sessions_col.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session


@router.get("/next-question/{session_id}", response_model=QuestionOut)
def get_next_question(session_id: str):
    """Return the next question for the given session without submitting an answer."""
    session = _get_session_or_404(session_id)

    if session["questions_answered"] >= MAX_QUESTIONS:
        raise HTTPException(status_code=400, detail="Test complete. Use /generate-study-plan.")

    answered_ids = [h["question_id"] for h in session.get("question_history", [])]
    last_topic = (
        session["question_history"][-1]["topic"]
        if session.get("question_history")
        else None
    )

    question = select_next_question(
        current_ability=session["current_ability"],
        answered_ids=answered_ids,
        last_topic=last_topic,
    )

    if not question:
        raise HTTPException(status_code=404, detail="No more questions available.")

    return question


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest):
    """
    Process the student's answer:
      1. Validate the answer
      2. Update ability score
      3. Persist history
      4. Return next question (or None if test is complete)
    """
    sessions_col = get_sessions_collection()
    session = _get_session_or_404(payload.session_id)

    if session["questions_answered"] >= MAX_QUESTIONS:
        raise HTTPException(status_code=400, detail="Test already complete.")

    # 1. Check correctness
    try:
        correct = check_answer(payload.question_id, payload.answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # 2. Fetch question doc for difficulty + topic
    from app.database import get_questions_collection
    q_doc = get_questions_collection().find_one({"_id": payload.question_id})
    topic = q_doc["topic"] if q_doc else "Unknown"
    difficulty = q_doc["difficulty"] if q_doc else 0.5

    # 3. Update ability using logistic IRT (passes actual question difficulty)
    new_ability = update_ability(session["current_ability"], correct, difficulty=difficulty)

    # 4. Build history entry
    history_entry = {
        "question_id": payload.question_id,
        "difficulty": difficulty,
        "correct": correct,
        "topic": topic,
    }

    new_history = session.get("question_history", []) + [history_entry]
    new_answered = session["questions_answered"] + 1
    new_progression = session.get("difficulty_progression", []) + [new_ability]
    topics_missed = list({h["topic"] for h in new_history if not h["correct"]})


    # 5. Persist updates
    sessions_col.update_one(
        {"_id": payload.session_id},
        {
            "$set": {
                "current_ability": new_ability,
                "questions_answered": new_answered,
                "question_history": new_history,
                "topics_missed": topics_missed,
                "difficulty_progression": new_progression,
            }
        },
    )

    # 6. Select next question (if test not yet complete)
    next_question = None
    message = ""
    if new_answered < MAX_QUESTIONS:
        answered_ids = [h["question_id"] for h in new_history]
        next_question = select_next_question(
            current_ability=new_ability,
            answered_ids=answered_ids,
            last_topic=topic,
        )
    else:
        message = "Test complete! Use POST /generate-study-plan/{session_id} to get your study plan."

    return SubmitAnswerResponse(
        correct=correct,
        ability_score=new_ability,
        next_question=next_question,
        message=message,
    )
