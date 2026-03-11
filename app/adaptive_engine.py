"""
Adaptive Engine — Item Response Theory (IRT) with Logistic Model

Ability update:
  Uses a 2-parameter logistic IRT probability function to calculate the
  expected probability of a correct answer, then updates ability based on
  the surprise (actual - expected).

  P(correct | ability, difficulty) = 1 / (1 + exp(-D * (ability - difficulty)))
  where D = 1.7 (standard IRT scaling constant)

  Update rule (gradient-step on log-likelihood):
    ability += α * (actual - P_expected)
  where α = 0.3 (learning rate), clamped to [0.1, 1.0].

  This gives finer-grained updates near the true ability level and larger
  corrections when performance departs from expectations — matching real
  CAT systems (GRE, GMAT, TOEFL).

Question selection:
  - Pick the unused question whose difficulty is closest to current ability.
  - Break ties by preferring the same topic as the last question answered.
"""

import math
from typing import List, Optional
from app.database import get_questions_collection
from app.models import QuestionOut


MAX_QUESTIONS = 10
ABILITY_MIN = 0.1
ABILITY_MAX = 1.0

# IRT constants
IRT_D = 1.7       # Standard IRT scaling constant
IRT_ALPHA = 0.3   # Learning rate (step size per answer)


# ─────────────────────────────────────────────
# IRT probability
# ─────────────────────────────────────────────

def irt_probability(ability: float, difficulty: float) -> float:
    """
    Compute P(correct) using the 1-PL logistic IRT model.
    P = 1 / (1 + exp(-D * (ability - difficulty)))
    """
    return 1.0 / (1.0 + math.exp(-IRT_D * (ability - difficulty)))


# ─────────────────────────────────────────────
# Ability update  (logistic IRT)
# ─────────────────────────────────────────────

def update_ability(current_ability: float, correct: bool, difficulty: float = 0.5) -> float:
    """
    Update the ability estimate using a logistic IRT gradient step.

    Args:
        current_ability: Current theta estimate (0.1–1.0)
        correct:         Whether the student answered correctly
        difficulty:      The difficulty of the question just answered

    Returns:
        New ability estimate clamped to [ABILITY_MIN, ABILITY_MAX]
    """
    p_expected = irt_probability(current_ability, difficulty)
    actual = 1.0 if correct else 0.0
    delta = IRT_ALPHA * (actual - p_expected)
    new_ability = current_ability + delta
    return round(max(ABILITY_MIN, min(ABILITY_MAX, new_ability)), 2)


# ─────────────────────────────────────────────
# Question selection
# ─────────────────────────────────────────────

def select_next_question(
    current_ability: float,
    answered_ids: List[str],
    last_topic: Optional[str] = None,
) -> Optional[QuestionOut]:
    """
    Select the best next question from the question bank.

    Strategy:
      1. Exclude already-answered questions.
      2. Sort remaining questions by |difficulty - ability|.
      3. Among ties, prefer the question matching `last_topic`.
    """
    questions_col = get_questions_collection()
    all_questions = list(questions_col.find({"_id": {"$nin": answered_ids}}))

    if not all_questions:
        return None

    def sort_key(q):
        diff_gap = abs(q["difficulty"] - current_ability)
        topic_bonus = 0.0 if (last_topic and q["topic"] == last_topic) else 0.001
        return diff_gap + topic_bonus

    best = min(all_questions, key=sort_key)

    return QuestionOut(
        question_id=best["_id"],
        question_text=best["question_text"],
        options=best["options"],
        difficulty=best["difficulty"],
        topic=best["topic"],
        tags=best["tags"],
    )


# ─────────────────────────────────────────────
# Answer checking
# ─────────────────────────────────────────────

def check_answer(question_id: str, submitted_answer: str) -> bool:
    """Return True if the submitted answer matches the stored correct answer."""
    questions_col = get_questions_collection()
    question = questions_col.find_one({"_id": question_id})
    if not question:
        raise ValueError(f"Question '{question_id}' not found.")
    return submitted_answer.strip().lower() == question["correct_answer"].strip().lower()


# ─────────────────────────────────────────────
# Topics missed
# ─────────────────────────────────────────────

def compute_topics_missed(history: list) -> List[str]:
    """Return a deduplicated list of topics where the student answered incorrectly."""
    missed = {h["topic"] for h in history if not h.get("correct", True)}
    return list(missed)


# ─────────────────────────────────────────────
# Difficulty distribution (bonus: analytics)
# ─────────────────────────────────────────────

def get_difficulty_distribution() -> dict:
    """
    Return a histogram of question counts bucketed by difficulty range.
    Buckets: 0.1–0.3 (easy), 0.4–0.6 (medium), 0.7–1.0 (hard).
    """
    questions_col = get_questions_collection()
    all_q = list(questions_col.find({}))
    dist = {"easy (0.1-0.3)": 0, "medium (0.4-0.6)": 0, "hard (0.7-1.0)": 0}
    for q in all_q:
        d = q.get("difficulty", 0.5)
        if d <= 0.3:
            dist["easy (0.1-0.3)"] += 1
        elif d <= 0.6:
            dist["medium (0.4-0.6)"] += 1
        else:
            dist["hard (0.7-1.0)"] += 1
    return dist
