"""
Analytics Routes (Bonus Feature):
  GET /session-analytics/{session_id}   — Detailed session analytics
  GET /difficulty-distribution          — Question difficulty histogram
"""

from fastapi import APIRouter, HTTPException
from app.database import get_sessions_collection
from app.adaptive_engine import get_difficulty_distribution

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/session/{session_id}")
def session_analytics(session_id: str):
    """
    Return rich analytics for a completed (or in-progress) session.

    Includes:
      - accuracy breakdown per topic
      - difficulty progression list
      - ability trajectory
      - IRT model metadata
    """
    sessions_col = get_sessions_collection()
    session = sessions_col.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    history = session.get("question_history", [])
    total = len(history)
    correct_count = sum(1 for h in history if h.get("correct"))

    # Per-topic breakdown
    topic_stats: dict = {}
    for h in history:
        t = h.get("topic", "Unknown")
        if t not in topic_stats:
            topic_stats[t] = {"correct": 0, "total": 0}
        topic_stats[t]["total"] += 1
        if h.get("correct"):
            topic_stats[t]["correct"] += 1

    for t in topic_stats:
        s = topic_stats[t]
        s["accuracy_pct"] = round((s["correct"] / s["total"]) * 100) if s["total"] else 0

    # Ability trajectory (progression of ability after each answer)
    ability_trajectory = session.get("difficulty_progression", [])

    # Difficulty of served questions
    difficulty_of_questions = [h.get("difficulty", 0.0) for h in history]

    return {
        "session_id": session_id,
        "summary": {
            "questions_answered": total,
            "correct": correct_count,
            "incorrect": total - correct_count,
            "accuracy_pct": round((correct_count / total) * 100) if total else 0,
            "final_ability": session.get("current_ability", 0.5),
            "topics_missed": session.get("topics_missed", []),
        },
        "topic_breakdown": topic_stats,
        "ability_trajectory": ability_trajectory,
        "difficulty_of_questions_served": difficulty_of_questions,
        "irt_model": {
            "type": "1-PL Logistic IRT",
            "scaling_constant_D": 1.7,
            "learning_rate_alpha": 0.3,
            "ability_range": [0.1, 1.0],
        },
    }


@router.get("/difficulty-distribution")
def difficulty_distribution():
    """
    Return a histogram of question counts bucketed by difficulty range.
    Useful for understanding the shape of the question bank.
    """
    dist = get_difficulty_distribution()
    total = sum(dist.values())
    return {
        "distribution": dist,
        "total_questions": total,
        "buckets": {
            "easy (0.1-0.3)": "Foundational — suitable for ability < 0.4",
            "medium (0.4-0.6)": "Intermediate — targets the average test-taker",
            "hard (0.7-1.0)": "Advanced — challenges high-ability students",
        },
    }
