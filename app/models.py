from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ─────────────────────────────────────────────
# Question models
# ─────────────────────────────────────────────

class QuestionInDB(BaseModel):
    """Represents a question as stored in MongoDB."""
    id: str = Field(alias="_id")
    question_text: str
    options: List[str]
    correct_answer: str
    difficulty: float          # 0.1 – 1.0
    topic: str
    tags: List[str]

    model_config = {"populate_by_name": True}


class QuestionOut(BaseModel):
    """Public-facing question payload (answer hidden)."""
    question_id: str
    question_text: str
    options: List[str]
    difficulty: float
    topic: str
    tags: List[str]


# ─────────────────────────────────────────────
# Session models
# ─────────────────────────────────────────────

class QuestionHistoryItem(BaseModel):
    question_id: str
    difficulty: float
    correct: bool
    topic: str


class UserSession(BaseModel):
    session_id: str
    current_ability: float = 0.5
    questions_answered: int = 0
    question_history: List[QuestionHistoryItem] = []
    topics_missed: List[str] = []
    difficulty_progression: List[float] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────

class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class StartSessionResponse(BaseModel):
    session_id: str
    first_question: Optional[QuestionOut]


class SubmitAnswerResponse(BaseModel):
    correct: bool
    ability_score: float
    next_question: Optional[QuestionOut]
    message: str = ""


class StudyPlanResponse(BaseModel):
    study_plan: str
